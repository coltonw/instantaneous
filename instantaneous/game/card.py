from enum import Enum, auto
from math import ceil
import random
import sys
import copy
from functools import reduce

from instantaneous.game.constants import (Age, Profession, Race, Phase, Mod, Special, USEFUL_PROFS, BASE_STRENGTH,
                                          POWER_ADVANTAGE,
                                          EASY_PROF_SYNERGY_THRESHOLD, EASY_RACE_SYNERGY_THRESHOLD,
                                          HARD_PROF_SYNERGY_THRESHOLD, HARD_RACE_SYNERGY_THRESHOLD,
                                          PROF_COUNTER_THRESHOLD, RACE_COUNTER_THRESHOLD,
                                          CRYSTAL_SYNERGY_THRESHOLD, HARD_VARIETY_THRESHOLD,
                                          EASY_VARIETY_THRESHOLD, HARD_DIVERSITY_THRESHOLD,
                                          EASY_DIVERSITY_THRESHOLD, DECK_SIZE)

from instantaneous.proto import cardpool_pb2


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
        protoCard.iron_strength = self.strength[0]
        protoCard.crystal_strength = self.strength[1]
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
                pool.append(Card(strength, age, race, prof))
                if age != Age.CRYSTAL:
                    pool.append(Card(strength, age, race, prof))
    return pool


def _weaken(strength):
    return [s - 1 if s > 0 else 0 for s in strength]


def _strengthen(strength, power=1, age=None):
    value = POWER_ADVANTAGE[power]
    if age is Age.IRON:
        value = int(value / 2)
    return [s + value if s > 0 else 0 for s in strength]


cardModOddsTable = {
    Profession.ALCHEMIST: {
        Mod.DELETE: .1,
        Mod.WEAK: .1,
        Mod.STRONG: .1,
        Mod.TRIGGER: .5
    },
    Profession.BATTLETECH: {
        Mod.DELETE: .1,
        Mod.WEAK: .1,
        Mod.STRONG: .1,
        Mod.TRIGGER: .5
    },
    Profession.CONJUROR: {
        Mod.DELETE: .1,
        Mod.WEAK: .1,
        Mod.STRONG: .1,
        Mod.TRIGGER: .5
    },
    Profession.PROPHET: {
        Mod.DELETE: .1,
        Mod.WEAK: .1,
        Mod.STRONG: .1,
        Mod.TRIGGER: .5
    },
    Profession.WOODSMAN: {
        Mod.DELETE: .1,
        Mod.WEAK: .1,
        Mod.STRONG: .1,
        Mod.TRIGGER: .5
    },
    Profession.PEASANT: {
        Mod.WEAK: .2
    }
}


def modify_card(card, mod):
    if mod == Mod.STRONG:
        # stronger card
        card.mod = Mod.STRONG
        card.strength = _strengthen(card.strength, age=card.age)
        card.desc = 'Strong'
    if mod == Mod.WEAK:
        # weaker card
        card.mod = Mod.WEAK
        card.strength = _weaken(card.strength)
        card.desc = 'Weak'
    elif mod == Mod.TRIGGER:
        generate_trigger_result(card)
    else:
        card.mod = mod


def add_special_cards(pool):
    # TODO: Add a bunch more special cards and add rules for how they get added to the pool
    pool.append(Card([3, 6], None, random.choice(list(Race)), random.choice(USEFUL_PROFS), desc='stair', mod=Mod.SPECIAL))
    # pool.append(Card([7, 0], None, random.choice(list(Race)), random.choice(USEFUL_PROFS), desc='iron-only', mod=Mod.SPECIAL))
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
    protoPool.deck_size = DECK_SIZE
    return protoPool


class Effect:
    def __init__(self, check, apply, phase, interactive, cardId, name=''):
        self.checkFn = check
        self.applyFn = apply
        self.phase = phase
        self.interactive = interactive
        self.cardId = cardId
        self.name = name

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
    def __init__(self, name, hydrate, difficulty=1, complexity=1, phases=set(Phase), interactive=False):
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
    def __init__(self, name, hydrate, power=1, complexity=1, phases=set(Phase), interactive=False):
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


def combine_trigger_result(card, trigger, result, phase=Phase.EFFECT, interactive=False, name=''):
    if card.mod is Mod.NORMAL:
        card.mod = Mod.TRIGGER
    if result.starting_str is not None:
        card.strength = result.starting_str(card)

    if result.apply is not None:
        effect = Effect(check=trigger.check, apply=result.apply, phase=phase,
                        interactive=interactive, cardId=card.cardId, name=name)
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

    return Trigger(f"you have at least {threshold} {synergy.plural().capitalize()}", check)


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

    return Trigger(f"you have at least {threshold} {synergy.plural().capitalize()}", check)


def hydrate_counter_trigger(card):
    rand = random.Random(card.triggerSeed)
    card.mod = Mod.COUNTER
    counter = rand.choice(list(Race) + USEFUL_PROFS)
    threshold = RACE_COUNTER_THRESHOLD if isinstance(counter, Race) else PROF_COUNTER_THRESHOLD
    card.synergy = counter

    def check(self, deck, oppDeck):
        return oppDeck['count'][counter] >= threshold
    return Trigger(f"your opponent has at least {threshold} {counter.plural().capitalize()}", check)


def hydrate_crystal_synergy_trigger(card):
    def check(self, deck, oppDeck):
        return deck['count'][Age.CRYSTAL] >= CRYSTAL_SYNERGY_THRESHOLD
    return Trigger(f"you have at least {CRYSTAL_SYNERGY_THRESHOLD} 0|X cards", check)


def hydrate_variety_trigger(card):
    def check(self, deck, oppDeck):
        for p in Profession:
            if deck['count'][p] < EASY_VARIETY_THRESHOLD:
                return False
        return True
    return Trigger(f"you have every profession", check)


def hydrate_hard_variety_trigger(card):
    def check(self, deck, oppDeck):
        for p in Profession:
            if deck['count'][p] < HARD_VARIETY_THRESHOLD:
                return False
        return True
    return Trigger(f"you have at least {HARD_VARIETY_THRESHOLD} of every profession", check)


def hydrate_diversity_trigger(card):
    def check(self, deck, oppDeck):
        for r in Race:
            if deck['count'][r] < EASY_DIVERSITY_THRESHOLD:
                return False
        return True
    return Trigger(f"you have at least {EASY_DIVERSITY_THRESHOLD} of every race", check)


def hydrate_hard_diversity_trigger(card):
    def check(self, deck, oppDeck):
        for r in Race:
            if deck['count'][r] < HARD_DIVERSITY_THRESHOLD:
                return False
        return True
    return Trigger(f"you have at least {HARD_DIVERSITY_THRESHOLD} of every race", check)


def hydrate_attacker_trigger(card):
    def check(self, deck, oppDeck):
        return deck['total'][0] > oppDeck['total'][0]
    return Trigger(f"you are winning the first age", check)


def hydrate_defender_trigger(card):
    def check(self, deck, oppDeck):
        return deck['total'][0] < oppDeck['total'][0]
    return Trigger(f"you are losing the first age", check)


def hydrate_close_defender_trigger(card):
    def check(self, deck, oppDeck):
        return deck['total'][0] < oppDeck['total'][0] and oppDeck['total'][0] - deck['total'][0] < 30
    return Trigger(f"you are losing the first age by less than 30", check)


triggerTypes = [
    TriggerType("easy_synergy", hydrate_easy_synergy_trigger),
    TriggerType("hard_synergy", hydrate_hard_synergy_trigger, difficulty=3),
    TriggerType("counter", hydrate_counter_trigger, difficulty=3, interactive=True),
    TriggerType("crystal_synergy", hydrate_crystal_synergy_trigger, difficulty=3),
    TriggerType("variety", hydrate_variety_trigger),
    TriggerType("hard_variety", hydrate_hard_variety_trigger, difficulty=2),
    TriggerType("diversity", hydrate_diversity_trigger),
    TriggerType("hard_diversity", hydrate_hard_diversity_trigger, difficulty=2),
    TriggerType("attacker", hydrate_attacker_trigger, phases={Phase.RESULT}, interactive=True),
    TriggerType("defender", hydrate_defender_trigger, phases={Phase.RESULT}, interactive=True),
    TriggerType("close_ defender", hydrate_close_defender_trigger,
                phases={Phase.RESULT}, difficulty=2, interactive=True)
]


###########
# RESULTS #
###########


def hydrate_strong_result(card):
    # not needed here but sometimes is needed
    # rand = random.Random(card.resultSeed)

    value = POWER_ADVANTAGE[1]
    valueStr = str(value)
    if card.age == Age.IRON:
        value = int(value / 2)
        valueStr = f"{value} | {value}"

    def apply(self, deck, oppDeck):
        for ageIdx in range(2):
            if deck[self.cardId].strength[ageIdx] > 0:
                deck[self.cardId].strength[ageIdx] += value
                deck['total'][ageIdx] += value

    return Result(f"gain {valueStr} strength", apply=apply)


def hydrate_verystrong_result(card):
    # not needed here but sometimes is needed
    # rand = random.Random(card.resultSeed)

    value = POWER_ADVANTAGE[2]
    valueStr = str(value)
    if card.age is Age.IRON:
        value = int(value / 2)
        valueStr = f"{value} | {value}"

    def apply(self, deck, oppDeck):
        for ageIdx in range(2):
            if deck[self.cardId].strength[ageIdx] > 0:
                deck[self.cardId].strength[ageIdx] += value
                deck['total'][ageIdx] += value

    return Result(f"gain {valueStr} strength", apply=apply)


def hydrate_ultrastrong_lowstart_result(card):
    # not needed here but sometimes is needed
    # rand = random.Random(card.resultSeed)

    def starting_str(c):
        return _weaken(c.strength)

    value = POWER_ADVANTAGE[3] + 1
    valueStr = str(value)
    if card.age is Age.IRON:
        value = int(POWER_ADVANTAGE[3] / 2) + 1
        valueStr = f"{value} | {value}"

    def apply(self, deck, oppDeck):
        for ageIdx in range(2):
            if deck[self.cardId].strength[ageIdx] > 0:
                deck[self.cardId].strength[ageIdx] += value
                deck['total'][ageIdx] += value

    return Result(f"gain {valueStr} strength", apply=apply, starting_str=starting_str)


resultTypes = [
    ResultType("strong", hydrate_strong_result, complexity=0),
    ResultType("verystrong", hydrate_verystrong_result, power=2, complexity=0),
    ResultType("ultrastrong_lowstart", hydrate_ultrastrong_lowstart_result, power=3)
]


def generate_trigger_result(card, difficulty=None):
    filteredTriggerTypes = triggerTypes
    if difficulty is not None:
        filteredTriggerTypes = list(filter(lambda tt: tt.difficulty == difficulty, triggerTypes))
    triggerType = random.choice(filteredTriggerTypes)
    # TODO: make this wiggle occasionally
    filteredResultTypes = list(filter(lambda rt: rt.power == triggerType.difficulty and len(rt.phases & triggerType.phases) > 0, resultTypes))
    resultType = random.choice(filteredResultTypes)

    card.triggerSeed = random.randrange(sys.maxsize)
    trigger = triggerType.hydrate(card)

    card.resultSeed = random.randrange(sys.maxsize)
    result = resultType.hydrate(card)

    possiblePhases = triggerType.phases & resultType.phases
    phase = Phase.EFFECT
    if Phase.EFFECT not in possiblePhases:
        for p in Phase:
            if p in possiblePhases:
                phase = p
                break

    combine_trigger_result(card, trigger, result, phase=phase,
                           interactive=triggerType.interactive or resultType.interactive,
                           name=f'{triggerType.name}-{resultType.name}')
