from random import randint


class Dice:
    def __init__(self, num: int, sides: int):
        self.num = num
        self.sides = sides

    def roll(self) -> int:
        result = 0
        for _ in range(self.num):
            result += randint(1, self.sides)
        return result
