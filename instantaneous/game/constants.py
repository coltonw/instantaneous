from enum import Enum, auto
from instantaneous.proto import cardpool_pb2


class Age(Enum):
    IRON = 2
    CRYSTAL = 4

    def to_proto(self):
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

    def plural(self):
        if self is Race.BEASTMAN:
            return 'BEASTMEN'
        elif self is Race.UNDEAD:
            return self.name
        return f"{self.name}S"


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
    Age.IRON: [5, 5],
    Age.CRYSTAL: [0, 9]
}
EASY_PROF_SYNERGY_THRESHOLD = 5
EASY_RACE_SYNERGY_THRESHOLD = 8

HARD_PROF_SYNERGY_THRESHOLD = 7
HARD_RACE_SYNERGY_THRESHOLD = 13

PROF_COUNTER_THRESHOLD = 5
RACE_COUNTER_THRESHOLD = 8

CRYSTAL_SYNERGY_THRESHOLD = 10

# there are 6 professions
EASY_VARIETY_THRESHOLD = 1
HARD_VARIETY_THRESHOLD = 2
# there are 3 races
EASY_DIVERSITY_THRESHOLD = 2
HARD_DIVERSITY_THRESHOLD = 4

# these are one less than 4 base strength cards.
# This means you can win an age with 2 strong cards and 1 base strength card
# or with 1 really strong card and 2 base strength cards
IRON_BONUS_THRESHOLD = 19
DECK_SIZE = 16
