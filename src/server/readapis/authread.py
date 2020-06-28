from flask import Blueprint, jsonify, request
from src.dao import create
from src.dao.thread import ForumThread
from src.dao.image import ForumImage
from src.ingest import authrunner
from src.ingest.imrunner import score_id
from src.server import util
import random

authread = Blueprint('authread', __name__)

@authread.route("/random", methods=["GET"])
def authrandom():
    dao = create.get_dao()
    top = dao.search_table("threads", {}, group_by=["author_id", "author"], limit=1000)
    auth_select = random.choice(top)
    result = build_author_result(auth_select["author"], auth_select["author_id"])
    return jsonify(result)


@authread.route("/find", methods=["GET"])
def auth_find():
    author = request.args.get('author', '')
    author_id = request.args.get('author_id', '')
    if not author and not author_id:
        return jsonify(fail_with_reason("Did not pass in author or author_id"))
    dao = create.get_dao()
    if not author:
        author_list = authrunner.get_author_from_id(author_id)
        if not author_list:
            return jsonify(util.fail_with_reason("Did not find author by id"))
        return jsonify(build_author_result(author_list[0], author_id))
    # There is author but no author_id
    author_id = authrunner.get_author_id(author)
    if author_id == "NO_SUCH_AUTHOR":
        return jsonify(util.fail_with_reason("Did not find author"))
    return jsonify(build_author_result(author, author_id))


@authread.route("/sample_img", methods=["GET"])
def get_new_samples():
    if not "author_id" in util.AUTH_CACHE:
        return jsonify(util.fail_with_reason("No record of auth cache for new samples"))
    samples = [im.get_file_path() for im in random_image_block(util.AUTH_CACHE["images"])]
    util.AUTH_CACHE["result"]["image_samples"] = samples
    return jsonify(util.AUTH_CACHE["result"])


def build_author_result(author, author_id):
    result = {
        "auth_name": author,
        "auth_id": author_id,
        "auth_score": score_id(author_id),
    }
    result.update(get_auth_information(author_id))
    result.update(util.SUCCESS_RESULT)
    util.populate_auth_cache(result["auth_id"], result)
    return result


def get_auth_information(author_id):
    dao = create.get_dao()
    threads = dao.get_items(ForumThread, {"author_id": author_id})
    images = dao.get_items(ForumImage, {"author_id": author_id})
    util.populate_auth_image(images)
    samples = [im.get_file_path() for im in random_image_block(images)]
    return {
        "auth_info": auth_info_block(threads, images),
        "image_samples": samples,
    }


def random_image_block(images):
    existing = [im for im in images if im.get_crawled_status() and not im.is_duplicate()]
    if len(existing) > 5:
        return random.sample(existing, 5)
    return existing


def auth_info_block(threads, images):
    avg_replies = sum([t.get_replies() for t in threads])/len(threads)
    return {
        "thread_count": len(threads),
        "avg_replies": avg_replies,
        "thread_crawled": len([t for t in threads if t.get_crawled_status()]),
        "image_count": len(images),
        "image_loaded": len([im for im in images if im.get_crawled_status()]),
        "duplicate_count": len([im for im in images if im.is_duplicate()]),
    }

