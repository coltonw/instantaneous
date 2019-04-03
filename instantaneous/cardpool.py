from game.

from flask import (
    Blueprint, flash
)

bp = Blueprint('cardpool', __name__, url_prefix='/cardpool')

# big old airquotes around the word database here
database = {}

@bp.route('/new', methods=['POST'])
def new_card_pool():

    # TODO: actually have the card pool generated here and have it returned via json and/or protobuf
    flash('Not yet implemented')

    return ''


@bp.route('/<int:id>/submitdeck', methods=['POST'])
def submit_deck(id):
    cardpool = database(id)

    # TODO: actually have the game played here and have it return json and/or protobuf
    flash('Not yet implemented')

    return ''
