from enum import Enum, auto


class Age(Enum):
    STONE = 1
    IRON = 2
    CRYSTAL = 3


class Race(Enum):
    BEASTMAN = auto()
    UNDEAD = auto()
    HUMAN = auto()


# should we add none / peasant?
class Profession(Enum):
    ALCHEMIST = auto()
    BATTLETECH = auto()
    CONJUROR = auto()
    PROPHET = auto()
    WOODSMAN = auto()


class Card:

    def __init__(self, strength, age, race, prof):
        self.strength = strength
        self.age = age
        self.race = race
        self.prof = prof

    def __repr__(self):
        return f'Card({self.strength},{self.age},{self.race},{self.prof})'

    def __str__(self):
        return repr(self)

    def calcStrength(self, deck, oppDeck):
        return self.strength


def pool():
    finalPool = []
    for age in Age:
        for race in Race:
            for prof in Profession:
                strength = 3
                if age == Age.IRON:
                    strength = 5
                elif age == Age.CRYSTAL:
                    strength = 8
                if race == Race.BEASTMAN:
                    strength += age.value
                finalPool.append(Card(strength, age, race, prof))
    return finalPool
