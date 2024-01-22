import random
from multiprocessing import Process, Queue, Value, Array, Manager, Pool
import concurrent.futures
import socket
import select

class Game:
    '''
    implements the game session, manages the deck and keeps track of suits in construction
    '''
    def __init__(self,number_of_players):
        self.number_of_players = number_of_players
        self.serve = True
        self.connecting()
        """
        以下变量需要被player process请求获得
        """
        self.deck = []
        self.shuffle_deck()
        """
        stored in a shared memory
        """
        with Manager() as manager:
            self.discard_pile = manager.list()
            self.suits_in_construction = manager.list()
            for _ in range(number_of_players):
                self.suits_in_construction.append(manager.list())#suits_in_construction = [[],[],[],[]] if 4 players
            self.suits_completed = manager.list()
            self.information_tokens = Value('i',number_of_players + 3)
            self.fuse_tokens = Value('i',3)

    """
    fuunction of connecting to player process via socket
    """
    def connecting(self):
        HOST = "localhost"
        PORT = 8848
        with concurrent.futures.ProcessPoolExecutor() as executor:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
                server_socket.bind((HOST, PORT))
                server_socket.listen(self.number_of_players)
                while self.serve:
                    readable, _, _ = select.select([server_socket], [], [], 1)
                    if server_socket in readable:
                        client_socket, address = server_socket.accept()
                        executor.submit(self.client_handler,client_socket,address)
    
    """
    function of handling client socket
    """
    def client_handler(self,client_socket,address):
        pass

    '''
    functions below are related to the gameplay
    '''
    def shuffle_deck(self):
        reserved_suit =[1,1,1,2,2,3,3,4,4,5]
        reserved_deck = [(i,j) for i in range(self.number_of_players)for j in reserved_suit] #card = (color,number)
        random.shuffle(reserved_deck)
        self.deck = reserved_deck

    def distribute_card(self,init=False):
        """distibute a card to a player, if init is True, distribute 5 cards to each player, means the game is just started"""
        if init:
            return [self.deck.pop(0) for i in range(5)]
        else:
            return self.deck.pop(0)
    
    def remove_token(self,token_type):
        if token_type == "information":
            if self.information_tokens == 0:
                pass #TODO: send signal to player process
            else:
                self.information_tokens -= 1
        elif token_type == "fuse":
            if self.fuse_tokens == 0:
                pass #TODO: send signal to player process, lose game
            else:
                self.fuse_tokens -= 1
        else:
            raise Exception("invalid token type")
    
    def test_entry_construction(self,card): #card = (color,number)
        """
        test if the card can be added to the suit_in_construction
        """
        if len(self.suits_in_construction[card[0]]) == 0: #if the card is 1 and the suit is empty
            if card[1]==1:
                self.suits_in_construction[card[0]].append(card)
                #TODO: send signal to player process
        else:
            if self.suits_in_construction[card[0]][-1][1] == card[1]-1: #if the card is the next card of the suit
                self.suits_in_construction[card[0]].append(card)
            else:
                self.fuse_tokens -= 1
                self.discarded_cards.append(card)
                #TODO: send signal to player process, add failed, and draw a new card


class Player:
    """
    """
    def __init__(self,id):
        self.player_id = id
        self.hand = [(0,0) for i in range(5)]

    def connect_to_game(self): 
        HOST = "localhost"
        PORT = 8848
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
            client_socket.connect((HOST, PORT))
            while True:
                pass