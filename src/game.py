from multiprocessing import Process, Queue
import concurrent.futures
import socket
import select
import struct
import sysv_ipc
import random
import signal
import sys


class Game:
    '''
    implements the game session, manages the deck and keeps track of suits in construction
    '''

    def __init__(self, number_of_players):
        self.number_of_players = number_of_players
        self.gaming = True
        self.queuekey = 128
        self.create_message_queue()
        self.create_shared_memory()
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.deck = []
        self.shuffle_deck()

    def create_shared_memory(self):
        self.shm_pool = []
        self.suits = sysv_ipc.SharedMemory(300, sysv_ipc.IPC_CREX,
                                           5 * self.number_of_players)
        self.shm_pool.append(self.suits)

        self.information_tokens = sysv_ipc.SharedMemory(
            301, sysv_ipc.IPC_CREX, 1)
        itok = self.number_of_players + 3
        self.information_tokens.write(struct.pack('i', itok))
        self.shm_pool.append(self.information_tokens)

        self.fuse_tokens = sysv_ipc.SharedMemory(302, sysv_ipc.IPC_CREX, 1)
        self.fuse_tokens.write(b'3')
        self.shm_pool.append(self.fuse_tokens)

        for shm in self.shm_pool:
            shm.attach()

    def create_message_queue(self):
        self.mq = sysv_ipc.MessageQueue(self.queuekey, sysv_ipc.IPC_CREAT)

    def socket_connection(self):
        HOST = "localhost"
        PORT = 8848

        self.server_socket.bind((HOST, PORT))
        self.server_socket.listen(self.number_of_players)
        executor = concurrent.futures.ProcessPoolExecutor()
        while self.gaming:
            readable, _, _ = select.select([self.server_socket], [], [], 10)
            id_player = 1
            if self.server_socket in readable:
                client_socket, address = self.server_socket.accept()
                executor.submit(self.init_game, client_socket, id_player)
                id_player += 1
                executor.submit(self.holding, client_socket)

    def ack(self, s):
        while True:
            recv = s.recv(1024).decode()
            if recv == "ack":
                break

    def holding(self, s):
        while self.gaming:
            try:
                data = s.recv(1024)
                if data.decode() == "draw":
                    new_card = self.distribute_card()
                    s.send(str(new_card).encode())
                elif data.decode() == "end":
                    self.end_game()

            except Exception as e:
                print("Error while holding the game :", e)

    def init_game(self, client_socket, id_player):
        s = client_socket
        try:
            s.sendall(struct.pack("i", self.number_of_players))
            s.sendall(struct.pack("i", id_player))
            self.ack(s)
            cards = str(self.distribute_card(True))[1:-1]
            s.sendall(cards.encode())
            self.ack(s)
        except Exception as e:
            print("Error initializing the game : ", e)

    def end_game(self):
        self.server_socket.close()
        self.mq.remove()
        for shm in self.shm_pool:
            shm.detach()

    def shuffle_deck(self):
        reserved_suit = [1, 1, 1, 2, 2, 3, 3, 4, 4, 5]
        reserved_deck = [(i, j) for i in range(self.number_of_players)
                         for j in reserved_suit]
        #card = (color,number)
        random.shuffle(reserved_deck)
        self.deck = reserved_deck

    def distribute_card(self, init=False):
        """
        distibute a card to a player, if init is True, distribute 5 cards to each player, means the game is just started
        """
        if init:
            return [self.deck.pop(0) for i in range(5)]
        else:
            return self.deck.pop(0)

    def cleanup_before_exit(self, signal, frame):
        try:
            self.server_socket.close()
            for shm in self.shm_pool:
                shm.detach()
        except Exception as e:
            pass
        sys.exit(0)


if __name__ == "__main__":
    game = Game(2)
    signal.signal(signal.SIGINT, game.cleanup_before_exit)
    # game.run()
    processes = []
    processes.append(Process(target=game.socket_connection, args=()))
    for p in processes:
        p.start()
    for p in processes:
        p.join()
