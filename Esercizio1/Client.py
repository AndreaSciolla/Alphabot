#client
import socket

SERVER_ADDRESS = ("192.168.1.127", 8000)
BUFFER_SIZE = 4096

def main():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(SERVER_ADDRESS)
    while True:
        string = input("-> inserisci istruzione(f:avanti, b:indietro, l:sinistra, r:destra, help:istruzioni, exit:esci): ")
        tempo = input("-> inserisci tempo in millisecondi: ")
        packet = f"{string}|{tempo}"
        s.sendall(packet.encode())
        stato, phrase = s.recv(BUFFER_SIZE).decode().split("|")
        print(f"stato: {stato}; risposta: {phrase}")
        
        
if __name__ == "__main__":
    main()