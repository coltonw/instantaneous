from random import sample, shuffle
from card import BASE_STRENGTH, Age
from match import DECK_SIZE


def deck_sample(deck, samplePool, sampleSize=DECK_SIZE):
    result = sample(samplePool, max(min(sampleSize, DECK_SIZE - len(deck), len(samplePool)), 0))
    return deck + result


# this is an arbitrary card strength value used for sorting
def get_card_relative_strength(card):
    if card.strength > BASE_STRENGTH[card.age]:
        return 2
    elif len(card.desc) > 0:
        return 1
    return 0


def sort_by_strength(basePool):
    return sorted(basePool, key=get_card_relative_strength, reverse=True)


def get_age_pools(basePool):
    pool = basePool[:]
    shuffle(pool)
    pool = sort_by_strength(pool)
    stone = [card for card in pool if card.age == Age.STONE]
    iron = [card for card in pool if card.age == Age.IRON]
    crystal = [card for card in pool if card.age == Age.CRYSTAL]
    return (stone, iron, crystal)


def strong(basePool):
    pool = basePool[:]
    strong = [card for card in pool if card.strength > BASE_STRENGTH[card.age]]
    deck = deck_sample([], strong)
    if len(deck) < DECK_SIZE:
        weak = [card for card in pool if card.strength <= BASE_STRENGTH[card.age]]
        deck = deck_sample(deck, weak)
    return deck


def even(basePool):
    (stone, iron, crystal) = get_age_pools(basePool)
    deck = []
    for i in range(DECK_SIZE):
        if len(stone) > i:
            deck = deck + [stone[i]]
        if len(iron) > i:
            deck = deck + [iron[i]]
        if len(crystal) > i:
            deck = deck + [crystal[i]]
        if len(deck) >= DECK_SIZE:
            return deck[0:20]
    return deck


def stone_iron(basePool):
    (stone, iron, crystal) = get_age_pools(basePool)
    deck = []
    for i in range(DECK_SIZE):
        if len(stone) > i:
            deck = deck + [stone[i]]
        if len(iron) > i:
            deck = deck + [iron[i]]
        if len(deck) >= DECK_SIZE:
            return deck[0:20]
    return deck


def iron_crystal(basePool):
    (stone, iron, crystal) = get_age_pools(basePool)
    deck = []
    for i in range(DECK_SIZE):
        if len(iron) > i:
            deck = deck + [iron[i]]
        if len(crystal) > i:
            deck = deck + [crystal[i]]
        if len(deck) >= DECK_SIZE:
            return deck[0:20]
    return deck


def low_stone(basePool):
    (stone, iron, crystal) = get_age_pools(basePool)
    deck = []
    for i in range(DECK_SIZE):
        if len(stone) > i and i < 4:
            deck = deck + [stone[i]]
        if len(iron) > i:
            deck = deck + [iron[i]]
        if len(crystal) > i:
            deck = deck + [crystal[i]]
        if len(deck) >= DECK_SIZE:
            return deck[0:20]
    return deck