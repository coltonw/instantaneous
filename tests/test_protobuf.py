from icg import card
from icg.proto import cardpool_pb2


def test_card_to_proto():
    c = card.Card([5, 5], card.Age.IRON, card.Race.UNDEAD,
                  card.Profession.ALCHEMIST, synergy=card.Race.HUMAN)
    cardProto = c.to_proto()
    assert cardProto.age is cardpool_pb2.Card.IRON
    assert cardProto.race is cardpool_pb2.Card.UNDEAD
    assert cardProto.prof is cardpool_pb2.Card.ALCHEMIST
    assert cardProto.race_synergy is cardpool_pb2.Card.HUMAN
    assert cardProto.prof_synergy is cardpool_pb2.Card.NONE_PROF


def test_cardpool_to_proto():
    p = card.generate_pool()
    protoPool = card.pool_to_proto(p, 'test')
    assert protoPool.id == 'test'
    assert len(protoPool.cards) == len(p)


def test_card_serialize_unserialize():
    oldCard = card.Card([5, 5], card.Age.IRON, card.Race.UNDEAD, card.Profession.ALCHEMIST)
    # test includes randomness which is probably questionable
    card.generate_trigger_result(oldCard)
    protoCard = oldCard.to_proto(complete=True)
    newCard = card.card_from_proto(protoCard)

    assert newCard.strength[0] == oldCard.strength[0]
    assert newCard.strength[1] == oldCard.strength[1]
    assert newCard.age is oldCard.age
    assert newCard.race is oldCard.race
    assert newCard.prof is oldCard.prof
    assert newCard.synergy is oldCard.synergy
    newEffect = newCard.effects[0]
    oldEffect = oldCard.effects[0]
    assert newEffect.name != ""
    assert newEffect.name == oldEffect.name
    assert newEffect.interactive == oldEffect.interactive
    assert newEffect.triggerName == oldEffect.triggerName
    assert newEffect.triggerSeed == oldEffect.triggerSeed
    assert newEffect.resultName == oldEffect.resultName
    assert newEffect.resultSeed == oldEffect.resultSeed
