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
            id_player = struct.unpack("i", s.recv(1024))[0]
            self.ack_send(s)
            print(id_player)
            discard_pile_name = s.recv(1024).decode()
            self.ack_send(s)
            print(discard_pile_name)
            suits_in_construction_name = s.recv(1024).decode()
            self.ack_send(s)
            print(suits_in_construction_name)
            suits_completed_name = s.recv(1024).decode()
            self.ack_send(s)
            print(suits_completed_name)
            information_tokens_name = s.recv(1024).decode()
            self.ack_send(s)
            print(information_tokens_name)
            fuse_tokens_name = s.recv(1024).decode()
            self.ack_send(s)
            print(fuse_tokens_name)
        except Exception as e:
            print("Error receiving basic infos: ", e)
        else:
            print("received basic infos")


if __name__ == "__main__":
    player = Player()
    with Pool(2) as pool:
        pool.apply(player.connect_to_game, ())
