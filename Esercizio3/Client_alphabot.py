import socket
from pynput import keyboard

SERVER_ADDRESS = ("192.168.1.140", 9090)
BUFFER_SIZE = 4096

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(SERVER_ADDRESS)

def on_press(key):

    if key.char == "w":
        print("press w")
    elif key.char == "s":
        print("press s")
    elif key.char == "a":
        print("press a")
    elif key.char == "d":
        print("press d")
    
    s.sendall(key.char.lower().encode())

def on_release(key):

    if key.char == "w":
        print("release w")
    elif key.char == "s":
        print("release s")
    elif key.char == "a":
        print("release a")
    elif key.char == "d":
        print("release d")
    
    s.sendall(key.char.upper().encode())
    

def start_listener():
    with keyboard.Listener(on_press = on_press, on_release = on_release) as listener:
        listener.join()
    
def main():
    start_listener()
    while True:
        pass

    s.close()

if __name__ == "__main__":
    main()