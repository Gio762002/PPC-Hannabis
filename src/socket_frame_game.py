from multiprocessing import Process, Queue, Value, Array, Manager, Pool
from multiprocessing.managers import BaseManager
import concurrent.futures
import socket
import select


class Game:

  def __init__(self):

    self.manager = BaseManager(address=('localhost', 50000), authkey=b'shared')
    self.array = Array('i', [0, 0, 0, 0, 0, 0, 0, 0])
    
    self.server_p = Process(target=self.server_process)
    self.server_p.start()

    self.connecting(2)

  def server_process(self):
    self.server = self.manager.get_server()
    self.server.serve_forever()

  def connecting(self, n):
    HOST = "localhost"
    PORT = 8848
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
      server_socket.bind((HOST, PORT))
      server_socket.listen(n)
      with concurrent.futures.ProcessPoolExecutor() as executor:
        while True:
          readable, _, _ = select.select([server_socket], [], [], 10)
          if server_socket in readable:
            client_socket, address = server_socket.accept()
            executor.submit(self.client_handler, client_socket, address)

  def client_handler(self, client_socket, address):
    with client_socket as s:
      while True:
        data = s.recv(1024)
        print("Received data from:", address, ":", data)
        if not data:
          break
        s.sendall(data)
        print("Sent data to:", address, ":", data)


if __name__ == "__main__":
  game = Game()
