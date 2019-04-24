from functools import reduce

from instantaneous.game.play import simulate
from instantaneous.game import match, ai, card

# wins = simulate({}, 0, verbose=False)

# print(wins)
pool = card.generate_pool()
deck = ai.build_deck(pool, [ai.max_hard_synergy_strat()])
oppDeck = ai.build_deck(pool, [ai.special_strat()])


def deck_strength1():
    return reduce(lambda sum, card: sum + card.calc_strength(2, deck, oppDeck), deck, 0)


def deck_strength2():
    return sum([card.calc_strength(2, deck, oppDeck) for card in deck])

if __name__ == '__main__':
    import timeit
    print(timeit.timeit("deck_strength2()", setup="from __main__ import deck_strength2", number=100000))

    print(timeit.timeit("deck_strength1()", setup="from __main__ import deck_strength1", number=100000))

