# Data: 10-17 Ottobre 2024
# Autori: Prandi Alessandro - Sciolla Andrea
# Descrizione:
# Questo script è un server TCP che viene eseguito su un Raspberry Pi connesso all' robot AlphaBot.
# Il server riceve comandi (come 'w', 'a', 's', 'd') da un client e controlla i movimenti del robot in base ai comandi inviati.
# I comandi minuscoli ('w', 'a', 's', 'd') fanno muovere il robot in avanti, indietro, sinistra e destra,
# i comandi in maiuscolo fermano il movimento. La comunicazione avviene su un socket TCP.

import socket as sck
import threading as thr
import time
import RPi.GPIO as GPIO  # Libreria per controllare i GPIO del Raspberry Pi
import ast
import sqlite3


client_list = []


class AlphaBot(object):  # Classe per controllare il robot AlphaBot

    # Metodo di inizializzazione, configurazione dei pin GPIO e dei motori
    def __init__(self, in1=13, in2=12, ena=6, in3=21, in4=20, enb=26):
        self.IN1 = in1
        self.IN2 = in2
        self.IN3 = in3
        self.IN4 = in4
        self.ENA = ena
        self.ENB = enb
        self.PA = 20  # Velocità di rotazione del motore sinistro
        self.PB = 20  # Velocità di rotazione del motore destro

        # Configurazione dei pin GPIO come output per controllare i motori
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        GPIO.setup(self.IN1, GPIO.OUT)
        GPIO.setup(self.IN2, GPIO.OUT)
        GPIO.setup(self.IN3, GPIO.OUT)
        GPIO.setup(self.IN4, GPIO.OUT)
        GPIO.setup(self.ENA, GPIO.OUT)
        GPIO.setup(self.ENB, GPIO.OUT)
        
        # Configurazione della PWM per i motori
        self.PWMA = GPIO.PWM(self.ENA, 500)
        self.PWMB = GPIO.PWM(self.ENB, 500)
        self.PWMA.start(self.PA)
        self.PWMB.start(self.PB)
        
        self.stop()  # Arresta il robot all'inizio

    def stop(self):  # Metodo per fermare il robot
        self.PWMA.ChangeDutyCycle(0)
        self.PWMB.ChangeDutyCycle(0)
        GPIO.output(self.IN1, GPIO.LOW)
        GPIO.output(self.IN2, GPIO.LOW)
        GPIO.output(self.IN3, GPIO.LOW)
        GPIO.output(self.IN4, GPIO.LOW)

    def forward(self, speed=60):  # Metodo per far avanzare il robot
        self.PWMA.ChangeDutyCycle(speed)
        self.PWMB.ChangeDutyCycle(speed)
        GPIO.output(self.IN1, GPIO.LOW)
        GPIO.output(self.IN2, GPIO.HIGH)
        GPIO.output(self.IN3, GPIO.HIGH)
        GPIO.output(self.IN4, GPIO.LOW)

    def backward(self, speed=60):  # Metodo per far andare indietro il robot
        self.PWMA.ChangeDutyCycle(speed)
        self.PWMB.ChangeDutyCycle(speed)
        GPIO.output(self.IN1, GPIO.HIGH)
        GPIO.output(self.IN2, GPIO.LOW)
        GPIO.output(self.IN3, GPIO.LOW)
        GPIO.output(self.IN4, GPIO.HIGH)

    def left(self, speed=25):  # Metodo per far girare il robot a sinistra
        self.PWMA.ChangeDutyCycle(speed)
        self.PWMB.ChangeDutyCycle(speed)
        GPIO.output(self.IN1, GPIO.HIGH)
        GPIO.output(self.IN2, GPIO.LOW)
        GPIO.output(self.IN3, GPIO.HIGH)
        GPIO.output(self.IN4, GPIO.LOW)

    def right(self, speed=25):  # Metodo per far girare il robot a destra
        self.PWMA.ChangeDutyCycle(speed)
        self.PWMB.ChangeDutyCycle(speed)
        GPIO.output(self.IN1, GPIO.LOW)
        GPIO.output(self.IN2, GPIO.HIGH)
        GPIO.output(self.IN3, GPIO.LOW)
        GPIO.output(self.IN4, GPIO.HIGH)

    # Metodo per modificare la velocità del motore sinistro
    def set_pwm_a(self, value):
        self.PA = value
        self.PWMA.ChangeDutyCycle(self.PA)

    # Metodo per modificare la velocità del motore destro
    def set_pwm_b(self, value):
        self.PB = value
        self.PWMB.ChangeDutyCycle(self.PB)

    # Metodo per controllare entrambi i motori con valori separati per sinistra e destra
    def set_motor(self, left, right):
        if (right >= 0) and (right <= 100):
            GPIO.output(self.IN1, GPIO.HIGH)
            GPIO.output(self.IN2, GPIO.LOW)
            self.PWMA.ChangeDutyCycle(right)
        elif (right < 0) and (right >= -100):
            GPIO.output(self.IN1, GPIO.LOW)
            GPIO.output(self.IN2, GPIO.HIGH)
            self.PWMA.ChangeDutyCycle(0 - right)
        if (left >= 0) and (left <= 100):
            GPIO.output(self.IN3, GPIO.HIGH)
            GPIO.output(self.IN4, GPIO.LOW)
            self.PWMB.ChangeDutyCycle(left)
        elif (left < 0) and (left >= -100):
            GPIO.output(self.IN3, GPIO.LOW)
            GPIO.output(self.IN4, GPIO.HIGH)
            self.PWMB.ChangeDutyCycle(0 - left)


# Indirizzo e porta del server
MY_ADDRESS = ("192.168.1.140", 9090)
BUFFER_SIZE = 4096

comandi = ["w", "a", "s", "d"] # Lista dei comandi validi che possono essere inviati ('w', 'a', 's', 'd') o presi dal database

def calcola_comandi_possibili(cur):
    global comandi

    #POPOLAZIONE DATABASE
    query_select =  '''  SELECT tasto
                        FROM Comandi
                    '''

    print(query_select)
    cur.execute(query_select)

    variabile_in_stampa = cur.fetchall()  #lista di tuple con i valori delle righe per ogni colonna
    lista_c = [x[0] for x in variabile_in_stampa]
    print(lista_c)
    for c in lista_c:
        comandi.append(c)


def muovi_curva(alphaBot, lista_mov, g_curva):
    for movimento in lista_mov:
        if movimento["direzione"] == "F":
            print("avanti")
            alphaBot.forward()
            time.sleep(movimento["distanza"])
            alphaBot.stop()
        elif movimento["direzione"] == "B":
            print("indietro")
            alphaBot.backward()
            time.sleep(movimento["distanza"])
            alphaBot.stop()
        elif movimento["direzione"] == "L":
            print("gira sinistra")
            alphaBot.left()
            time.sleep(movimento["g_curva"])
            alphaBot.forward()
            time.sleep(movimento["distanza"])
            alphaBot.stop()
        elif movimento["direzione"] == "R":
            print("destra")
            alphaBot.right()
            time.sleep(movimento["g_curva"])
            alphaBot.forward()
            time.sleep(movimento["distanza"])
            alphaBot.stop()


def main():
    alphaBot = AlphaBot() 
    alphaBot.stop()  # Il robot viene fermato inizialmente

    # Creazione del socket TCP
    s = sck.socket(sck.AF_INET, sck.SOCK_STREAM)
    s.bind(MY_ADDRESS)  
    s.listen()  
    
    connection, client_address = s.accept()
    print(f"Il client {client_address} si è connesso")

    conn = sqlite3.connect("db_comandi.db") #si connettte a database (se non esiste lo crea)
    cur = conn.cursor()

    calcola_comandi_possibili(cur)
    print(comandi)

    # Loop principale per ricevere e gestire i comandi
    while True:
        message = connection.recv(BUFFER_SIZE)  # Ricezione dei dati dal client
        direz_decode = message.decode()  

        if direz_decode in comandi:

            # Controllo dei comandi e esecuzione dei metodi appropriati
            if direz_decode == "w":
                print("avanti")
                alphaBot.forward()
            elif direz_decode == "s":
                print("indietro")
                alphaBot.backward()
            elif direz_decode == "a":
                print("sinistra")
                alphaBot.left()
            elif direz_decode == "d":
                print("destra")
                alphaBot.right()
            elif direz_decode.isupper():  # Se il comando è maiuscolo, ferma il robot
                print("stop")
                alphaBot.stop()


            elif direz_decode == "q" or direz_decode == "e" or direz_decode == "z" or direz_decode == "c":

                query_select_mov = f' SELECT "str_mov" FROM "Comandi" WHERE "tasto" = "{direz_decode}" '

                print(query_select_mov)
                cur.execute(query_select_mov)
                conn.commit()

                variabile_in_stampa = cur.fetchall()  #serve per mandare in stampa
                stringa_comando = variabile_in_stampa[0][0]
                dati_comando = stringa_comando.split(";")
                nome_mov = dati_comando[0]
                lista_movimenti = []

                for i in range(1, len(dati_comando)):
                    #movimento = {"direzione": dati_comando[i][0], "distanza": dati_comando[i][1:]}
                    movimento = {"direzione": dati_comando[i][0], "distanza": 1}
                    lista_movimenti.append(movimento)

                gradi_curva = 0.5
                #gradi_curva = nome_mov.split("_")[1]
                muovi_curva(alphaBot, lista_movimenti, gradi_curva)

                
    # Chiusura del socket
    s.close()

if __name__ == "__main__":
    main()