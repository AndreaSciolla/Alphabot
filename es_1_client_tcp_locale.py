#client
import socket

SERVER_ADDRESS = ("127.0.0.1", 8000)
BUFFER_SIZE = 4096
    
def main():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(SERVER_ADDRESS)
    while True:
        string = input("-> inserisci istruzione(f:avanti, b:indietro, l:sinistra, r:destra, help:istruzioni, exit:esci): ")
        tempo = input("-> inserisci tempo in millisecondi: ")
        packet = f"{string}|{tempo}"
        s.sendall(packet.encode())  
        msg =  s.recv(BUFFER_SIZE).decode()
        phrase = msg.split("|")[1] 
        stato = msg.split("|")[0] 
        print(f"stato: {stato}; risposta: {phrase}")
        

if __name__ == "__main__":
    main()