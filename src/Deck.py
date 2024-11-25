from src.Card import Card
from src.Enums import CardValue, CardType
import random

class Deck(Card):
    def __init__(self):
        self.deck = []
        self.build()

    def build(self):
        for value in CardValue:
            for type in CardType:
                self.deck.append(Card(value, type))

    def shuffle(self):
        random.shuffle(self.deck)

    def draw(self):
        return self.deck.pop()

    def __str__(self):
        deck = ""
        for card in self.deck:
            deck += str(card) + "\n"
        return deck