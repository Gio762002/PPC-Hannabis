from multiprocessing import Process, Queue, Value, Array, Manager, Pool
from multiprocessing.managers import BaseManager
import socket


class Player:

  def __init__(self):

    self.m = BaseManager(address=("localhost", 50000), authkey=b"shared")
    self.m.connect()
    self.connect_to_game()

  def connect_to_game(self):
    HOST = "localhost"
    PORT = 8848
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
      client_socket.connect((HOST, PORT))
      shared = client_socket.recv(1024).decode()
      print("receiving shared data")
      print(shared)
      for i in range(5):
        client_socket.sendall(str(i).encode())
        client_socket.recv(1024)


if __name__ == "__main__":
  player = Player()
