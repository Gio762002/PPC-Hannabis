import random
from multiprocessing import Process, Queue, shared_memory, Pool
import concurrent.futures
import socket
import select
import numpy as np
import struct


class Player:

    def __init__(self):
        self.shm = None

    def connect_to_game(self):
        HOST = "localhost"
        PORT = 8848
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((HOST, PORT))
        print("connected to game host")
        self.receive_basic_infos(client_socket)

    def ack_send(self, client_socket):
        client_socket.sendall("ack".encode())
        print("ack sent")

    def receive_basic_infos(self, client_socket):
        print("start receiving basic infos")
        s = client_socket
        try:
            self.id_player = struct.unpack("i", s.recv(1024))[0]
            self.ack_send(s)

        except Exception as e:
            print("Error receiving basic infos: ", e)
        else:
            print("received basic infos")


if __name__ == "__main__":
    player = Player()
    with Pool(2) as pool:
        pool.apply(player.connect_to_game, ())
