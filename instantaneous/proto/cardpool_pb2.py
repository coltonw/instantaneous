# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: instantaneous/proto/cardpool.proto

import sys
_b=sys.version_info[0]<3 and (lambda x:x) or (lambda x:x.encode('latin1'))
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
from google.protobuf import descriptor_pb2
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor.FileDescriptor(
  name='instantaneous/proto/cardpool.proto',
  package='',
  syntax='proto3',
  serialized_pb=_b('\n\"instantaneous/proto/cardpool.proto\"?\n\x08\x43\x61rdPool\x12\n\n\x02id\x18\x01 \x01(\t\x12\x14\n\x05\x63\x61rds\x18\x02 \x03(\x0b\x32\x05.Card\x12\x11\n\tdeck_size\x18\x03 \x01(\x05\")\n\x04\x44\x65\x63k\x12\x0f\n\x07pool_id\x18\x01 \x01(\t\x12\x10\n\x08\x63\x61rd_ids\x18\x02 \x03(\x05\"^\n\nDeckResult\x12\x10\n\x08win_rate\x18\x01 \x01(\x02\x12\x0c\n\x04wins\x18\x02 \x01(\x05\x12\x0e\n\x06losses\x18\x03 \x01(\x05\x12\x0c\n\x04rank\x18\x04 \x01(\x05\x12\x12\n\npercentile\x18\x05 \x01(\x02\"\xea\x03\n\x04\x43\x61rd\x12\n\n\x02id\x18\x01 \x01(\x05\x12\x16\n\x0estone_strength\x18\x02 \x01(\x05\x12\x15\n\riron_strength\x18\x03 \x01(\x05\x12\x18\n\x10\x63rystal_strength\x18\x04 \x01(\x05\x12\x16\n\x03\x61ge\x18\x05 \x01(\x0e\x32\t.Card.Age\x12\x18\n\x04race\x18\x06 \x01(\x0e\x32\n.Card.Race\x12\x1e\n\x04prof\x18\x07 \x01(\x0e\x32\x10.Card.Profession\x12\x0c\n\x04\x64\x65sc\x18\x08 \x01(\t\x12 \n\x0crace_synergy\x18\t \x01(\x0e\x32\n.Card.Race\x12&\n\x0cprof_synergy\x18\n \x01(\x0e\x32\x10.Card.Profession\"5\n\x03\x41ge\x12\x0c\n\x08NONE_AGE\x10\x00\x12\t\n\x05STONE\x10\x01\x12\x08\n\x04IRON\x10\x02\x12\x0b\n\x07\x43RYSTAL\x10\x03\":\n\x04Race\x12\r\n\tNONE_RACE\x10\x00\x12\x0c\n\x08\x42\x45\x41STMAN\x10\x01\x12\t\n\x05HUMAN\x10\x02\x12\n\n\x06UNDEAD\x10\x03\"p\n\nProfession\x12\r\n\tNONE_PROF\x10\x00\x12\r\n\tALCHEMIST\x10\x01\x12\x0e\n\nBATTLETECH\x10\x02\x12\x0c\n\x08\x43ONJUROR\x10\x03\x12\x0b\n\x07PROPHET\x10\x04\x12\x0c\n\x08WOODSMAN\x10\x05\x12\x0b\n\x07PEASANT\x10\x06\x62\x06proto3')
)
_sym_db.RegisterFileDescriptor(DESCRIPTOR)



_CARD_AGE = _descriptor.EnumDescriptor(
  name='Age',
  full_name='Card.Age',
  filename=None,
  file=DESCRIPTOR,
  values=[
    _descriptor.EnumValueDescriptor(
      name='NONE_AGE', index=0, number=0,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='STONE', index=1, number=1,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='IRON', index=2, number=2,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='CRYSTAL', index=3, number=3,
      options=None,
      type=None),
  ],
  containing_type=None,
  options=None,
  serialized_start=506,
  serialized_end=559,
)
_sym_db.RegisterEnumDescriptor(_CARD_AGE)

_CARD_RACE = _descriptor.EnumDescriptor(
  name='Race',
  full_name='Card.Race',
  filename=None,
  file=DESCRIPTOR,
  values=[
    _descriptor.EnumValueDescriptor(
      name='NONE_RACE', index=0, number=0,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='BEASTMAN', index=1, number=1,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='HUMAN', index=2, number=2,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='UNDEAD', index=3, number=3,
      options=None,
      type=None),
  ],
  containing_type=None,
  options=None,
  serialized_start=561,
  serialized_end=619,
)
_sym_db.RegisterEnumDescriptor(_CARD_RACE)

_CARD_PROFESSION = _descriptor.EnumDescriptor(
  name='Profession',
  full_name='Card.Profession',
  filename=None,
  file=DESCRIPTOR,
  values=[
    _descriptor.EnumValueDescriptor(
      name='NONE_PROF', index=0, number=0,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='ALCHEMIST', index=1, number=1,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='BATTLETECH', index=2, number=2,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='CONJUROR', index=3, number=3,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='PROPHET', index=4, number=4,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='WOODSMAN', index=5, number=5,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='PEASANT', index=6, number=6,
      options=None,
      type=None),
  ],
  containing_type=None,
  options=None,
  serialized_start=621,
  serialized_end=733,
)
_sym_db.RegisterEnumDescriptor(_CARD_PROFESSION)


_CARDPOOL = _descriptor.Descriptor(
  name='CardPool',
  full_name='CardPool',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='id', full_name='CardPool.id', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='cards', full_name='CardPool.cards', index=1,
      number=2, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='deck_size', full_name='CardPool.deck_size', index=2,
      number=3, type=5, cpp_type=1, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=38,
  serialized_end=101,
)


_DECK = _descriptor.Descriptor(
  name='Deck',
  full_name='Deck',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='pool_id', full_name='Deck.pool_id', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='card_ids', full_name='Deck.card_ids', index=1,
      number=2, type=5, cpp_type=1, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=103,
  serialized_end=144,
)


_DECKRESULT = _descriptor.Descriptor(
  name='DeckResult',
  full_name='DeckResult',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='win_rate', full_name='DeckResult.win_rate', index=0,
      number=1, type=2, cpp_type=6, label=1,
      has_default_value=False, default_value=float(0),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='wins', full_name='DeckResult.wins', index=1,
      number=2, type=5, cpp_type=1, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='losses', full_name='DeckResult.losses', index=2,
      number=3, type=5, cpp_type=1, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='rank', full_name='DeckResult.rank', index=3,
      number=4, type=5, cpp_type=1, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='percentile', full_name='DeckResult.percentile', index=4,
      number=5, type=2, cpp_type=6, label=1,
      has_default_value=False, default_value=float(0),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=146,
  serialized_end=240,
)


_CARD = _descriptor.Descriptor(
  name='Card',
  full_name='Card',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='id', full_name='Card.id', index=0,
      number=1, type=5, cpp_type=1, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='stone_strength', full_name='Card.stone_strength', index=1,
      number=2, type=5, cpp_type=1, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='iron_strength', full_name='Card.iron_strength', index=2,
      number=3, type=5, cpp_type=1, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='crystal_strength', full_name='Card.crystal_strength', index=3,
      number=4, type=5, cpp_type=1, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='age', full_name='Card.age', index=4,
      number=5, type=14, cpp_type=8, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='race', full_name='Card.race', index=5,
      number=6, type=14, cpp_type=8, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='prof', full_name='Card.prof', index=6,
      number=7, type=14, cpp_type=8, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='desc', full_name='Card.desc', index=7,
      number=8, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='race_synergy', full_name='Card.race_synergy', index=8,
      number=9, type=14, cpp_type=8, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='prof_synergy', full_name='Card.prof_synergy', index=9,
      number=10, type=14, cpp_type=8, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
    _CARD_AGE,
    _CARD_RACE,
    _CARD_PROFESSION,
  ],
  options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=243,
  serialized_end=733,
)

_CARDPOOL.fields_by_name['cards'].message_type = _CARD
_CARD.fields_by_name['age'].enum_type = _CARD_AGE
_CARD.fields_by_name['race'].enum_type = _CARD_RACE
_CARD.fields_by_name['prof'].enum_type = _CARD_PROFESSION
_CARD.fields_by_name['race_synergy'].enum_type = _CARD_RACE
_CARD.fields_by_name['prof_synergy'].enum_type = _CARD_PROFESSION
_CARD_AGE.containing_type = _CARD
_CARD_RACE.containing_type = _CARD
_CARD_PROFESSION.containing_type = _CARD
DESCRIPTOR.message_types_by_name['CardPool'] = _CARDPOOL
DESCRIPTOR.message_types_by_name['Deck'] = _DECK
DESCRIPTOR.message_types_by_name['DeckResult'] = _DECKRESULT
DESCRIPTOR.message_types_by_name['Card'] = _CARD

CardPool = _reflection.GeneratedProtocolMessageType('CardPool', (_message.Message,), dict(
  DESCRIPTOR = _CARDPOOL,
  __module__ = 'instantaneous.proto.cardpool_pb2'
  # @@protoc_insertion_point(class_scope:CardPool)
  ))
_sym_db.RegisterMessage(CardPool)

Deck = _reflection.GeneratedProtocolMessageType('Deck', (_message.Message,), dict(
  DESCRIPTOR = _DECK,
  __module__ = 'instantaneous.proto.cardpool_pb2'
  # @@protoc_insertion_point(class_scope:Deck)
  ))
_sym_db.RegisterMessage(Deck)

DeckResult = _reflection.GeneratedProtocolMessageType('DeckResult', (_message.Message,), dict(
  DESCRIPTOR = _DECKRESULT,
  __module__ = 'instantaneous.proto.cardpool_pb2'
  # @@protoc_insertion_point(class_scope:DeckResult)
  ))
_sym_db.RegisterMessage(DeckResult)

Card = _reflection.GeneratedProtocolMessageType('Card', (_message.Message,), dict(
  DESCRIPTOR = _CARD,
  __module__ = 'instantaneous.proto.cardpool_pb2'
  # @@protoc_insertion_point(class_scope:Card)
  ))
_sym_db.RegisterMessage(Card)


# @@protoc_insertion_point(module_scope)
