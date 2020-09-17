from flask import Blueprint, jsonify, request
from src.dao import create
from src.dao.judgement import Judgement
from src.dao.image import ForumImage
from src.server import util
from sqlitedao import SearchDict
import random

gameread = Blueprint('gameread', __name__)

TABLE_NAME = 'auth_judge'

@gameread.route('/', methods=["POST"])
def get_by_attr():
    if request.method == 'POST':
        data = request.get_json(force=True)
        if not check_args(data):
            return jsonify(util.fail_with_reason("Args not found"))
        return handle_request(data)
    return jsonify(util.fail_with_reason("Only post request allowed"))


def check_args(data):
    required_args = ['l_arg', 'x_arg']
    for arg in required_args:
        if not arg in data:
            return False
    return True


def handle_request(data):
    dao = create.get_dao()
    spread = 1
    l_arg = int(data['l_arg'])
    x_arg = int(data['x_arg'])
    possibles = []
    while True:
        l_lower = l_arg - spread
        x_lower = x_arg - spread
        l_higher = l_arg + spread
        x_higher = x_arg + spread
        terms = SearchDict()
        terms.add_between('l_judge', l_lower, l_higher)
        terms.add_between('x_judge', x_lower, x_higher)
        possibles = dao.search_table(TABLE_NAME, terms, debug=True)
        print("Found {} matching".format(len(possibles)))
        if len(possibles) > 0:
            break
        spread += 1
    selected = random.choice(possibles)
    result = {
        'author': selected['author'],
        'author_id': selected['author_id'],
        'l_judge': selected['l_judge'],
        'x_judge': selected['x_judge'],
    }
    result.update(util.SUCCESS_RESULT)
    return jsonify(result)
