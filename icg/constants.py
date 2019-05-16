from enum import Enum, auto
from icg.proto import cardpool_pb2


class Age(Enum):
    IRON = auto()
    CRYSTAL = auto()

    def to_proto(self):
        if self is Age.IRON:
            return cardpool_pb2.Card.IRON
        if self is Age.CRYSTAL:
            return cardpool_pb2.Card.CRYSTAL


def age_from_proto(proto):
    if proto is cardpool_pb2.Card.IRON:
        return Age.IRON
    if proto is cardpool_pb2.Card.CRYSTAL:
        return Age.CRYSTAL
    return None


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

    def plural(self):
        if self is Race.BEASTMAN:
            return 'BEASTMEN'
        elif self is Race.UNDEAD:
            return self.name
        return f"{self.name}S"


def race_from_proto(proto):
    if proto is cardpool_pb2.Card.BEASTMAN:
        return Race.BEASTMAN
    if proto is cardpool_pb2.Card.HUMAN:
        return Race.HUMAN
    if proto is cardpool_pb2.Card.UNDEAD:
        return Race.UNDEAD
    return None


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

    def plural(self):
        if self is Profession.WOODSMAN:
            return 'WOODSMEN'
        return f"{self.name}S"


def prof_from_proto(proto):
    if proto is cardpool_pb2.Card.ALCHEMIST:
        return Profession.ALCHEMIST
    if proto is cardpool_pb2.Card.BATTLETECH:
        return Profession.BATTLETECH
    if proto is cardpool_pb2.Card.CONJUROR:
        return Profession.CONJUROR
    if proto is cardpool_pb2.Card.PROPHET:
        return Profession.PROPHET
    if proto is cardpool_pb2.Card.WOODSMAN:
        return Profession.WOODSMAN
    if proto is cardpool_pb2.Card.PEASANT:
        return Profession.PEASANT
    return None


class Phase(Enum):
    BEFORE = auto()
    EFFECT = auto()
    AFTER = auto()
    RESULT = auto()


def phase_from_proto(proto):
    if proto is cardpool_pb2.CardEffect.BEFORE:
        return Phase.BEFORE
    if proto is cardpool_pb2.CardEffect.EFFECT:
        return Phase.EFFECT
    if proto is cardpool_pb2.CardEffect.AFTER:
        return Phase.AFTER
    if proto is cardpool_pb2.CardEffect.RESULT:
        return Phase.RESULT
    return None


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


BASE_STRENGTH = {
    Age.IRON: [4, 4],
    Age.CRYSTAL: [0, 7]
}
# power 0, 1, 2, 3
# for iron age, these are split evenly so they must be even
POWER_ADVANTAGE = [0, 2, 4, 6]


USEFUL_PROFS = [prof for prof in list(Profession) if prof != Profession.PEASANT]

EASY_PROF_SYNERGY_THRESHOLD = 5
EASY_RACE_SYNERGY_THRESHOLD = 8

HARD_PROF_SYNERGY_THRESHOLD = 7
HARD_RACE_SYNERGY_THRESHOLD = 12

PROF_COUNTER_THRESHOLD = 5
RACE_COUNTER_THRESHOLD = 8

CRYSTAL_SYNERGY_THRESHOLD = 10

# there are 6 professions
EASY_VARIETY_THRESHOLD = 1
HARD_VARIETY_THRESHOLD = 2
# there are 3 races
EASY_DIVERSITY_THRESHOLD = 2
HARD_DIVERSITY_THRESHOLD = 4

DECK_SIZE = 16
