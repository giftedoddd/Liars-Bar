# - Each player holds a revolver with 1 bullet randomly loaded in one of the 6 chambers
import random

class Gun:
    def __init__(self):
        self.chambers = [False] * 6
        self.chambers[random.randint(0, 5)] = True

    def fire(self):
        bullet = self.chambers.pop(0)
        self.chambers.append(False)
        return bullet