from multiprocessing import Process
import concurrent.futures
import socket
import select
import struct
import sysv_ipc
import random


class Game:
    '''
    implements the game session, manages the deck and keeps track of suits in construction
    '''

    def __init__(self, number_of_players):
        self.number_of_players = number_of_players
        self.gaming = True

        self.deck = []
        # self.shuffle_deck()
        self.create_shared_memory()

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

    def socket_connection(self):
        HOST = "localhost"
        PORT = 8848
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind((HOST, PORT))
        server_socket.listen(self.number_of_players)
        executor = concurrent.futures.ProcessPoolExecutor()
        while self.gaming:
            readable, _, _ = select.select([server_socket], [], [], 10)
            id_player = 1
            if server_socket in readable:
                client_socket, address = server_socket.accept()
                executor.submit(self.send_basic_infos, client_socket,
                                id_player)

    def ack_reception(self, client_socket):
        recv = client_socket.recv(1024).decode()
        if recv == "ack":
            print("ack received")

    def send_basic_infos(self, client_socket, id_player):
        with client_socket as s:
            try:
                s.sendall(struct.pack("i", id_player))
                self.ack_reception(s)
            except Exception as e:
                print("Error sending basic infos: ", e)

    def shuffle_deck(self):
        reserved_suit = [1, 1, 1, 2, 2, 3, 3, 4, 4, 5]
        reserved_deck = [(i, j) for i in range(self.number_of_players)
                         for j in reserved_suit]
        #card = (color,number)
        random.shuffle(reserved_deck)
        self.deck = reserved_deck

    def distribute_card(self, init=False):
        """distibute a card to a player, if init is True, distribute 5 cards to each player, means the game is just started"""
        if init:
            return [self.deck.pop(0) for i in range(5)]
        else:
            return self.deck.pop(0)


if __name__ == "__main__":
    game = Game(2)
    # game.run()
    processes = []
    processes.append(Process(target=game.socket_connection, args=()))
    for p in processes:
        p.start()
    for p in processes:
        p.join()
