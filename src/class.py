import random

class Game:
    '''
    implements the game session, manages the deck and keeps track of suits in construction
    '''
    def __init__(self,number_of_players):
        self.number_of_players = number_of_players
        """
        以下变量需要被player process请求获得
        """
        self.deck = []
        self.shuffle_deck()
        """
        stored in a shared memory
        """
        self.discarded_cards = [] #I suppose that in the real game, players should check the discarded cards
        self.information_tokens = number_of_players + 3
        self.fuse_tokens = 3
        self.suits_in_construction = [[] for i in range(number_of_players)]
        self.suits_completed = []

    def shuffle_deck(self):
        reserved_suit =[1,1,1,2,2,3,3,4,4,5]
        reserved_deck = [(i,j) for i in range(self.number_of_players) for j in reserved_suit] #card = (color,number)
        self.deck = random.shuffle(reserved_deck)

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
        if card[1]==1 and len(self.suits_in_construction[card[0]]) == 0: #if the card is 1 and the suit is empty
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
    def __init__(self):
        self.hand = [(0,0) for i in range(5)]
        