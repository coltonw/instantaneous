import random
import sys
import copy
import uuid

from icg.constants import (Age, Profession, Race, Phase, Mod, Special, USEFUL_PROFS, BASE_STRENGTH,
                           EASY_PROF_SYNERGY_THRESHOLD, EASY_RACE_SYNERGY_THRESHOLD,
                           HARD_PROF_SYNERGY_THRESHOLD, HARD_RACE_SYNERGY_THRESHOLD,
                           PROF_COUNTER_THRESHOLD, RACE_COUNTER_THRESHOLD,
                           CRYSTAL_SYNERGY_THRESHOLD, HARD_VARIETY_THRESHOLD,
                           EASY_VARIETY_THRESHOLD, HARD_DIVERSITY_THRESHOLD,
                           EASY_DIVERSITY_THRESHOLD, DECK_SIZE, phase_from_proto,
                           age_from_proto, race_from_proto, prof_from_proto)

from icg.proto import cardpool_pb2


class Card:
    cardId = 1

    def __init__(self, strength, age, race, prof, desc='', mod=Mod.NORMAL,
                 synergy=None, effects=None, cardId=None, useUuid=False):
        if cardId is None and useUuid:
            self.cardId = str(uuid.uuid4())
        elif cardId is None and not useUuid:
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

    def to_proto(self, complete=False):
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
        if complete:
            for effect in self.effects:
                protoEffect = protoCard.effects.add()
                if effect.triggerName is not None:
                    protoEffect.trigger_name = effect.triggerName
                if effect.triggerSeed is not None:
                    protoEffect.trigger_seed = effect.triggerSeed
                if effect.resultName is not None:
                    protoEffect.result_name = effect.resultName
                if effect.resultSeed is not None:
                    protoEffect.result_seed = effect.resultSeed

        return protoCard


def card_from_proto(protoCard):
    synergy = None
    if protoCard.race_synergy is not cardpool_pb2.Card.NONE_RACE:
        synergy = race_from_proto(protoCard.race_synergy)
    elif protoCard.prof_synergy is not cardpool_pb2.Card.NONE_PROF:
        synergy = prof_from_proto(protoCard.prof_synergy)
    card = Card([protoCard.iron_strength, protoCard.crystal_strength], age_from_proto(protoCard.age),
                race_from_proto(protoCard.race), prof_from_proto(protoCard.prof), desc=protoCard.desc,
                synergy=synergy, cardId=protoCard.id)
    hydrate_effects_from_proto(card, protoCard)

    return card


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
    value = power * 2
    if age is Age.IRON:
        value = power
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


def pool_from_proto(protoPool):
    return [card_from_proto(c) for c in protoPool.cards]


class Effect:
    def __init__(self, check, apply, phase, interactive, cardId, name='',
                 triggerName=None, triggerSeed=None, resultName=None,
                 resultSeed=None):
        self.checkFn = check
        self.applyFn = apply
        self.phase = phase
        self.interactive = interactive
        self.cardId = cardId
        self.name = name
        self.triggerName = triggerName
        self.triggerSeed = triggerSeed
        self.resultName = resultName
        self.resultSeed = resultSeed

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
    def __init__(self, name, hydrate, difficulty=1, complexity=1, weight=1, phases=set(Phase), preferredPhase=None, interactive=False):
        self.name = name
        self.hydrate = hydrate
        self.difficulty = difficulty
        self.complexity = complexity
        self.weight = weight
        self.phases = phases
        self.preferredPhase = preferredPhase
        self.interactive = interactive

    def __repr__(self):
        return f'TriggerType({self.name},{self.difficulty},{self.complexity},{self.weight},{self.phases},{self.preferredPhase},{self.interactive})'

    def __str__(self):
        return repr(self)


# ResultType
# each power is ~equivalent to adding 2 strength to a card
# complexity 0 = simple, 1 = sorta simple, 2 = complex
# hydrate should generate a Result which is always the same given the same card.resultSeed
class ResultType:
    def __init__(self, name, hydrate, minPower=1, maxPower=sys.maxsize, complexity=1, weight=1, phases=set(Phase), preferredPhase=None, interactive=False):
        self.name = name
        self.hydrate = hydrate
        self.minPower = minPower
        self.maxPower = maxPower
        self.complexity = complexity
        self.weight = weight
        self.phases = phases
        self.preferredPhase = preferredPhase
        self.interactive = interactive

    def __repr__(self):
        return f'ResultType({self.name},{self.minPower},{self.maxPower},{self.complexity},{self.phases},{self.preferredPhase},{self.interactive})'

    def __str__(self):
        return repr(self)


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
        # this -1 is a bit confusing while adding very little. Considering removing it
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
        # this -1 is a bit confusing while adding very little. Considering removing it
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


def hydrate_exact_synergy_trigger(card):
    rand = random.Random(card.triggerSeed)
    choices = list(Race) + USEFUL_PROFS
    synergy = rand.choice(choices)
    maxTarget = 3 if synergy is isinstance(card.synergy, Profession) else 5
    target = rand.randint(1, maxTarget)
    card.synergy = synergy

    def check(self, deck, oppDeck):
        return deck['count'][synergy] == target

    return Trigger(f"you have exactly {target} {synergy.plural().capitalize() if target > 1 else synergy.name.capitalize()}", check)


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
        return deck['total'][0] < oppDeck['total'][0] and oppDeck['total'][0] - deck['total'][0] < 25
    return Trigger(f"you are losing the first age by less than 25", check)


# TODO: possibly add limits
triggerTypes = [
    TriggerType("easy_synergy", hydrate_easy_synergy_trigger),
    TriggerType("hard_synergy", hydrate_hard_synergy_trigger, difficulty=3),
    TriggerType("counter", hydrate_counter_trigger, difficulty=3, interactive=True),
    TriggerType("crystal_synergy", hydrate_crystal_synergy_trigger, difficulty=3),
    TriggerType("exact_synergy", hydrate_exact_synergy_trigger, difficulty=2, weight=.5),
    TriggerType("variety", hydrate_variety_trigger),
    TriggerType("hard_variety", hydrate_hard_variety_trigger, difficulty=2, weight=.5),
    TriggerType("diversity", hydrate_diversity_trigger),
    TriggerType("hard_diversity", hydrate_hard_diversity_trigger, difficulty=2, weight=.5),
    TriggerType("attacker", hydrate_attacker_trigger, weight=1.8, phases={Phase.RESULT}, interactive=True),
    TriggerType("defender", hydrate_defender_trigger, weight=1.2, phases={Phase.RESULT}, interactive=True),
    TriggerType("close_defender", hydrate_close_defender_trigger, weight=1.8,
                phases={Phase.RESULT}, difficulty=2, interactive=True, complexity=2)
]


# TODO: complex triggers which have built in results as part of the trigger
# e.g. Destroy all your Prophets. If at least 3 were destroyed, RESULT


###########
# RESULTS #
###########


# TODO: Results should mostly be variable with maybe a minPower but can take a power input


def hydrate_strength_result(card, power):
    # not needed here but sometimes is needed
    # rand = random.Random(card.resultSeed)

    value = power * 2
    valueStr = str(value)
    if card.age == Age.IRON:
        value = power
        valueStr = f"{value} | {value}"

    def apply(self, deck, oppDeck):
        for ageIdx in range(2):
            if deck['cards'][self.cardId].strength[ageIdx] > 0:
                deck['cards'][self.cardId].strength[ageIdx] += value
                deck['total'][ageIdx] += value

    return Result(f"gain {valueStr} strength", apply=apply)


def hydrate_strength_lowstart_result(card, power):
    # not needed here but sometimes is needed
    # rand = random.Random(card.resultSeed)

    def starting_str(c):
        return _weaken(c.strength)

    value = power * 2 + 1
    valueStr = str(value)
    if card.age is Age.IRON:
        value = power + 1
        valueStr = f"{value} | {value}"

    def apply(self, deck, oppDeck):
        for ageIdx in range(2):
            if deck['cards'][self.cardId].strength[ageIdx] > 0:
                deck['cards'][self.cardId].strength[ageIdx] += value
                deck['total'][ageIdx] += value

    return Result(f"gain {valueStr} strength", apply=apply, starting_str=starting_str)


def hydrate_spawn_result(card, power):
    # not needed here but sometimes is needed
    # rand = random.Random(card.resultSeed)

    value = power * 2
    valueStr = str(value)

    def apply(self, deck, oppDeck):
        spawn = Card([0, value], Age.CRYSTAL, card.race, card.prof, useUuid=True)
        deck['cards'][spawn.cardId] = spawn
        deck['total'][1] += value

    return Result(f"create a 0 | {valueStr} {card.race.name.capitalize()} {card.prof.name.capitalize()}", apply=apply)


def hydrate_mirror_iron_result(card, power):
    # not needed here but sometimes is needed
    # rand = random.Random(card.resultSeed)

    def apply(self, deck, oppDeck):
        maxStr = 0
        for card in deck['cards'].values():
            if card.strength[0] == card.strength[1] and card.strength[0] > maxStr:
                maxStr = card.strength[0]
        if maxStr > 0:
            strDiff = maxStr - deck['cards'][self.cardId].strength[0]
            deck['cards'][self.cardId].strength[0] = maxStr
            deck['total'][0] += strDiff
            strDiff = maxStr - deck['cards'][self.cardId].strength[1]
            deck['cards'][self.cardId].strength[1] = maxStr
            deck['total'][1] += strDiff

    return Result(f"copy the strength of your biggest X|X card", apply=apply)


def hydrate_mirror_crystal_result(card, power):
    # not needed here but sometimes is needed
    # rand = random.Random(card.resultSeed)

    def apply(self, deck, oppDeck):
        maxStr = 0
        for card in deck['cards'].values():
            if card.strength[0] == 0 and card.strength[1] > maxStr:
                maxStr = card.strength[1]
        if maxStr > 0:
            deck['cards'][self.cardId].strength[0] = 0
            deck['total'][0] -= deck['cards'][self.cardId].strength[0]
            strDiff = maxStr - deck['cards'][self.cardId].strength[1]
            deck['cards'][self.cardId].strength[1] = maxStr
            deck['total'][1] += strDiff

    return Result(f"copy the strength of your biggest 0|X card", apply=apply)


def hydrate_weaken_opponent_army_result(card, power):
    # not needed here but sometimes is needed
    # rand = random.Random(card.resultSeed)

    value = power * 2
    valueStr = str(value)

    def apply(self, deck, oppDeck):
        oppDeck['total'][1] -= value

    return Result(f"weaken the opponent's army by {valueStr} in the final age", apply=apply)


resultTypes = [
    ResultType("strength", hydrate_strength_result, complexity=0),
    ResultType("strength_lowstart", hydrate_strength_lowstart_result, minPower=3),
    ResultType("spawn", hydrate_spawn_result, weight=.25, preferredPhase=Phase.BEFORE),
    ResultType("mirror_iron", hydrate_mirror_iron_result, minPower=2, maxPower=3, weight=.1),
    ResultType("mirror_crystal", hydrate_mirror_crystal_result, minPower=2, maxPower=3, weight=.1),
    ResultType("weaken_opponent_army", hydrate_weaken_opponent_army_result, weight=.25, complexity=2)
]


def generate_trigger_result(card, difficulty=None):
    filteredTriggerTypes = triggerTypes
    if difficulty is not None:
        filteredTriggerTypes = [tt for tt in triggerTypes if tt.difficulty == difficulty]
    triggerTypeWeights = [tt.weight for tt in filteredTriggerTypes]
    triggerType = random.choices(filteredTriggerTypes, weights=triggerTypeWeights)[0]
    # TODO: make this wiggle occasionally
    filteredResultTypes = [rt for rt in resultTypes if rt.minPower <= triggerType.difficulty and rt.maxPower >= triggerType.difficulty and len(rt.phases & triggerType.phases) > 0]
    resultTypeWeights = [rt.weight for rt in filteredResultTypes]
    resultType = random.choices(filteredResultTypes, weights=resultTypeWeights)[0]

    card.triggerSeed = random.randrange(sys.maxsize)
    trigger = triggerType.hydrate(card)

    card.resultSeed = random.randrange(sys.maxsize)
    result = resultType.hydrate(card, triggerType.difficulty)

    possiblePhases = triggerType.phases & resultType.phases
    preferredPhase = Phase.EFFECT
    if triggerType.preferredPhase is not None and triggerType.preferredPhase in possiblePhases:
        preferredPhase = triggerType.preferredPhase
    elif resultType.preferredPhase is not None and resultType.preferredPhase in possiblePhases:
        preferredPhase = resultType.preferredPhase
    if preferredPhase not in possiblePhases:
        for p in Phase:
            if p in possiblePhases:
                preferredPhase = p
                break

    if card.mod is Mod.NORMAL:
        card.mod = Mod.TRIGGER
    if result.starting_str is not None:
        card.strength = result.starting_str(card)

    if result.apply is not None:
        effect = Effect(check=trigger.check, apply=result.apply, phase=preferredPhase,
                        interactive=triggerType.interactive or resultType.interactive, cardId=card.cardId,
                        name=f'{triggerType.name}-{resultType.name}', triggerName=triggerType.name,
                        triggerSeed=card.triggerSeed, resultName=resultType.name, resultSeed=card.resultSeed)
        card.effects.append(effect)
    condition = 'If'
    if preferredPhase is Phase.BEFORE:
        condition = 'Before effects, if'
    elif preferredPhase is Phase.AFTER:
        condition = 'After effects, if'
    card.desc = f'{condition} {trigger.desc}, {result.desc}'

    return card


def hydrate_effects_from_proto(card, protoCard):
    for protoEffect in protoCard.effects:
        triggerType = None
        for tt in triggerTypes:
            if tt.name == protoEffect.trigger_name:
                triggerType = tt
                break
        resultType = None
        for rt in resultTypes:
            if rt.name == protoEffect.result_name:
                resultType = rt
        if resultType is None or triggerType is None:
            return

        card.triggerSeed = protoEffect.trigger_seed
        trigger = triggerType.hydrate(card)

        card.resultSeed = protoEffect.result_seed
        result = resultType.hydrate(card, triggerType.difficulty)

        effect = Effect(check=trigger.check, apply=result.apply, phase=phase_from_proto(protoEffect.phase),
                        interactive=triggerType.interactive or resultType.interactive, cardId=card.cardId,
                        name=f'{triggerType.name}-{resultType.name}', triggerName=triggerType.name,
                        triggerSeed=protoEffect.trigger_seed, resultName=resultType.name,
                        resultSeed=protoEffect.result_seed)
        card.effects.append(effect)
