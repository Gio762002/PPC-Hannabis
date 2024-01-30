import random
from multiprocessing import Process, Queue, shared_memory, Pool
from threading import Event
import concurrent.futures
import socket
import select
import numpy as np
import struct
import sysv_ipc


class Player:

    def __init__(self):
        self.nb_players = 4
        self.gaming = True  # True represents that the game is running

        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.queue = None
        # self.interqueue = Queue()  # a queue for inter-process communication
        self.draw_req = Event()
        self.hands = {1: [], 2: [], 3: [], 4: []}

    def attach_to_shm(self):
        self.shm_pool = []
        self.suits = sysv_ipc.SharedMemory(300, sysv_ipc.IPC_CREAT,
                                           5 * self.nb_players)
        self.shm_pool.append(self.suits)

        self.information_tokens = sysv_ipc.SharedMemory(
            301, sysv_ipc.IPC_CREAT, 1)
        self.shm_pool.append(self.information_tokens)

        self.fuse_tokens = sysv_ipc.SharedMemory(302, sysv_ipc.IPC_CREAT, 1)
        self.shm_pool.append(self.fuse_tokens)

        for shm in self.shm_pool:
            shm.attach()

    def connect_to_game(self):
        HOST = "localhost"
        PORT = 8848
        self.client_socket.connect((HOST, PORT))
        print("connected to game host")
        self.ack = False
        self.init_game()
        # self.interp_com()

    def ack(self, send=True):
        if send:
            self.client_socket.sendall(b"ack")
        else:
            self.client_socket.recv(10).decode()

    def init_game(self):
        print("start initializing, please wait")
        # receiving the number of players and player id
        try:
            self.nb_players = struct.unpack("i",
                                            self.client_socket.recv(10))[0]
        except Exception as e:
            print("Error getting number of players: ", e)
        else:
            self.ack(True)
            print("game begins, you are one of the ",
                  self.nb_players,
                  " players,",
                  end=' ')

        try:
            self.player_id = struct.unpack("i", self.client_socket.recv(10))[0]
        except Exception as e:
            print("Error getting player id : ", e)
        else:
            self.ack(True)
            print("you are player no.", self.player_id)

        # dealing five cards
        try:
            data = self.client_socket.recv(
                1024).decode()  #something like "(1,2),(0,3),(0,4),(2,1),(1,5)"
            self.hands[self.player_id] = self.convert_dataflow_to_list(data)
        except Exception as e:
            print("Error getting hand : ", e)
        else:
            self.ack(True)

    # def interp_com(self):
    #     while True:
    #         try:
    #             if not self.interqueue.empty(
    #             ):  # Check if the queue is not empty
    #                 req = self.interqueue.get_nowait()  # or queue.get()
    #                 if req == "draw":
    #                     self.client_socket.sendall(req.encode())
    #                     res = self.client_socket.recv(10)
    #                     res = res.decode()
    #                     self.interqueue.put(res)
    #         except Exception as e:
    #             print("Error in interprocess communication: ", e)
    # if we used multi-thread, we dont need this, we need only event
    def holding(self):
        while self.gaming:
            self.draw_req.wait()
            self.client_socket.sendall(b"draw")
            data = self.client_socket.recv(10)
            self.new_card = data.decode()
            self.draw_req.clear()

    def connect_to_mq(
        self
    ):  # connect to the queue created by game for exchanging information between processes
        self.objects_dict = {}
        for i in range(self.nb_players):
            object_name = f'object_{i}'
            self.objects_dict[object_name] = sysv_ipc.MessageQueue(
                self.queue, sysv_ipc.IPC_CREAT)

    def send_via_mq(self, message, type):
        pass

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
            # before every turn starts, update hands.
            self.get_update_hand()
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
        old_card_indice = self.choose_card()
        new_card = self.draw_card()
        self.replace_card(old_card_indice, new_card)
        self.update_hand()
        self.check_if_added_to_suit(new_card)

    def choose_card(self):
        while True:
            chose = input(
                "Please choose a card to play : 1-5 from left to right")
            try:
                if int(chose) in range(1, 6):
                    break
                else:
                    print("please enter a correct number")
            except Exception:
                print("please enter a number")
                continue
            return (int(chose) - 1)

    def draw_card(self):
        # self.interqueue.put('draw')
        # new_card = self.interqueue.get()
        # return (new_card)  # new_card is like "2,3"
        # use new_card to replace the card that has been used
        self.draw_req.set()
        while True:  #wait for self.new_card
            try:
                new_card = self.new_card
                return (new_card)
            except Exception:
                continue

    def replace_card(self, old_card_indice, new_card):
        self.hands[self.player_id][old_card_indice] = new_card

    def update_hand(self):  #是不是应该明确谁是发送者
        # new_hand is like "(1,2),(0,3),(0,4),(2,1),(1,5)"
        new_hand = self.hands[self.player_id]
        new_hand = str(new_hand)[1:-1]
        message = new_hand.encode()
        for name, obj in self.objects_dict.items():
            obj.send(message, type=2)

    def get_update_hand(self):
        pass  #TODO 接收更新，默认在每个回合开始前调用一次，包括游戏开始之初。

    # def update_tokens(self, value):
    #     message = str(value).encode()
    #     for name, obj in self.objects_dict.items():
    #         obj.send(message, type=2)
    #不用特意写成函数，因为是shm随时可用

    def check_if_added_to_suit(self, new_card):
        (color, number) = new_card
        top_on_suit = []
        bottoms = [0, 5, 10, 15, 20, 25, 30, 35]
        for i in bottoms:
            j = i
            while True:
                now = self.suits.read(1, j)
                if now != ' ':
                    j += 1
                else:
                    top_on_suit.append((i / 5, j - i))
                    break
        for (topcolor, topnumber) in top_on_suit:
            if topcolor == color:
                if topnumber == number - 1:  # success
                    self.suits.write(b'1', topcolor * 5 + topnumber + 1)
                    ind = top_on_suit.index(topcolor, topnumber)
                    top_on_suit[ind] = (topcolor, number)
                    # we dont need to write the value, just sth != ' '
                    if number == 5:
                        information_tokens = int(
                            self.information_tokens.read(1))
                        self.information_tokens.write(
                            f'{information_tokens+1}'.encode)
                else:
                    fuse_tokens = int(self.fuse_tokens.read(1))
                    self.fuse_tokens.write(f'{fuse_tokens-1}'.encode)
                    if fuse_tokens - 1 <= 0:
                        pass  #TODO: signal game over: lose
        win = True
        for (_, topnumber) in top_on_suit:
            if topnumber != 5:
                win = False
                break
        if win:
            pass  #TODO : signal game over: win

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

    def display(self):
        for nb, cards in self.hands.items():
            print(f"Player {nb} hand: {cards}")
        print("token information: ", self.information_tokens)
        print("token fuse: ", self.fuse_tokens)
        print("constructing suits: ", )

    def convert_dataflow_to_list(self, flow):
        tuplized = flow.replace("(", "").replace(")", "").split(",")
        return ([tuple(map(int, tpl.split(','))) for tpl in tuplized])


if __name__ == "__main__":
    player = Player()
    with Pool(2) as pool:
        pool.apply_async(player.display, ())
        pool.apply_async(player.connect_to_game, ())
        pool.apply_async(player.connect_to_mq, ())
        pool.apply_async(player.play_game, ())
