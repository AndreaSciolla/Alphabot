# Data: 10-17-24-28 Ottobre 2024
# Autori: Prandi Alessandro - Sciolla Andrea
# Descrizione: 
# Questo  è un client TCP che si connette a un Alphabot su una specifica 
# porta e invia comandi (w, a, s, d) corrispondenti ai tasti premuti sulla tastiera.
# Il programma cattura la pressione e il rilascio dei tasti 'w', 'a', 's', 'd' tramite la libreria pynput 
# e invia il comando corrispondente in tempo reale al server (Alphabot). 
# Quando un tasto viene premuto, invia il carattere in minuscolo, e quando viene rilasciato, invia il carattere in maiuscolo (in questo modo si distinguono).
# E' stato anche implementato un meccanismo per evitare di inviare ripetutamente lo stesso comando mentre un tasto è tenuto premuto.

import socket
import time
from pynput import keyboard

# Indirizzo IP e porta dell'Alphabot a cui ci connettiamo
SERVER_ADDRESS = ("192.168.1.140", 9090)
BUFFER_SIZE = 4096

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)   # Creazione del socket TCP per la comunicazione con il server
s.connect(SERVER_ADDRESS)   # Connessione al server

ultimo_comando = None # Variabile globale per tenere traccia dell'ultimo comando inviato

def on_press(key):
    '''questa funzione gestisce la pressione di un tasto''' 

    global ultimo_comando

    if key.char != ultimo_comando:  # Controlla se il tasto corrente è diverso dall'ultimo comando inviato e fa parte dei comandi
        
        s.sendall(key.char.lower().encode())   # Invia il tasto in minuscolo al server per indicare la pressione
        ultimo_comando = key.char   # Aggiorna l'ultimo comando inviato
        
        time.sleep(0.05)     # Pausa per evitare di sovraccaricare la rete con troppi comandi consecutivi

def on_release(key):
    '''questa funzione gestisce il rilascio di un tasto''' 

    global ultimo_comando
        
    ultimo_comando = None   # Resetta l'ultimo comando inviato
    s.sendall(key.char.upper().encode())     # Invia il tasto in maiuscolo al server per indicare il rilascio
    
    time.sleep(0.05)

def start_listener():
    ''' Funzione che avvia il listener della tastiera''' 

    # listener per monitorare la pressione e il rilascio dei tasti
    with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
        listener.join()

def main():

    start_listener()    # Avvia il listener della tastiera
    if KeyError:     # Se si verifica un'eccezione KeyError (non gestito), chiude il socket
        s.close()

if __name__ == "__main__":
    main()