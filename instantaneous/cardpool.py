from instantaneous.game.card import generate_pool, pool_to_proto
import json
import io

from flask import (
    Blueprint,
    send_file
)
from werkzeug.exceptions import abort

bp = Blueprint('cardpool', __name__, url_prefix='/cardpool')

# big old airquotes around the word database here
database = []

@bp.route('/new', methods=['POST'])
def new_card_pool():
    pool = generate_pool()
    database.append(pool)
    # TODO: generate an id?

    return send_file(
        io.BytesIO(pool_to_proto(pool).SerializeToString()),
        attachment_filename='pool.protodata',
        mimetype='attachment/x-protobuf'
    )


@bp.route('/<int:id>/submitdeck', methods=['POST'])
def submit_deck(id):
    try:
        cardpool = database[id]

        # TODO: take deck as input and calculate game result

        # TODO: use protobuff here and return game result rather than the pool back
        poolStrings = list(map(str, cardpool))
        return json.dumps(poolStrings)
    except IndexError:
        abort(404, "cardpool id {0} doesn't exist.".format(id))
