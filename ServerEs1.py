#server UDP con eco
import socket

def main():
    host="127.0.0.1"
    port=12345
    # Creazione del socket UDP
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    # Assegnazione dell'host e della porta
    sock.bind((host, port))
    
    print(f"Server UDP di eco in ascolto su {host}:{port}")

    while True:
        # Ricezione del messaggio dal client
        data, addr = sock.recvfrom(4096)  # Dimensione massima del buffer (1024 byte)
        print(f"Messaggio ricevuto da {addr}: {data.decode()}")

        # Invia il messaggio di eco al client
        sock.sendto(data, addr)
        print(f"Eco inviato a {addr}")

if __name__ == "__main__":
    main()
