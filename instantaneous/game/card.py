from enum import Enum, auto
from math import ceil
import random
import sys
import copy
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

CRYSTAL_SYNERGY_THRESHOLD = 12


class Card:
    cardId = 1

    def __init__(self, strength, age, race, prof, desc='', mod=Mod.NORMAL,
                 synergy=None, effects=None, cardId=None):
        if cardId is None:
            self.cardId = Card.cardId
            Card.cardId += 1
        else:
            self.cardId = cardId
        self.strength = strength
        self.age = age
        self.race = race
        self.prof = prof
        self.desc = desc
        self.mod = mod
        self.synergy = synergy
        if effects is None:
            self.effects = []
        else:
            self.effects = effects

    def __repr__(self):
        return f'Card({self.strength},{self.age},{self.race},{self.prof},{self.desc})'

    def __str__(self):
        return repr(self)

    def __copy__(self):
        return Card(strength=self.strength, age=self.age, race=self.race,
                    prof=self.prof, desc=self.desc, mod=self.mod,
                    synergy=self.synergy, effects=self.effects,
                    cardId=self.cardId)

    def __deepcopy__(self, memodict={}):
        return Card(strength=copy.deepcopy(self.strength), age=self.age, race=self.race,
                    prof=self.prof, desc=self.desc, mod=self.mod,
                    synergy=self.synergy, effects=copy.deepcopy(self.effects),
                    cardId=self.cardId)

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
    elif mod == Mod.EASY_MATCHING_SYNERGY or mod == Mod.EASY_NONMATCHING_SYNERGY:
        # easy matching synergy
        generate_trigger_result(card, difficulty=1)
    elif mod == Mod.HARD_MATCHING_SYNERGY or mod == Mod.HARD_NONMATCHING_SYNERGY:
        # hard matching synergy
        generate_trigger_result(card, difficulty=2)
    elif mod == Mod.COUNTER:
        # counter
        generate_trigger_result(card, difficulty=2)
    else:
        card.mod = mod


def add_special_cards(pool):
    # TODO: Add a bunch more special cards and add rules for how they get added to the pool
    pool.append(Card([1, 3, 6], None, random.choice(list(Race)), random.choice(USEFUL_PROFS), desc='stair', mod=Mod.SPECIAL))
    # pool.append(Card([8, 0, 0], None, random.choice(list(Race)), random.choice(USEFUL_PROFS), desc='stone-ly', mod=Mod.SPECIAL))\
    return pool


def generate_pool():
    pool = generate_basic_pool()
    for card in pool:
        r = random.random()
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


class Effect:
    def __init__(self, check, apply, phase, interactive, cardId):
        self.checkFn = check
        self.applyFn = apply
        self.phase = phase
        self.interactive = interactive
        self.cardId = cardId

    def check(self, deckMetadata, oppDeckMetadata):
        return self.checkFn(self, deckMetadata, oppDeckMetadata)

    def apply(self, deckMetadata, oppDeckMetadata):
        self.applyFn(self, deckMetadata, oppDeckMetadata)


class Trigger:
    def __init__(self, desc, check):
        self.desc = desc
        self.check = check

    def __repr__(self):
        return f'Trigger({self.desc})'

    def __str__(self):
        return repr(self)


class Result:
    def __init__(self, desc, apply=None, starting_str=None):
        self.desc = desc
        self.apply = apply
        self.starting_str = starting_str

    def __repr__(self):
        return f'Result({self.desc})'

    def __str__(self):
        return repr(self)


# TriggerType
# difficulty 0 = easy, 1 = medium, 2 = hard
# complexity 0 = simple, 1 = sorta simple, 2 = complex
# hydrate should generate a Trigger which is always the same given the same card.triggerSeed
class TriggerType:
    def __init__(self, name, hydrate, difficulty=1, complexity=1, phases=list(Phase), interactive=False):
        self.name = name
        self.hydrate = hydrate
        self.difficulty = difficulty
        self.complexity = complexity
        self.phases = phases
        self.interactive = interactive

    def __repr__(self):
        return f'TriggerType({self.name},{self.difficulty},{self.complexity},{self.phases},{self.interactive})'

    def __str__(self):
        return repr(self)


# ResultType
# power 0 = weak, 1 = medium, 2 = strong
# complexity 0 = simple, 1 = sorta simple, 2 = complex
# hydrate should generate a Result which is always the same given the same card.resultSeed
class ResultType:
    def __init__(self, name, hydrate, power=1, complexity=1, phases=list(Phase), interactive=False):
        self.name = name
        self.hydrate = hydrate
        self.power = power
        self.complexity = complexity
        self.phases = phases
        self.interactive = interactive

    def __repr__(self):
        return f'ResultType({self.name},{self.power},{self.complexity},{self.phases},{self.interactive})'

    def __str__(self):
        return repr(self)


def combine_trigger_result(card, trigger, result, phase=Phase.EFFECT, interactive=False):
    if card.mod is Mod.NORMAL:
        card.mod = Mod.TRIGGER
    if result.starting_str is not None:
        card.strength = result.starting_str(card)

    if result.apply is not None:
        effect = Effect(check=trigger.check, apply=result.apply, phase=phase, interactive=interactive, cardId=card.cardId)
        card.effects.append(effect)
    card.desc = f'If {trigger.desc}, {result.desc}'


############
# TRIGGERS #
############


def hydrate_easy_synergy_trigger(card):
    rand = random.Random(card.triggerSeed)
    choices = set([])
    threshold = 0
    if rand.random() < 0.66:
        card.mod = Mod.EASY_MATCHING_SYNERGY
        choices = set([card.race, card.prof])
    else:
        card.mod = Mod.EASY_NONMATCHING_SYNERGY
        choices = set(Race) | set(USEFUL_PROFS) - set([card.race, card.prof])
        threshold = -1
    synergy = rand.choice(list(choices))
    threshold += EASY_RACE_SYNERGY_THRESHOLD if isinstance(synergy, Race) else EASY_PROF_SYNERGY_THRESHOLD
    card.synergy = synergy

    def check(self, deck, oppDeck):
        return deck['count'][synergy] >= threshold

    return Trigger(f"you have at least {threshold} {synergy.name.capitalize()}s", check)


def hydrate_hard_synergy_trigger(card):
    rand = random.Random(card.triggerSeed)
    choices = set([])
    threshold = 0
    if rand.random() < 0.75:
        card.mod = Mod.HARD_MATCHING_SYNERGY
        choices = set([card.race, card.prof])
    else:
        card.mod = Mod.HARD_NONMATCHING_SYNERGY
        choices = set(Race) | set(USEFUL_PROFS) - set([card.race, card.prof])
        threshold = -1
    synergy = rand.choice(list(choices))
    threshold += HARD_RACE_SYNERGY_THRESHOLD if isinstance(synergy, Race) else HARD_PROF_SYNERGY_THRESHOLD
    card.synergy = synergy

    def check(self, deck, oppDeck):
        return deck['count'][synergy] >= threshold

    return Trigger(f"you have at least {threshold} {synergy.name.capitalize()}s", check)


# how do counters work? Are they unbounded? Are they based on counts?
# def hydrate_counter_trigger(card):
#     rand = random.Random(card.triggerSeed)
#     card.mod = Mod.COUNTER
#     counter = rand.choice(list(Race) + USEFUL_PROFS)
#     threshold = RACE_COUNTER_THRESHOLD if isinstance(counter, Race) else PROF_COUNTER_THRESHOLD
#     card.synergy = counter

#     def check(self, ageIdx, deck, oppDeck):
#         return synergy_count(oppDeck, counter) >= threshold
#     return Trigger(f"your opponent has at least {threshold} {counter.name.capitalize()}s", check)


# def hydrate_crystal_synergy_trigger(card):
#     def check(self, ageIdx, deck, oppDeck):
#         numCrystal = sum([card.age is Age.CRYSTAL for card in deck])
#         return numCrystal >= CRYSTAL_SYNERGY_THRESHOLD
#     return Trigger(f"you have at least {CRYSTAL_SYNERGY_THRESHOLD} 0|0|X cards", check)


# def hydrate_variety_trigger(card):
#     def check(self, ageIdx, deck, oppDeck):
#         numProfTypes = {card.prof for card in deck}
#         return numProfTypes == len(Profession)
#     return Trigger(f"you have every profession", check)


# def hydrate_hard_variety_trigger(card):
#     def check(self, ageIdx, deck, oppDeck):
#         profCounts = {}
#         for c in deck:
#             if c.prof in profCounts:
#                 profCounts[c.prof] = 1 + profCounts[c.prof]
#             else:
#                 profCounts[c.prof] = 1
#         for p in Profession:
#             if p not in profCounts or profCounts[p] < 2:
#                 return False
#         return True
#     return Trigger(f"you have at least 2 of every profession", check)


# def hydrate_diversity_trigger(card):
#     def check(self, ageIdx, deck, oppDeck):
#         raceCounts = {}
#         for c in deck:
#             if c.race in raceCounts:
#                 raceCounts[c.race] = 1 + raceCounts[c.race]
#             else:
#                 raceCounts[c.race] = 1
#         for r in Race:
#             if r not in raceCounts or raceCounts[r] < 2:
#                 return False
#         return True
#     return Trigger(f"you have at least 2 of every race", check)


# def hydrate_hard_diversity_trigger(card):
#     def check(self, ageIdx, deck, oppDeck):
#         raceCounts = {}
#         for c in deck:
#             if c.race in raceCounts:
#                 raceCounts[c.race] = 1 + raceCounts[c.race]
#             else:
#                 raceCounts[c.race] = 1
#         for r in Race:
#             if r not in raceCounts or raceCounts[r] < 4:
#                 return False
#         return True
#     return Trigger(f"you have at least 4 of every race", check)


triggerTypes = [
    TriggerType("easy_synergy", hydrate_easy_synergy_trigger),
    TriggerType("hard_synergy", hydrate_hard_synergy_trigger, difficulty=2),
    # TriggerType("counter", hydrate_counter_trigger, difficulty=2),
    # TriggerType("crystal_synergy", hydrate_crystal_synergy_trigger, difficulty=2),
    # TriggerType("variety", hydrate_variety_trigger),
    # TriggerType("hard_variety", hydrate_hard_variety_trigger, difficulty=2),
    # TriggerType("diversity", hydrate_diversity_trigger),
    # TriggerType("hard_diversity", hydrate_hard_diversity_trigger)
]


###########
# RESULTS #
###########


def hydrate_strong_result(card):
    # not needed here but sometimes is needed
    # rand = random.Random(card.resultSeed)

    def apply(self, deck, oppDeck):
        for ageIdx in range(3):
            if deck[self.cardId].strength[ageIdx] > 0:
                deck[self.cardId].strength[ageIdx] += card.age.value
                deck['total'][ageIdx] += card.age.value

    return Result(f"gain {card.age.value} strength", apply=apply)


def hydrate_ultrastrong_lowstart_result(card):
    # not needed here but sometimes is needed
    # rand = random.Random(card.resultSeed)

    def starting_str(c):
        return _weaken(c.strength)

    def apply(self, deck, oppDeck):
        for ageIdx in range(3):
            if deck[self.cardId].strength[ageIdx] > 0:
                deck[self.cardId].strength[ageIdx] += 1 + ceil(card.age.value * 1.5)
                deck['total'][ageIdx] += 1 + ceil(card.age.value * 1.5)

    return Result(f"gain {1 + ceil(card.age.value * 1.5)} strength", apply=apply, starting_str=starting_str)


resultTypes = [
    ResultType("strong", hydrate_strong_result, complexity=0),
    ResultType("ultrastrong_lowstart", hydrate_ultrastrong_lowstart_result, power=2)
]


def generate_trigger_result(card, difficulty=None):
    filteredTriggerTypes = triggerTypes
    if difficulty is not None:
        filteredTriggerTypes = list(filter(lambda tt: tt.difficulty == difficulty, triggerTypes))
    triggerType = random.choice(filteredTriggerTypes)
    # TODO: make this wiggle occasionally
    filteredResultTypes = list(filter(lambda rt: rt.power == triggerType.difficulty, resultTypes))
    resultType = random.choice(filteredResultTypes)

    card.triggerSeed = random.randrange(sys.maxsize)
    trigger = triggerType.hydrate(card)

    card.resultSeed = random.randrange(sys.maxsize)
    result = resultType.hydrate(card)
    combine_trigger_result(card, trigger, result, interactive=triggerType.interactive or resultType.interactive)
