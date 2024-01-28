import random
from multiprocessing import Process, Queue, shared_memory
import concurrent.futures
import socket
import select
import numpy as np


class Player:

    def __init__(self):
        self.shm = None
        self.connect_to_game()

    def connect_to_game(self):
        HOST = "localhost"
        PORT = 8848
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
            client_socket.connect((HOST, PORT))
        print("connected to game host")
        with concurrent.futures.ProcessPoolExecutor() as executor:
            executor.submit(self.receive_basic_infos, client_socket)

    def receive_basic_infos(self, client_socket):
        with client_socket as s:
            try:
                id_player = s.recv(1024).decode()
                print(id_player)
                discard_pile_name = s.recv(1024).decode()
                print(discard_pile_name)
                suits_in_construction_name = s.recv(1024).decode()
                print(suits_in_construction_name)
                suits_completed_name = s.recv(1024).decode()
                print(suits_completed_name)
                information_tokens_name = s.recv(1024).decode()
                print(information_tokens_name)
                fuse_tokens_name = s.recv(1024).decode()
                print(fuse_tokens_name)
            except Exception as e:
                print("Error receiving basic infos: ", e)
            else:
                print("received basic infos")