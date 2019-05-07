from functools import reduce

from instantaneous.game.play import simulate
from instantaneous.game import match, ai, card

(wins, gamesPlayed, effects, decks) = simulate({}, 0, verbose=False)

print(wins)
