#client
import socket
from pynput import keyboard

SERVER_ADDRESS = ("192.168.1.140", 3450)
BUFFER_SIZE = 4096

global funzione
global direzione

def on_press(key):
    global funzione
    global direzione
    if key.char == "w":
        print("avanti")
        direzione = "F"
        funzione = "press"
        
def on_release(key):
    global funzione
    global direzione
    if key.char == "w":
        print("fermo")
        direzione = "F"
        funzione = "release"
        
def startlistener():
    with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
        listener.join()
        
def mandaMessaggio(socket):
    packet = f"{direzione}|{funzione}"
    socket.sendall(packet.encode())
            
def main():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(SERVER_ADDRESS)
    startlistener()
    print("messaggio mandato")
    packet = f"{direzione}|{funzione}"
    s.sendall(packet.encode())  
       

if __name__ == "__main__":
    main()