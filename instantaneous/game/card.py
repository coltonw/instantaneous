from enum import Enum, auto
from math import ceil
from random import random, choice
from functools import reduce

from instantaneous.proto import cardpool_pb2


class Age(Enum):
    STONE = 1
    IRON = 2
    CRYSTAL = 4

    def to_proto(self):
        if self is Age.STONE:
            return cardpool_pb2.Card.STONE
        if self is Age.IRON:
            return cardpool_pb2.Card.IRON
        if self is Age.CRYSTAL:
            return cardpool_pb2.Card.CRYSTAL


class Race(Enum):
    BEASTMAN = auto()
    HUMAN = auto()
    UNDEAD = auto()

    def to_proto(self):
        if self is Race.BEASTMAN:
            return cardpool_pb2.Card.BEASTMAN
        if self is Race.HUMAN:
            return cardpool_pb2.Card.HUMAN
        if self is Race.UNDEAD:
            return cardpool_pb2.Card.UNDEAD


class Profession(Enum):
    ALCHEMIST = auto()
    BATTLETECH = auto()
    CONJUROR = auto()
    PROPHET = auto()
    WOODSMAN = auto()
    PEASANT = auto()

    def to_proto(self):
        if self is Profession.ALCHEMIST:
            return cardpool_pb2.Card.ALCHEMIST
        if self is Profession.BATTLETECH:
            return cardpool_pb2.Card.BATTLETECH
        if self is Profession.CONJUROR:
            return cardpool_pb2.Card.CONJUROR
        if self is Profession.PROPHET:
            return cardpool_pb2.Card.PROPHET
        if self is Profession.WOODSMAN:
            return cardpool_pb2.Card.WOODSMAN
        if self is Profession.PEASANT:
            return cardpool_pb2.Card.PEASANT


class Phase(Enum):
    BEFORE = auto()
    EFFECT = auto()
    AFTER = auto()
    RESULT = auto()


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
    TRIGGER = auto()
    SPECIAL = auto()


class Special(Enum):
    STAIRS = auto()


USEFUL_PROFS = [prof for prof in list(Profession) if prof != Profession.PEASANT]
BASE_STRENGTH = {
    Age.STONE: [3, 3, 3],
    Age.IRON: [0, 5, 5],
    Age.CRYSTAL: [0, 0, 9]
}
EASY_PROF_SYNERGY_THRESHOLD = 6
EASY_RACE_SYNERGY_THRESHOLD = 10

HARD_PROF_SYNERGY_THRESHOLD = 9
HARD_RACE_SYNERGY_THRESHOLD = 16

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

    def to_proto(self):
        protoCard = cardpool_pb2.Card()
        protoCard.id = self.cardId
        protoCard.stone_strength = self.strength[0]
        protoCard.iron_strength = self.strength[1]
        protoCard.crystal_strength = self.strength[2]
        if self.age is not None:
            protoCard.age = self.age.to_proto()
        if self.race is not None:
            protoCard.race = self.race.to_proto()
        if self.prof is not None:
            protoCard.prof = self.prof.to_proto()
        protoCard.desc = self.desc
        if isinstance(self.synergy, Race):
            protoCard.race_synergy = self.synergy.to_proto()
        elif isinstance(self.synergy, Profession):
            protoCard.prof_synergy = self.synergy.to_proto()

        return protoCard


def generate_basic_pool():
    Card.cardId = 1
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
    else:
        card.mod = Mod.EASY_NONMATCHING_SYNERGY
        choices = set(Race) | set(USEFUL_PROFS) - set([card.race, card.prof])
        threshold = -1
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
    card.desc = f'If you have {threshold} or more {synergy.name.lower().capitalize()}, for +{card.age.value} strength'


def generate_hard_synergy(card, matching):
    card.strength = _weaken(card.strength)
    choices = set([])
    threshold = 0
    if matching:
        card.mod = Mod.HARD_MATCHING_SYNERGY
        choices = set([card.race, card.prof])
    else:
        card.mod = Mod.HARD_NONMATCHING_SYNERGY
        choices = set(Race) | set(USEFUL_PROFS) - set([card.race, card.prof])
        threshold = -1
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


def add_special_cards(pool):
    # TODO: Add a bunch more special cards and add rules for how they get added to the pool
    pool.append(Card([1, 3, 6], None, choice(list(Race)), choice(USEFUL_PROFS), desc='stair', mod=Mod.SPECIAL))
    # pool.append(Card([8, 0, 0], None, choice(list(Race)), choice(USEFUL_PROFS), desc='stone-ly', mod=Mod.SPECIAL))\
    return pool


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
    pool = [c for c in pool if c.mod != Mod.DELETE]
    return add_special_cards(pool)


def pool_to_proto(pool, id='0'):
    protoPool = cardpool_pb2.CardPool()
    protoPool.id = id
    protoCards = map(lambda card: card.to_proto(), pool)
    protoPool.cards.extend(protoCards)
    return protoPool


def combine_trigger_result(card, trigger, result):
    card.mod = Mod.TRIGGER
    card.strength = result.starting_str(card)

    if result.calc_strength is not None:
        def calc_trigger_strength(self, ageIdx, deck, oppDeck):
            if trigger.check(self, ageIdx, deck, oppDeck):
                return result.calc_strength(self, ageIdx, deck, oppDeck)
            return self.strength[ageIdx]
        card.calc = calc_trigger_strength
    card.desc = f'If {trigger.desc}, {result.desc}'


# Trigger
# difficulty 0 = easy, 1 = medium, 2 = hard
# complexity 0 = simple, 1 = sorta simple, 2 = complex
class Trigger:
    def __init__(self, desc, check, difficulty=1, complexity=1, phases=list(Phase)):
        self.desc = desc
        self.check = check
        self.difficulty = difficulty
        self.complexity = complexity
        self.phases = phases

    def __repr__(self):
        return f'Trigger({self.desc},{self.difficulty},{self.complexity},{self.phases})'

    def __str__(self):
        return repr(self)


# Result
# power 0 = weak, 1 = medium, 2 = strong
# complexity 0 = simple, 1 = sorta simple, 2 = complex
class Result:
    def __init__(self, desc, calc_strength=None, modify_deck=None, power=1, complexity=1, phases=list(Phase)):
        self.desc = desc
        self.calc_strength = calc_strength
        self.modify_deck = modify_deck
        self.power = power
        self.complexity = complexity
        self.phases = phases

    def __repr__(self):
        return f'Trigger({self.desc},{self.difficulty},{self.complexity},{self.phases})'

    def __str__(self):
        return repr(self)


def generate_easy_synergy_trigger(card):
    choices = set([])
    threshold = 0
    if random() > 0.5:
        card.mod = Mod.EASY_MATCHING_SYNERGY
        choices = set([card.race, card.prof])
    else:
        card.mod = Mod.EASY_NONMATCHING_SYNERGY
        choices = set(Race) | set(USEFUL_PROFS) - set([card.race, card.prof])
        threshold = -1
    synergy = choice(list(choices))
    threshold += EASY_RACE_SYNERGY_THRESHOLD if isinstance(synergy, Race) else EASY_PROF_SYNERGY_THRESHOLD

    def check(self, ageIdx, deck, oppDeck):
        return synergy_count(deck, synergy) >= threshold

    return Trigger(f"you have at least {threshold} {synergy.name.capitalize()}s", check)
