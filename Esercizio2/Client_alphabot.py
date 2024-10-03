#client
import socket

SERVER_ADDRESS = ("192.168.1.140", 9000)
BUFFER_SIZE = 4096
    
def main():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(SERVER_ADDRESS)
    while True:
        string = input("-> inserisci istruzione(f:avanti, b:indietro, l:sinistra, r:destra, help:istruzioni, exit:esci): ")
        tempo = input("-> inserisci tempo in secondi: ")
        packet = f"{string}|{tempo}"
        s.sendall(packet.encode())  

        

if __name__ == "__main__":
    main()