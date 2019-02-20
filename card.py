from enum import Enum, auto
from random import random


class Age(Enum):
    STONE = 1
    IRON = 2
    CRYSTAL = 4


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


BASE_STRENGTH = {Age.STONE: 3, Age.IRON: 5, Age.CRYSTAL: 8}


class Card:

    def __init__(self, strength, age, race, prof, desc=''):
        self.strength = strength
        self.age = age
        self.race = race
        self.prof = prof
        self.desc = desc

    def __repr__(self):
        return f'Card({self.strength},{self.age},{self.race},{self.prof},{self.desc})'

    def __str__(self):
        return repr(self)

    def calcStrength(self, deck, oppDeck):
        return self.strength


def generate_basic_pool():
    pool = []
    for age in Age:
        for race in Race:
            for prof in Profession:
                strength = BASE_STRENGTH[age]
                if random() > .1:
                    pool.append(Card(strength, age, race, prof))
                if age != Age.CRYSTAL and random() > .1:
                    pool.append(Card(strength, age, race, prof))
    return pool


def generate_pool():
    pool = generate_basic_pool()
    for card in pool:
        r = random()
        if r < .1:
            # stronger card
            card.strength = card.strength + card.age.value
        elif r < .2:
            # easy synergy
            card.desc = 'easy synergy which has a super long desc which would never fit on a card ever because it is way too long'
        elif r < .3:
            # tough synergy
            card.desc = 'tough synergy'
        elif r < .4:
            # counter
            card.desc = 'counter'
    return pool
