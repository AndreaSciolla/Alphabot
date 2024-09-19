import socket as sck


isRunning = True


address = ("0.0.0.0", 8000)

s_server = sck.socket(sck.AF_INET, sck.SOCK_STREAM)
s_server.bind(address)

phrase = ""
status = ""

comandi = {"f": "vado avanti", "b": "vado indietro", "l": "giro a sinistra", "r": "giro a destra"}

    
def main():

    global isRunning

    s_server.listen()

    conn, addr = s_server.accept()

    while isRunning:
        text = conn.recv(4096)
        
        if text.decode().split("|")[0] == "help":
            status = "ok"
            phrase = "richiesta d'aiuto"
            conn.sendall(f"{status}|{phrase}".encode())
          

        elif text.decode() == "exit":
            status = "ok"
            phrase = "uscita"
            conn.sendall(f"{status}|{phrase}".encode())
            isRunning = False
            

        elif text.decode().count("|") > 1 or text.decode().count("|") == 0:
            status = "errore"
            phrase = "errore nel messaggio inviato dal client( manca | o ce ne sono troppe)"
            conn.sendall(f"{status}|{phrase}".encode())
            

        elif text.decode().split("|")[0].lower() not in comandi:
            status = "errore"
            phrase = "comando non presente"
            conn.sendall(f"{status}|{phrase}".encode())
            

        elif float(text.decode().split("|")[1]) < 0:
            status = "errore"
            phrase = "valore per il tempo negativo"
            conn.sendall(f"{status}|{phrase}".encode())
           
        else :
            status = "ok" 
            phrase = "il robot inizia a muoversi: " + str(comandi[text.decode().split("|")[0].lower()]) + "per " + str( (float(text.decode().split("|")[1]))) + " ms"
            conn.sendall(f"{status}|{phrase}".encode())

    s_server.close()

if __name__=="__main__":
    main()