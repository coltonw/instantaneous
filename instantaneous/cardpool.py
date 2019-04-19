from instantaneous.game.card import generate_pool, pool_to_proto
from instantaneous.game import play
from instantaneous.proto import cardpool_pb2
import json
import io

from flask import (
    Blueprint,
    request,
    send_file
)
from werkzeug.exceptions import abort

bp = Blueprint('cardpool', __name__, url_prefix='/cardpool')

# big old airquotes around the word database here
database = [[]]

@bp.route('/new', methods=['POST'])
def new_card_pool():
    pool = generate_pool()
    # TODO: generate an id
    database[0] = pool

    return send_file(
        io.BytesIO(pool_to_proto(pool).SerializeToString()),
        attachment_filename='pool.protodata',
        mimetype='attachment/x-protobuf'
    )


@bp.route('/<int:id>/submitdeck', methods=['POST'])
def submit_deck(id):
    try:
        cardPool = database[id]
        data = request.get_data()
        deck = cardpool_pb2.Deck()
        deck.ParseFromString(data)
        print(str(deck.card_ids))
        # TODO: take deck as input and calculate game result

        deckResult = play.play(deck, cardPool)
        # TODO: actually use submitted deck and fill in deck result
        return send_file(
            io.BytesIO(deckResult.SerializeToString()),
            attachment_filename='pool.protodata',
            mimetype='attachment/x-protobuf'
        )
    except IndexError:
        abort(404, "cardpool id {0} doesn't exist.".format(id))
