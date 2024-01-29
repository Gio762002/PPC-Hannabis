import socket
from multiprocessing import Process


class client:

    def connect_to_game(self):
        HOST = "localhost"
        PORT = 8848
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect((HOST, PORT))
        # self.client_socket.settimeout(1)
        print("connected to game host")
        self.receive_basic_infos()

    def receive_basic_infos(self):
        print("start receiving basic infos")
        data = self.client_socket.recv(1024)
        print(data.decode)

    def send(self):
        m = input("message> ")
        while len(m):
            if m == "pause" or m == "run":
                self.client_socket.sendall(m.encode())
            else:
                print("nothing")
            print("sent")
            m = input("message> ")


if __name__ == "__main__":
    c = client()
    c.connect_to_game()
    c.send()
