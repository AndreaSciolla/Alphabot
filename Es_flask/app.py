from flask import Flask, make_response, render_template, request, redirect, url_for, jsonify
import sqlite3
import hashlib
import jwt
import datetime
import RPi.GPIO as GPIO  # Libreria per controllare i GPIO del Raspberry Pi

app = Flask(__name__)

DB_PATH = "./login.db"

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
    try:
        conn = sqlite3.connect(DB_PATH)
        return conn
    except sqlite3.Error as e:
        print(f"Errore durante la connessione al database: {e}")
        return None

def hash_password(password):
    """Crea un hash SHA256 della password per memorizzarla in modo sicuro."""
    return hashlib.sha256(password.encode('utf-8')).hexdigest()

def generate_token(username):
    """Genera un token JWT contenente lo username e una data di scadenza di 1 giorno"""
    payload = {
        "username": username,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(days=1)
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    
    if isinstance(token, bytes):
        token = token.decode('utf-8')
    return token

def verify_token(token):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        print("Il token è scaduto.")
    except jwt.InvalidTokenError:
        print("Token non valido.")
    return None

def control_alphabot(key, state):
    """
    Controlla il robot in base al tasto ricevuto e al suo stato.
    Se il tasto viene rilasciato (state=False), ferma il robot.
    """
    if not state:
        print("Comando: Stop")
        bot.stop()
        return

    if key == 'w':
        print("Comando: Avanti")
        bot.setMotor(60, 60)
    elif key == 's':
        print("Comando: Indietro")
        bot.setMotor(-60, -60)
    elif key == 'd':
        print("Comando: Destra")
        bot.setMotor(60, 20)
    elif key == 'a':
        print("Comando: Sinistra")
        bot.setMotor(20, 60)
    else:
        print("Comando: Stop")
        bot.stop()

@app.route('/login', methods=['GET', 'POST'])
def login():
    """
    Gestisce la pagina di login.
    In caso di POST, verifica le credenziali e genera un token JWT.
    Viene impostato solo il cookie del token, poiché contiene già lo username.
    """
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

        conn = get_db_connection()
        if conn:
            cur = conn.cursor()
            cur.execute(query_login, (username, password_hash))
            user = cur.fetchone()
            conn.close()

        if user:
            token = generate_token(username)
            response = make_response(redirect(url_for('index')))
            response.set_cookie('token', token, max_age=60 * 60 * 24)
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

        conn = get_db_connection()
        if conn:
            cur = conn.cursor()
            try:
                cur.execute(query_insert, (username, password_hash))
                conn.commit()
                conn.close()
                return redirect(url_for('login'))
            except sqlite3.IntegrityError:
                conn.close()
                return render_template('create_account.html', alert="Username già esistente!")
    return render_template('create_account.html')

@app.route('/logout', methods=['POST'])
def logout():
    """Gestisce il logout cancellando il cookie del token"""
    response = make_response(redirect(url_for('login')))
    response.delete_cookie('token')
    return response

@app.route('/')
def index():
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
    Passa il tasto e lo stato a control_alphabot per controllare il robot.
    """
    data = request.json
    key = data.get('key')
    state = data.get('state')  # True = premuto, False = rilasciato

    control_alphabot(key, state)
    return jsonify({"success": True}), 200

@app.route("/token_info", methods=['GET'])
def token_info():
    """Mostra le informazioni del token"""
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
    robot = "0.0.0.0"
    print(f"Server avviato su http://{robot}:5000")
    app.run(debug=True, host=robot)
