from functools import reduce

from instantaneous.game.play import simulate
from instantaneous.game import match, ai, card

# wins = simulate({}, 0, verbose=False)

# print(wins)
pool = card.generate_pool()
deck = ai.build_deck(pool, [ai.max_hard_synergy_strat()])
oppDeck = ai.build_deck(pool, [ai.special_strat()])
