from enum import Enum, auto
from math import ceil
from random import random, choice


class Age(Enum):
    STONE = 1
    IRON = 2
    CRYSTAL = 4


class Race(Enum):
    BEASTMAN = auto()
    HUMAN = auto()
    UNDEAD = auto()


class Profession(Enum):
    ALCHEMIST = auto()
    BATTLETECH = auto()
    CONJUROR = auto()
    PROPHET = auto()
    WOODSMAN = auto()
    PEASANT = auto()


class Mod(Enum):
    NORMAL = auto()
    DELETE = auto()
    WEAK = auto()
    STRONG = auto()
    EASY_MATCHING_SYNERGY = auto()
    EASY_NONMATCHING_SYNERGY = auto()
    HARD_MATCHING_SYNERGY = auto()
    HARD_NONMATCHING_SYNERGY = auto()
    COUNTER = auto()


USEFUL_PROFS = [prof for prof in list(Profession) if prof != Profession.PEASANT]
BASE_STRENGTH = {
    Age.STONE: [3, 3, 3],
    Age.IRON: [0, 5, 5],
    Age.CRYSTAL: [0, 0, 8]
}
EASY_PROF_SYNERGY_THRESHOLD = 5
EASY_RACE_SYNERGY_THRESHOLD = 9

HARD_PROF_SYNERGY_THRESHOLD = 8
HARD_RACE_SYNERGY_THRESHOLD = 15

PROF_COUNTER_THRESHOLD = 6
RACE_COUNTER_THRESHOLD = 10


class Card:
    cardId = 1

    def __init__(self, strength, age, race, prof, desc='', mod=Mod.NORMAL, synergy=None, calc=lambda self, ageIdx, d, o: self.strength[ageIdx]):
        self.cardId = Card.cardId
        self.strength = strength
        self.age = age
        self.race = race
        self.prof = prof
        self.desc = desc
        self.mod = mod
        self.synergy = synergy
        self.calc = calc
        Card.cardId += 1

    def __repr__(self):
        return f'Card({self.strength},{self.age},{self.race},{self.prof},{self.desc})'

    def __str__(self):
        return repr(self)

    def calc_strength(self, ageIdx, deck, oppDeck):
        return self.calc(self, ageIdx, deck, oppDeck)


def generate_basic_pool():
    pool = []
    for age in Age:
        for race in Race:
            for prof in Profession:
                strength = BASE_STRENGTH[age][:]
                pool.append(Card(strength, age, race, prof))
                if age != Age.CRYSTAL:
                    pool.append(Card(strength, age, race, prof))
    return pool


def _weaken(strength):
    return list(map(lambda stre: stre - 1 if stre > 0 else 0, strength))


def synergy_count(deck, synergy):
    return sum(c.prof == synergy or c.race == synergy for c in deck)


def generate_easy_synergy(card, matching):
    choices = set([])
    threshold = 0
    if matching:
        card.mod = Mod.EASY_MATCHING_SYNERGY
        choices = set([card.race, card.prof])
        threshold = 1
    else:
        card.mod = Mod.EASY_NONMATCHING_SYNERGY
        choices = set(Race) | set(USEFUL_PROFS) - set([card.race, card.prof])
    synergy = choice(list(choices))
    threshold += EASY_RACE_SYNERGY_THRESHOLD if isinstance(synergy, Race) else EASY_PROF_SYNERGY_THRESHOLD

    def calc_synergy_strength(self, ageIdx, deck, oppDeck):
        if self.strength[ageIdx] == 0:
            return 0
        if synergy_count(deck, synergy) >= threshold:
            return self.strength[ageIdx] + self.age.value
        return self.strength[ageIdx]
    card.calc = calc_synergy_strength
    card.synergy = synergy
    card.desc = f'{threshold}+ {synergy.name.lower().capitalize()} for +{card.age.value}str'


def generate_hard_synergy(card, matching):
    choices = set([])
    threshold = 0
    if matching:
        card.mod = Mod.HARD_MATCHING_SYNERGY
        choices = set([card.race, card.prof])
        threshold = 1
    else:
        card.mod = Mod.HARD_NONMATCHING_SYNERGY
        choices = set(Race) | set(USEFUL_PROFS) - set([card.race, card.prof])
    synergy = choice(list(choices))
    threshold += HARD_RACE_SYNERGY_THRESHOLD if isinstance(synergy, Race) else HARD_PROF_SYNERGY_THRESHOLD

    def calc_synergy_strength(self, ageIdx, deck, oppDeck):
        if self.strength[ageIdx] == 0:
            return 0
        if synergy_count(deck, synergy) >= threshold:
            return self.strength[ageIdx] + 1 + ceil(self.age.value * 1.5)
        return self.strength[ageIdx]
    card.calc = calc_synergy_strength
    card.synergy = synergy
    card.desc = f'{threshold}+ {synergy.name.lower().capitalize()} for +{1 + ceil(card.age.value * 1.5)}str'


# how do counters work? Are they unbounded? Are they based on counts?
def generate_counter(card):
    card.mod = Mod.COUNTER
    card.strength = _weaken(card.strength)
    counter = choice(list(Race) + USEFUL_PROFS)
    threshold = RACE_COUNTER_THRESHOLD if isinstance(counter, Race) else PROF_COUNTER_THRESHOLD

    def calc_synergy_strength(self, ageIdx, deck, oppDeck):
        if self.strength[ageIdx] == 0:
            return 0
        if synergy_count(oppDeck, counter) >= threshold:
            return self.strength[ageIdx] + 1 + ceil(self.age.value * 1.5)
        return self.strength[ageIdx]
    card.calc = calc_synergy_strength
    card.synergy = counter
    card.desc = f'facing {threshold}+ {counter.name.lower().capitalize()} for +{1 + ceil(card.age.value * 1.5)}str'


cardModOddsTable = {
    Profession.ALCHEMIST: {
        Mod.DELETE: .1,
        Mod.WEAK: .1,
        Mod.STRONG: .1,
        Mod.EASY_MATCHING_SYNERGY: .1,
        Mod.EASY_NONMATCHING_SYNERGY: .05,
        Mod.HARD_MATCHING_SYNERGY: .15,
        Mod.HARD_NONMATCHING_SYNERGY: .05,
        Mod.COUNTER: .1
    },
    Profession.BATTLETECH: {
        Mod.DELETE: .1,
        Mod.WEAK: .1,
        Mod.STRONG: .1,
        Mod.EASY_MATCHING_SYNERGY: .1,
        Mod.EASY_NONMATCHING_SYNERGY: .05,
        Mod.HARD_MATCHING_SYNERGY: .15,
        Mod.HARD_NONMATCHING_SYNERGY: .05,
        Mod.COUNTER: .1
    },
    Profession.CONJUROR: {
        Mod.DELETE: .1,
        Mod.WEAK: .1,
        Mod.STRONG: .1,
        Mod.EASY_MATCHING_SYNERGY: .1,
        Mod.EASY_NONMATCHING_SYNERGY: .05,
        Mod.HARD_MATCHING_SYNERGY: .15,
        Mod.HARD_NONMATCHING_SYNERGY: .05,
        Mod.COUNTER: .1
    },
    Profession.PROPHET: {
        Mod.DELETE: .1,
        Mod.WEAK: .1,
        Mod.STRONG: .1,
        Mod.EASY_MATCHING_SYNERGY: .1,
        Mod.EASY_NONMATCHING_SYNERGY: .05,
        Mod.HARD_MATCHING_SYNERGY: .15,
        Mod.HARD_NONMATCHING_SYNERGY: .05,
        Mod.COUNTER: .1
    },
    Profession.WOODSMAN: {
        Mod.DELETE: .1,
        Mod.WEAK: .1,
        Mod.STRONG: .1,
        Mod.EASY_MATCHING_SYNERGY: .1,
        Mod.EASY_NONMATCHING_SYNERGY: .05,
        Mod.HARD_MATCHING_SYNERGY: .15,
        Mod.HARD_NONMATCHING_SYNERGY: .05,
        Mod.COUNTER: .1
    },
    Profession.PEASANT: {
        Mod.WEAK: .2
    }
}


def modify_card(card, mod):
    if mod == Mod.STRONG:
        # stronger card
        card.mod = Mod.STRONG
        card.strength = list(map(lambda str: str + card.age.value if str > 0 else 0, card.strength))
        card.desc = 'strong'
    if mod == Mod.WEAK:
        # stronger card
        card.mod = Mod.WEAK
        card.strength = _weaken(card.strength)
        card.desc = 'weak'
    elif mod == Mod.EASY_MATCHING_SYNERGY:
        # easy matching synergy
        generate_easy_synergy(card, True)
    elif mod == Mod.EASY_NONMATCHING_SYNERGY:
        # easy non-matching synergy
        generate_easy_synergy(card, False)
    elif mod == Mod.HARD_MATCHING_SYNERGY:
        # hard matching synergy
        generate_hard_synergy(card, True)
    elif mod == Mod.HARD_NONMATCHING_SYNERGY:
        # hard non-matching synergy
        generate_hard_synergy(card, False)
    elif mod == Mod.COUNTER:
        # counter
        generate_counter(card)
    else:
        card.mod = mod


def generate_pool():
    pool = generate_basic_pool()
    for card in pool:
        r = random()
        currentOdds = 0
        for mod, odds in cardModOddsTable[card.prof].items():
            currentOdds += odds
            if r < currentOdds:
                modify_card(card, mod)
                break
    return [c for c in pool if c.mod != Mod.DELETE]
