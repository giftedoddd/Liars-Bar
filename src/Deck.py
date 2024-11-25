from src.Card import Card
from src.Enums import CardValue, CardType
import random

class Deck:
    def __init__(self):
        self.cards = []
        for value in CardValue:
            for type in CardType:
                self.cards.append(Card(value, type))
        self.shuffle()
    
    def shuffle(self):
        random.shuffle(self.cards)
    
    def draw(self):
        return self.cards.pop()
    
    def __len__(self):
        return len(self.cards)