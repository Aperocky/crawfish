from flask import Blueprint, jsonify, request
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
