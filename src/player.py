import random
from multiprocessing import Process, Queue, shared_memory, Pool
import concurrent.futures
import socket
import select
import numpy as np
import struct
import sysv_ipc


class Player:

    def __init__(self):
        self.shm = None
        self.nb_players = 4
        self.gaming = True  # True represents that the game is running
        self.queue = None
        self.hands = {1: [], 2: [], 3: [], 4: []}

    def connect_to_game(self):
        HOST = "localhost"
        PORT = 8848
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect((HOST, PORT))
        print("connected to game host")
        self.receive_basic_infos()

    def connect_to_mq(self):
        objects_dict = {}
        for i in range(self.nb_players):
            object_name = f'object_{i}'
            objects_dict[object_name] = sysv_ipc.MessageQueue(
                self.queue, sysv_ipc.IPC_CREAT)

    def ack_send(self):
        self.client_socket.sendall("ack".encode())
        print("ack sent")

    def receive_basic_infos(self):
        print("start receiving basic infos")
        self.client_socket
        try:
            self.id_player = struct.unpack("i",
                                           self.client_socket.recv(1024))[0]
            self.ack_send()

        except Exception as e:
            print("Error receiving basic infos: ", e)
        else:
            print("received basic infos")

    def send_via_socket(self):
        try:
            self.client_socket.sendall("draw".encode())
        except Exception as e:
            print("error while demanding to draw: ", e)

    def is_my_turn(self):
        # read from message queue
        self.turn = 0

    def play_game(self):
        while self.gaming == True:
            if self.turn == 0:  #TODO write the veriifcation of the turn
                self.play_turn()

    def play_turn(self):
        action_type = 0
        while action_type not in ['1', '2']:
            action_type = input(
                "Please choose an action: (1:play a card, 2:give information)")

        if action_type == '1':
            self.play_card()

        elif action_type == '2':
            self.give_information()

    def play_card(self):
        self.draw_card()
        self.update_hand()

    def give_information(self):
        pass

    def draw_card(self):

        pass

    def update_hand(self):
        pass


if __name__ == "__main__":
    player = Player()
    with Pool(2) as pool:
        pool.apply(player.connect_to_game, ())
        pool.apply(player.connect_to_mq, ())
        pool.apply(player.play_game, ())
