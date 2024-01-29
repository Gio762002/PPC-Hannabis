import socket
import concurrent.futures
import select
import time
from multiprocessing import Process


class server():

    def __init__(self):
        self.number_of_players = 4
        self.gaming = True
        self.counting = True

    def socket_connection(self):
        HOST = "localhost"
        PORT = 8848
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((HOST, PORT))
        self.server_socket.listen(self.number_of_players)
        # self.server_socket.settimeout(0)
        executor = concurrent.futures.ProcessPoolExecutor()
        while self.gaming:
            readable, _, _ = select.select([self.server_socket], [], [], 10)
            if self.server_socket in readable:
                client_socket, address = self.server_socket.accept()
                executor.submit(self.send_basic_infos, client_socket)
                executor.submit(self.holding_game, client_socket)

    def send_basic_infos(self, client_socket):
        with client_socket as s:
            s.sendall(b'hi')
            print("sent basic infos")

    def holding_game(self, client_socket):
        s = client_socket
        while True:
            data = s.recv(1024)
            print(data.decode)
            if data == 'pause':
                self.counting = False
            elif data == 'run':
                self.counting = True
            time.sleep(1)

    def count(self):
        n = 0
        while self.counting:
            n += 1
            print(n)
            time.sleep(1)


if __name__ == "__main__":
    game = server()
    processes = []
    processes.append(Process(target=game.socket_connection, args=()))
    processes.append(Process(target=game.count, args=()))

    for p in processes:
        p.start()
    for p in processes:
        p.join()
