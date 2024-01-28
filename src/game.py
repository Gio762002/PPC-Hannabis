import random
from multiprocessing import Process, Queue, shared_memory, Pool
import concurrent.futures
import signal
import sys
import socket
import select
import numpy as np
import struct


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
        print(self.shm_names)

    def create_shared_memory(self):
        card_type = np.dtype([('color', np.uint8), ('number', np.uint8)])
        discard_pile = np.zeros(self.number_of_players * 10, dtype=card_type)
        suits_in_construction = np.zeros([self.number_of_players, 10],
                                         dtype=card_type,
                                         order='C')
        suits_completed = np.zeros(self.number_of_players, dtype=np.uint8)
        information_tokens = np.zeros(1, dtype=np.uint8)
        information_tokens[0] = self.number_of_players + 3
        fuse_tokens = np.zeros(1, dtype=np.uint8)
        fuse_tokens[0] = 3

        try:
            discard_pile_buf = shared_memory.SharedMemory(
                create=True, size=discard_pile.nbytes)
            suits_in_construction_buf = shared_memory.SharedMemory(
                create=True, size=suits_in_construction.nbytes)
            suits_completed_buf = shared_memory.SharedMemory(
                create=True, size=suits_completed.nbytes)
            information_tokens_buf = shared_memory.SharedMemory(
                create=True, size=information_tokens.nbytes)
            fuse_tokens_buf = shared_memory.SharedMemory(
                create=True, size=fuse_tokens.nbytes)
        except Exception as e:
            print("Error creating shared memory buffers: ", e)

        try:
            self.discard_pile = np.ndarray(discard_pile.shape,
                                           dtype=discard_pile.dtype,
                                           buffer=discard_pile_buf.buf)
            self.suits_in_construction = np.ndarray(
                suits_in_construction.shape,
                dtype=suits_in_construction.dtype,
                buffer=suits_in_construction_buf.buf)
            self.suits_completed = np.ndarray(suits_completed.shape,
                                              dtype=suits_completed.dtype,
                                              buffer=suits_completed_buf.buf)
            self.information_tokens = np.ndarray(
                information_tokens.shape,
                dtype=information_tokens.dtype,
                buffer=information_tokens_buf.buf)
            self.fuse_tokens = np.ndarray(fuse_tokens.shape,
                                          dtype=fuse_tokens.dtype,
                                          buffer=fuse_tokens_buf.buf)
        except Exception as e:
            print("Error creating shared memory buffers: ", e)

        self.shm_pool = [
            discard_pile_buf, suits_in_construction_buf, suits_completed_buf,
            information_tokens_buf, fuse_tokens_buf
        ]
        self.shm_names = {
            "discard_pile": discard_pile_buf.name,
            "suits_in_construction": suits_in_construction_buf.name,
            "suits_completed": suits_completed_buf.name,
            "information_tokens": information_tokens_buf.name,
            "fuse_tokens": fuse_tokens_buf.name
        }

    def delete_shared_memory(self):
        for shm in self.shm_pool:
            shm.close()
            shm.unlink()

    def run(self):
        HOST = "localhost"
        PORT = 8848
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind((HOST, PORT))
        server_socket.listen(self.number_of_players)
        with concurrent.futures.ProcessPoolExecutor() as executor:
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
                s.sendall(self.shm_names["discard_pile"].encode())
                self.ack_reception(s)
                s.sendall(self.shm_names["suits_in_construction"].encode())
                self.ack_reception(s)
                s.sendall(self.shm_names["suits_completed"].encode())
                self.ack_reception(s)
                s.sendall(self.shm_names["information_tokens"].encode())
                self.ack_reception(s)
                s.sendall(self.shm_names["fuse_tokens"].encode())
                self.ack_reception(s)
            except Exception as e:
                print("Error sending basic infos: ", e)

    def handle_sigint(self, signal, frame):
        if self.gaming:
            print("releasing shared memory before exiting")
            self.gaming = False
            try:
                self.delete_shared_memory()
                exit(0)
            except Exception as e:
                print("")


if __name__ == "__main__":
    game = Game(2)
    signal.signal(signal.SIGINT, game.handle_sigint)
    game.run()
    # with Pool(2) as pool:
    #     pool.apply(game.run, ())
