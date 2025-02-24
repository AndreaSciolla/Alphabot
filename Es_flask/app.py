from flask import Flask, make_response, render_template, request, redirect, url_for, jsonify
import sqlite3
import hashlib
import jwt
import datetime
from functools import wraps
import RPi.GPIO as GPIO  # Libreria per controllare i GPIO del Raspberry Pi

app = Flask(__name__)

DB_PATH = "./login.db"

# Dizionario per tenere traccia dello stato dei tasti (premuto/rilasciato)
key_state = {
    'w': False,  # Avanti
    'a': False,  # Sinistra
    's': False,  # Indietro
    'd': False   # Destra
}

SECRET_KEY = "secret_key"
ALGORITHM = "HS256"


class AlphaBot(object):
    def __init__(self, in1=12, in2=13, ena=6, in3=20, in4=21, enb=26):
        self.IN1 = in1
        self.IN2 = in2
        self.IN3 = in3
        self.IN4 = in4
        self.ENA = ena
        self.ENB = enb

        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        # Imposta i pin come output per il controllo dei motori
        GPIO.setup(self.IN1, GPIO.OUT)
        GPIO.setup(self.IN2, GPIO.OUT)
        GPIO.setup(self.IN3, GPIO.OUT)
        GPIO.setup(self.IN4, GPIO.OUT)
        GPIO.setup(self.ENA, GPIO.OUT)
        GPIO.setup(self.ENB, GPIO.OUT)

        # Configura il PWM per il controllo della velocità dei motori
        self.PWMA = GPIO.PWM(self.ENA, 500)
        self.PWMB = GPIO.PWM(self.ENB, 500)
        self.PWMA.start(0)
        self.PWMB.start(0)

    def setMotor(self, left, right):
        # Controllo del motore destro
        if right >= 0:
            GPIO.output(self.IN3, GPIO.LOW)
            GPIO.output(self.IN4, GPIO.HIGH)
            self.PWMB.ChangeDutyCycle(right)
        elif right < 0:
            GPIO.output(self.IN3, GPIO.HIGH)
            GPIO.output(self.IN4, GPIO.LOW)
            self.PWMB.ChangeDutyCycle(abs(right))

        # Controllo del motore sinistro
        if left >= 0:
            GPIO.output(self.IN1, GPIO.HIGH)
            GPIO.output(self.IN2, GPIO.LOW)
            self.PWMA.ChangeDutyCycle(left)
        elif left < 0:
            GPIO.output(self.IN1, GPIO.LOW)
            GPIO.output(self.IN2, GPIO.HIGH)
            self.PWMA.ChangeDutyCycle(abs(left))

    def stop(self):
        self.setMotor(0, 0)


# Istanza globale del robot
bot = AlphaBot()


def get_db_connection():
    """
    Crea e restituisce una connessione al database SQLite.
    Utilizza row_factory per poter accedere alle righe come dizionari.
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row  # Abilita l'accesso alle righe come dizionario
        return conn
    except sqlite3.Error as e:
        print(f"Errore durante la connessione al database: {e}")
        return None


def hash_password(password):
    #Crea un hash SHA256 della password per memorizzarla in modo sicuro.
    return hashlib.sha256(password.encode('utf-8')).hexdigest()


def generate_token(username):
    #Genera un token JWT contenente lo username e una data di scadenza di 1 giorno.
    payload = {
        "username": username,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(days=1)
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    
    if isinstance(token, bytes):
        token = token.decode('utf-8')
    return token


def verify_token(token):
    #Verifica la validità del token JWT.
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        print("Il token è scaduto.")
    except jwt.InvalidTokenError:
        print("Token non valido.")
    return None


def control_alphabot():
    """
    Valuta lo stato dei tasti e invia il comando appropriato al robot.
    Utilizza il metodo setMotor per controllare i motori.
    """
    # Combinazioni di due tasti
    if key_state['w'] and key_state['d']:
        print("Comando: Avanti-Destra")
        bot.setMotor(60, 40)
    elif key_state['w'] and key_state['a']:
        print("Comando: Avanti-Sinistra")
        bot.setMotor(40, 60)
    elif key_state['s'] and key_state['d']:
        print("Comando: Indietro-Destra")
        bot.setMotor(-60, -40)
    elif key_state['s'] and key_state['a']:
        print("Comando: Indietro-Sinistra")
        bot.setMotor(-40, -60)
        
    # Comandi singoli
    elif key_state['w']:
        print("Comando: Avanti")
        bot.setMotor(60, 60)
    elif key_state['s']:
        print("Comando: Indietro")
        bot.setMotor(-60, -60)
    elif key_state['d']:
        print("Comando: Destra")
        bot.setMotor(60, 20)
    elif key_state['a']:
        print("Comando: Sinistra")
        bot.setMotor(20, 60)
    else:
        print("Comando: Stop")
        bot.stop()


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('e-mail')
        password = request.form.get('password')

        if not username or not password:
            return render_template('login.html', alert="Inserisci username e password!")

        password_hash = hash_password(password)

        query_login = """ 
            SELECT * 
            FROM credenziali 
            WHERE username = ? AND password = ?
        """

        with get_db_connection() as conn:
            if conn:
                cur = conn.cursor()
                cur.execute(query_login, (username, password_hash))
                user = cur.fetchone()

        if user:
            # Genera il token JWT al momento del login
            token = generate_token(username)
            response = make_response(redirect(url_for('index')))
            # Imposta il cookie del token (contiene anche lo username)
            response.set_cookie('token', token, max_age=60 * 60 * 24)  # 1 giorno
            print(f"Token generato: {token}")
            return response
        else:
            return render_template('login.html', alert="Credenziali non valide!")
    return render_template('login.html')


@app.route('/create_account', methods=['GET', 'POST'])
def create_account():
    if request.method == 'POST':
        username = request.form.get('e-mail')
        password = request.form.get('password')

        if not username or not password:
            return render_template('create_account.html', alert="Inserisci tutti i dati richiesti!")

        password_hash = hash_password(password)

        query_insert = """
            INSERT INTO credenziali (username, password)
            VALUES (?, ?)
        """

        with get_db_connection() as conn:
            if conn:
                cur = conn.cursor()
                try:
                    cur.execute(query_insert, (username, password_hash))
                    conn.commit()
                    return redirect(url_for('login'))
                except sqlite3.IntegrityError:
                    return render_template('create_account.html', alert="Username già esistente!")
    return render_template('create_account.html')


@app.route('/logout', methods=['POST'])
def logout():
    response = make_response(redirect(url_for('login')))
    response.delete_cookie('token')
    return response


@app.route('/')
def index():
    """
    Pagina principale.
    Recupera il token dal cookie, lo verifica e utilizza lo username contenuto nel payload.
    Se il token non è valido o assente, reindirizza al login.
    """
    token = request.cookies.get('token')
    if token:
        payload = verify_token(token)
        if payload:
            username = payload.get("username")
            return render_template('index.html', username=username)
    return redirect(url_for('login'))


@app.route("/key_event", methods=['POST'])
def key_event():
    """
    Riceve gli eventi dei tasti (premuto/rilasciato) dal client.
    Aggiorna il dizionario key_state e richiama control_alphabot() per controllare il robot.
    """
    data = request.json
    key = data.get('key')
    state = data.get('state')  # True = premuto, False = rilasciato

    if key in key_state:
        key_state[key] = state
        if state:
            print(f"Tasto premuto: {key}")
        else:
            print(f"Tasto rilasciato: {key}")
        # Dopo l'aggiornamento dello stato, controlla il robot
        control_alphabot()
        return jsonify({"success": True}), 200
    return jsonify({"success": False}), 400


@app.route("/token_info", methods=['GET'])
def token_info():
    #Mostra le informazioni del token.
    token = request.cookies.get('token')
    if not token:
        return jsonify({"message": "Token non trovato!"}), 400

    payload = verify_token(token)
    print("Token:", token)
    print("Payload:", payload)

    return jsonify({
        "token": token,
        "payload": payload
    }), 200


if __name__ == "__main__":
    robot = "192.168.1.140"
    app.run(debug=True, host=robot)
