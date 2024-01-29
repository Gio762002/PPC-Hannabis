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
        self.tokens_information = self.nb_players + 3
        self.tokens_fuse = 0

    def connect_to_game(self):
        HOST = "localhost"
        PORT = 8848
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect((HOST, PORT))
        print("connected to game host")
        self.receive_basic_infos()

    def connect_to_mq(self):
        self.objects_dict = {}
        for i in range(self.nb_players):
            object_name = f'object_{i}'
            self.objects_dict[object_name] = sysv_ipc.MessageQueue(
                self.queue, sysv_ipc.IPC_CREAT)

    def send_via_mq(self, message, type):
        pass

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
        value = self.draw_card()
        self.update_hand(value)

    #execute connect_to_mq before give_information
    def give_information(self):
        while True:
            try:

                while True:
                    name_players = input(
                        "Give information for (1:player 1, 2: player 2): ")
                    try:
                        if int(name_players) <= self.nb_players and int(
                                name_players) > 0:
                            break
                        else:
                            print("Please enter a valid number")

                    except Exception as e:
                        print("Please enter a correct number!")
                        continue

                while True:
                    color_number = input(
                        "Please give a color or a number of cards: ")
                    try:
                        if color_number in [
                                "1", "2", "3", "4", "5", "blue", "red",
                                "green", "purple", "orange", "yellow", "white",
                                "black"
                        ]:
                            break
                        else:
                            print("Please enter a valid color or number")

                    except Exception as e:
                        print("Please enter a correct number!")
                        continue

                while True:
                    nb = input("How many cards are the same color or number: ")
                    try:
                        if int(nb) < 5 and int(nb) > 0:
                            break
                        else:
                            print("Please enter a valid number")

                    except Exception as e:
                        print("Please enter a correct number!")
                        continue
                value = "Player " + str(name_players) + " has " + str(
                    nb) + " " + str(color_number) + " cards"

            except EOFError:
                break
            except Exception as e:
                print("Input error:", e)
                continue

            message = str(value).encode()
            for name, obj in self.objects_dict.items():
                obj.send(message)

            message = "exit".encode()
            for name, obj in self.objects_dict.items():
                obj.send(message)

            break

    def draw_card(self):

        pass

    def update_hand(self, value):
        #value 是socket 传过来的新牌信息
        message = str(value).encode()
        for name, obj in self.objects_dict.items():
            obj.send(message, type=2)

    def update_tokens(self, value):
        message = str(value).encode()
        for name, obj in self.objects_dict.items():
            obj.send(message, type=2)

    def display(self):
        for nb, cards in self.hands.items():
            print(f"Player {nb} hand: {cards}")
        print("token information: ", self.tokens_information)
        print("token fuse: ", self.tokens_fuse)
        print("constructing suits: ", )


if __name__ == "__main__":
    player = Player()
    with Pool(2) as pool:
        pool.apply_async(player.display, ())
        pool.apply_async(player.connect_to_game, ())
        pool.apply_async(player.connect_to_mq, ())
        pool.apply_async(player.play_game, ())
