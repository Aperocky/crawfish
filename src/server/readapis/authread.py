from flask import Blueprint, jsonify, request
from src.dao import create
from src.dao.judgement import Judgement
from src.dao.thread import ForumThread
from src.dao.image import ForumImage
from src.ingest import authrunner
from src.ingest.imrunner import score_id
from src.server import util
import random

authread = Blueprint('authread', __name__)

@authread.route("/random", methods=["GET"])
def authrandom():
    crawled = request.args.get('crawled', '')
    crawled = bool(crawled)
    tojudge = request.args.get('tojudge', '')
    tojudge = bool(tojudge)
    above_l = request.args.get('above_l', '0')
    above_l = int(above_l)
    above_x = request.args.get('above_x', '0')
    above_x = int(above_x)
    dao = create.get_dao()
    top = dao.search_table("images", {}, group_by=["author_id", "author"], limit=1000)

    auth_select = {}
    while True:
        auth_select = random.choice(top)
        c_flag = False if crawled else True
        t_flag = False if tojudge else True
        l_flag = False if tojudge else True
        x_flag = False if tojudge else True
        judgement = dao.find_item(Judgement(author_id=auth_select["author_id"]))
        if crawled:
            images = dao.get_items(ForumImage, {"author_id": auth_select["author_id"]})
            if any(im.get_crawled_status() for im in images):
                c_flag = True
        if tojudge:
            if judgement:
                t_flag = True
            else:
                continue
            if judgement.get_l_judge() > above_l:
                l_flag = True
            if judgement.get_x_judge() > above_x:
                x_flag = True
        if all([c_flag, t_flag, l_flag, x_flag]):
            break

    result = build_author_result(auth_select["author"], auth_select["author_id"])
    return jsonify(result)


@authread.route("/find", methods=["GET"])
def auth_find():
    author = request.args.get('author', '')
    author_id = request.args.get('author_id', '')
    if not author and not author_id:
        return jsonify(util.fail_with_reason("Did not pass in author or author_id"))
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
    updated_samples  = random_image_block(util.AUTH_CACHE["images"])
    util.AUTH_CACHE["result"].update(updated_samples)
    return jsonify(util.AUTH_CACHE["result"])


@authread.route("/refresh", methods=["GET"])
def refresh():
    if not "author_id" in util.AUTH_CACHE:
        return jsonify(util.fail_with_reason("No record of auth cache for refresh"))
    return jsonify(build_author_result(util.AUTH_CACHE["result"]["auth_name"], util.AUTH_CACHE["result"]["auth_id"]))


@authread.route("/judgement", methods=["GET"])
def get_judgement():
    author_id = request.args.get("author_id", "")
    if not author_id:
        return jsonify(util.fail_with_reason("author_id not passed in"))
    dao = create.get_dao()
    dummy = Judgement(author_id=author_id)
    judgement = dao.find_item(dummy)
    if judgement:
        result = {
            "l_judge": judgement.get_l_judge(),
            "x_judge": judgement.get_x_judge(),
            "times_judged": judgement.get_judge_count(),
        }
        result.update(util.SUCCESS_RESULT)
        return jsonify(result)
    else:
        return jsonify(util.fail_with_reason("No judgement found"))


def build_author_result(author, author_id):
    result = {
        "auth_name": author,
        "auth_id": author_id,
        "auth_score": score_id(author_id, False),
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
    result = { "auth_info": auth_info_block(threads, images) }
    result.update(random_image_block(images))
    return result


def select_five(l):
    if len(l) > 5:
        return random.sample(l, 5)
    return l


def random_image_block(images):
    existing = [im for im in images if im.get_crawled_status() and not im.is_duplicate()]
    at_large = [im for im in images if not im.get_crawled_status()]
    return {
        "image_samples": [im.get_file_path() for im in select_five(existing)],
        "image_atlarge": [im.get_src() for im in select_five(at_large)],
    }


def auth_info_block(threads, images):
    avg_replies = sum([t.get_replies() for t in threads])/len(threads)
    return {
        "thread_count": len(threads),
        "avg_replies": avg_replies,
        "thread_crawled": len([t for t in threads if t.get_crawled_status()]),
        "image_count": len(images),
        "image_loaded": len([im for im in images if im.get_crawled_status()]),
        "duplicate_count": len([im for im in images if im.is_duplicate()]),
        "update_count": sum([t.get_update_count() for t in threads]),
    }

