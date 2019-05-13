from instantaneous.game.card import generate_pool, pool_to_proto, pool_from_proto
from instantaneous.game import play
from instantaneous.proto import cardpool_pb2
import json
import io
import uuid
import sqlite3
from flask import (
    Blueprint,
    request,
    send_file
)
from werkzeug.exceptions import abort
from instantaneous.db import get_db

bp = Blueprint('cardpool', __name__, url_prefix='/cardpool')


@bp.route('/new', methods=['POST'])
def new_card_pool():
    pool = generate_pool()
    new_id = str(uuid.uuid4())
    print(new_id)
    protoPool = pool_to_proto(pool, id=new_id)
    poolSerialized = protoPool.SerializeToString()
    db = get_db()

    db.execute(
        'INSERT INTO cardpool (pool_id, data) VALUES (?, ?)',
        (new_id, poolSerialized)
    )
    db.commit()

    return send_file(
        io.BytesIO(poolSerialized),
        attachment_filename='pool.protodata',
        mimetype='attachment/x-protobuf'
    )


@bp.route('/<id>', methods=['GET'])
def get_card_pool(id):
    db = get_db()
    poolSql = db.execute(
        'SELECT * FROM cardpool WHERE pool_id = ?', (id,)
    ).fetchone()

    if poolSql is None:
        abort(404, "cardpool id {0} doesn't exist.".format(id))
        return

    protoPool = cardpool_pb2.CardPool()
    protoPool.ParseFromString(poolSql['data'])

    return send_file(
        io.BytesIO(poolSql['data']),
        attachment_filename='pool.protodata',
        mimetype='attachment/x-protobuf'
    )


@bp.route('/<id>/submitdeck', methods=['POST'])
def submit_deck(id):
    db = get_db()
    poolSql = db.execute(
        'SELECT * FROM cardpool WHERE pool_id = ?', (id,)
    ).fetchone()

    if poolSql is None:
        abort(404, "cardpool id {0} doesn't exist.".format(id))
        return
    protoPool = cardpool_pb2.CardPool()
    protoPool.ParseFromString(poolSql['data'])

    cardPool = pool_from_proto(protoPool)
    data = request.get_data()
    deck = cardpool_pb2.Deck()
    deck.ParseFromString(data)
    print(str(deck.card_ids))

    deckResult = play.play(deck, cardPool)
    return send_file(
        io.BytesIO(deckResult.SerializeToString()),
        attachment_filename='pool.protodata',
        mimetype='attachment/x-protobuf'
    )
