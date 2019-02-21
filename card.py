from enum import Enum, auto
from math import ceil
from random import random, choice


class Age(Enum):
    STONE = 1
    IRON = 2
    CRYSTAL = 4


class Race(Enum):
    BEASTMAN = auto()
    UNDEAD = auto()
    HUMAN = auto()


class Profession(Enum):
    ALCHEMIST = auto()
    BATTLETECH = auto()
    CONJUROR = auto()
    PROPHET = auto()
    WOODSMAN = auto()
    PEASANT = auto()


class Mod(Enum):
    NORMAL = auto()
    WEAK = auto()
    STRONG = auto()
    EASY_SYNERGY = auto()
    HARD_SYNERGY = auto()
    COUNTER = auto()


USEFUL_PROFS = [prof for prof in list(Profession) if prof != Profession.PEASANT]
BASE_STRENGTH = {
    Age.STONE: [3, 3, 3],
    Age.IRON: [0, 5, 5],
    Age.CRYSTAL: [0, 0, 8]
}
EASY_PROF_SYNERGY_THRESHOLD = 5
HARD_PROF_SYNERGY_THRESHOLD = 8
EASY_RACE_SYNERGY_THRESHOLD = 9
HARD_RACE_SYNERGY_THRESHOLD = 16


class Card:

    def __init__(self, strength, age, race, prof, desc='', mod=Mod.NORMAL, synergy=lambda a, b, c, d: 0):
        self.strength = strength
        self.age = age
        self.race = race
        self.prof = prof
        self.desc = desc
        self.mod = mod
        self.synergy = synergy

    def __repr__(self):
        return f'Card({self.strength},{self.age},{self.race},{self.prof},{self.desc})'

    def __str__(self):
        return repr(self)

    def set_synergy(self, synergy):
        self.synergy = synergy

    def calc_strength(self, ageIdx, deck, oppDeck):
        return self.strength[ageIdx] + self.synergy(self, ageIdx, deck, oppDeck)


def generate_basic_pool():
    pool = []
    for age in Age:
        for race in Race:
            for prof in Profession:
                strength = BASE_STRENGTH[age][:]
                # TODO delete as part of the normal generate pool function
                if random() > .1:
                    pool.append(Card(strength, age, race, prof))
                if age != Age.CRYSTAL and random() > .1:
                    pool.append(Card(strength, age, race, prof))
    return pool


# TODO: should cards be affected by their own types?  Should race synergies and prof synergies happen equally often?
def generate_easy_synergy(card):
    card.mod = Mod.EASY_SYNERGY
    synergy = choice(list(Race) + USEFUL_PROFS)
    threshold = EASY_RACE_SYNERGY_THRESHOLD if isinstance(synergy, Race) else EASY_PROF_SYNERGY_THRESHOLD

    def calc_synergy_strength(self, ageIdx, deck, oppDeck):
        if self.strength[ageIdx] == 0:
            return 0
        synergisticCards = filter(lambda c: c.prof == synergy or c.race == synergy, deck)
        if sum(1 for x in synergisticCards) >= threshold:
            return self.strength[ageIdx] + self.age.value
        return self.strength[ageIdx]
    card.set_synergy(calc_synergy_strength)
    card.desc = f'{threshold}+ {synergy.name.lower().capitalize()} for +{card.age.value}str'


def generate_hard_synergy(card):
    card.mod = Mod.HARD_SYNERGY
    card.strength = list(map(lambda str: str - 1 if str > 0 else 0, card.strength))
    synergy = choice(list(Race) + USEFUL_PROFS)
    threshold = HARD_RACE_SYNERGY_THRESHOLD if isinstance(synergy, Race) else HARD_PROF_SYNERGY_THRESHOLD

    def calc_synergy_strength(self, ageIdx, deck, oppDeck):
        if self.strength[ageIdx] == 0:
            return 0
        synergisticCards = filter(lambda c: c.prof == synergy or c.race == synergy, deck)
        if sum(1 for x in synergisticCards) >= threshold:
            return self.strength[ageIdx] + 1 + ceil(self.age.value * 1.5)
        return self.strength[ageIdx]
    card.set_synergy(calc_synergy_strength)
    card.desc = f'{threshold}+ {synergy.name.lower().capitalize()} for +{1 + ceil(card.age.value * 1.5)}str'


def generate_pool():
    pool = generate_basic_pool()
    for card in pool:
        if card.prof == Profession.PEASANT:
            continue
        r = random()
        if r < .1:
            # stronger card
            card.mod = Mod.STRONG
            card.strength = list(map(lambda str: str + card.age.value if str > 0 else 0, card.strength))
        elif r < .2:
            # easy synergy
            generate_easy_synergy(card)
        elif r < .3:
            # hard synergy
            generate_hard_synergy(card)
        elif r < .4:
            # counter
            card.mod = Mod.COUNTER
            card.desc = 'counter'
    return pool
