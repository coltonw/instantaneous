from instantaneous.game import card
from instantaneous.proto import cardpool_pb2


def test_card_to_proto():
    c = card.Card([3, 3, 3], card.Age.STONE, card.Race.UNDEAD,
                  card.Profession.ALCHEMIST, synergy=card.Race.HUMAN)
    cardProto = c.to_proto()
    assert cardProto.age is cardpool_pb2.Card.STONE
    assert cardProto.race is cardpool_pb2.Card.UNDEAD
    assert cardProto.prof is cardpool_pb2.Card.ALCHEMIST
    assert cardProto.race_synergy is cardpool_pb2.Card.HUMAN
    assert cardProto.prof_synergy is cardpool_pb2.Card.NONE_PROF
