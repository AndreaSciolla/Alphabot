import socket

def main():
    server_host="127.0.0.1"
    server_port=12345
    # Creazione del socket UDP
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    server_address = (server_host, server_port)
    print(f"Connesso al server UDP {server_host}:{server_port}")
    
    try:
        # Ciclo di invio e ricezione dei messaggi
        while True:
            message = input("Inserisci un messaggio da inviare (o 'exit' per uscire): ")
            
            if message.lower() == 'exit':
                print("Chiusura della connessione...")
                break

            # Invia il messaggio al server
            sock.sendto(message.encode(), server_address)
            
            # Attende la risposta dal server (eco)
            data, _ = sock.recvfrom(4096)
            print(f"Ricevuto eco dal server: {data.decode()}")
    
    finally:
        sock.close()

if __name__ == "__main__":
    main()
