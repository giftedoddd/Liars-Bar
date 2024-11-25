from src.Enums import CardValue, CardType


class Card:
    def __init__(self, value: CardValue, type: CardType):
        self.value = value
        self.type = type
    
    def __str__(self):
        return f"{self.value} of {self.type}"