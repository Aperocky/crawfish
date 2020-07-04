from flask import Blueprint, jsonify, request
from src.dao import create
from src.dao.judgement import Judgement
from src.server import util
from src.recon import reconciliation
from src.ingest import imrunner
from multiprocessing import Process

authmod = Blueprint('authmod', __name__)

@authmod.route("/recon_id", methods=["GET"])
def recon_author_id():
    author_id = request.args.get('author_id', '')
    remove_duplicate = request.args.get('remove_duplicate', '')
    remove_dup = False
    if not author_id:
        return jsonify(fail_with_reason("Did not pass in author_id"))
    if remove_duplicate.lower() == "true":
        remove_dup = True
    result = reconciliation.recon_id(author_id, remove_dup)
    result.update(util.SUCCESS_RESULT)
    return jsonify(result)


@authmod.route("/load_id", methods=["GET"])
def load_author_id():
    author_id = request.args.get('author_id', '')
    # This is not yet working because we need async/queue
    return jsonify(util.SUCCESS_RESULT)


@authmod.route("/judge_id", methods=["POST"])
def judge_author_id():
    request_data = request.get_json()
    dao = create.get_dao()
    mandatory_fields = ["author", "author_id", "update_count", "thread_count", "image_count", "l_judge", "x_judge", "avg_replies"]
    if not all(f in request_data for f in mandatory_fields):
        return jsonify(util.fail_with_reason("Need to pass in author and author_id"))
    author = request_data["author"]
    author_id = request_data["author_id"]
    thread_count = request_data["thread_count"]
    image_count = request_data["image_count"]
    update_count = request_data["update_count"]
    avg_replies = request_data["avg_replies"]
    l_judge = request_data["l_judge"]
    x_judge = request_data["x_judge"]
    existing_judgement = dao.find_item(Judgement(author_id=author_id))

    # Sanity check
    if not type(l_judge) == type(x_judge) == int:
        return jsonify(util.fail_with_reason("Judgements need to be delivered in integers"))
    if l_judge > 10 or x_judge > 10:
        return jsonify(util.fail_with_reason("Judgements should not exceed 10"))
    if l_judge < 0 or x_judge < 0:
        return jsonify(util.fail_with_reason("Judgement should not be less than 0"))

    if existing_judgement:
        modified_judgement = existing_judgement.update(thread_count, image_count, avg_replies, update_count, l_judge, x_judge)
        dao.update_item(modified_judgement)
    else:
        new_judgement = Judgement(author_id=author_id, author=author, l_judge=l_judge, x_judge=x_judge, thread_count=thread_count, image_count=image_count, avg_replies=avg_replies, update_count=update_count)
        dao.insert_item(new_judgement)
    return jsonify(util.SUCCESS_RESULT)

