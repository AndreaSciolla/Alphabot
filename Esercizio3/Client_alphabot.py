import socket
from pynput import keyboard
from threading import Thread
import time

comandi = {}


class MyThread(Thread):
    def __init__(self, socket):
        super().__init__()
        self.socket = socket
        self.running = True

    def send_command(self, comandi):
        packet = str(comandi)
        self.socket.sendall(packet.encode())

    def stop(self):
        self.running = False


SERVER_ADDRESS = ("192.168.1.140", 3450)
BUFFER_SIZE = 4096

def on_press(key, t1):
    if key.char == "w":
        comandi["F"] = "press"
    elif key.char == "a":
        comandi["L"] = "press"
    elif key.char == "s":
        comandi["B"] = "press"
    elif key.char == "d":
        comandi["R"] = "press"
    t1.send_command(comandi)  

def on_release(key, t1):
    if key.char == "w":
        comandi["F"] = "release"
    elif key.char == "a":
        comandi["L"] = "release"
    elif key.char == "s":
        comandi["B"] = "release"
    elif key.char == "d":
        comandi["R"] = "release"
    t1.send_command(comandi)  


def start_listener(t1):
    with keyboard.Listener(on_press=lambda key: on_press(key, t1), on_release=lambda key: on_release(key, t1)) as listener:
        listener.join()


def main():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(SERVER_ADDRESS)
    t1 = MyThread(s)
    t1.start()
    start_listener(t1)


if __name__ == "__main__":
    main()
