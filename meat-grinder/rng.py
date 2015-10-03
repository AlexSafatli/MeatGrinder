# rng.py
# -------------------------
# Fall 2015; Alex Safatli
# -------------------------
# Random Number Generation Assets

class dice:
    def __init__(self,num,sides):
        self.num = num
        self.sides = sides
    def roll(self):
        result = 0
        for i in xrange(self.num):
            result += r.randint(1,self.sides)
        return result