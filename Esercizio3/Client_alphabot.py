import socket
import time
from pynput import keyboard

SERVER_ADDRESS = ("192.168.1.140", 9090)
#HEARTBEAT_ADDRESS = ("192.168.1.140", 9000)
BUFFER_SIZE = 4096

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(SERVER_ADDRESS)
#heartbeat = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#heartbeat.connect(HEARTBEAT_ADDRESS)
comandi = ["w", "a", "s", "d"]
ultimo_comando = None

def on_press(key):
    
    global ultimo_comando

    if key.char in comandi:
        print(f"press {key.char}")

    if key.char != ultimo_comando and key.char in comandi:
        s.sendall(key.char.lower().encode())
        ultimo_comando = key.char
        time.sleep(0.05)


def on_release(key):
    
    global ultimo_comando

    if key.char in comandi:
        print(f"release {key.char}")

    if key.char in comandi:
        ultimo_comando = None
        s.sendall(key.char.upper().encode())
        time.sleep(0.05)


def start_listener():
    with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
        listener.join()


def main():
    start_listener()

    if KeyError:
        s.close()
        #heartbeat.close()


if __name__ == "__main__":
    main()
