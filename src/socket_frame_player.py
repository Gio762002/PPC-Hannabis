from multiprocessing import Process, Queue, Value, Array, Manager, Pool
import concurrent.futures
import socket
import select


class Player:

  def __init__(self):
    self.connect_to_game()

  def connect_to_game(self):
    HOST = "localhost"
    PORT = 8848
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
      client_socket.connect((HOST, PORT))
      i = 0
      while True:
          client_socket.sendall(str(i).encode())
          i += 1
      


if __name__ == "__main__":
  player = Player()