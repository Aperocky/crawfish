from sqlitedao import SqliteDao, ColumnDict
from bs4 import BeautifulSoup
from src.dao.thread import ForumThread
from src.dao.image import ForumImage
from src.dao import create
from src.ingest.selenium import Selenium
import traceback
import math
import random
import json

MAIN_URL = "http://tieba.baidu.com"
MAIN_BLOCK_SELECTOR = "div#j_p_postlist"
FLOOR_SELECTOR = "div.l_post.j_l_post"
CONTENT_SELECTOR = "div.j_d_post_content"
AUTHOR_FLAG = "div.j_louzhubiaoshi.louzhubiaoshi"
IMAGE_SELECTOR = "img.BDE_Image"
CREATE_TIME_SELECTOR = "div.post-tail-wrap > span.tail-info"
DELETED_FLAG = "div#errorText > h1"


# Main func
def get_random_images(limit=500, amount=5, threshold=10):
    """
    Deposit info of images found in threads of authors given that they passed the scoring threshold.

    args:
        limit: int - only look in the top $limit authors
        amount: int - only take ingestion from $amount authors
        threshold: float - only clear an author for ingestion after they score higher than $threshold
    """
    if type(limit) is not int:
        limit = int(limit)
    if type(threshold) is not float:
        threshold = float(threshold)
    if type(amount) is not int:
        amount = int(amount)
    dao = create.get_dao()
    besties = dao.search_table("threads", {}, group_by=["author_id", "author"], limit=limit)
    random.shuffle(besties) # Add randomness
    counter = 0
    for each in besties:
        spoils = get_author_aggregate_stat(dao, each["author_id"], False)
        score = score_agg_stats(spoils["data"])
        if score["total"] > threshold:
            print("RUNNING INGEST FOR AUTHOR: {}".format(each["author"]))
            print(spoils["data"])
            summary = run_threads(spoils["threads"])
            print("NEW RESULTS FOR {}: {}".format(each["author"], summary))
            counter += 1
        if counter >= amount:
            break


# Main func
def get_id_images(author_id, vis=True):
    """
    Get pictures info from an author

    args:
        author_id: str - id of author
    """
    dao = create.get_dao()
    spoils = get_author_aggregate_stat(dao, author_id, True)
    score = score_agg_stats(spoils["data"])
    if vis:
        print(score)
    result = run_threads(spoils["threads"])
    print(result)


def get_author_aggregate_stat(dao, author_id, vis=True):
    threads = dao.get_items(ForumThread, {"author_id": author_id})
    agg_stats = {
        "total_threads": 0,
        "replies": 0,
        "update_count": 0,
        "crawled": 0,
        "years": {
            "2020": 0,
            "2019": 0,
            "2018": 0,
            "2017": 0,
            "2016": 0,
            "2015": 0,
            "2014": 0,
            "2013": 0,
            "2012": 0,
        }
    }
    for each in threads:
        agg_stats["total_threads"] += 1
        agg_stats["replies"] += each.get_replies()
        agg_stats["update_count"] += each.get_update_count()
        agg_stats["crawled"] += int(each.get_crawled_status())
        curr_year = True
        for year in agg_stats["years"].keys():
            if year in each.get_create_time():
                agg_stats["years"][year] += 1
                curr_year = False
        if curr_year:
            agg_stats["years"]["2020"] += 1
    # Visualize
    if vis:
        strsand = "NAME: {}\nTHREADS: {}\nREPLIES: {}\nUPDATES: {}\nAVERAGE: {}\nCRAWLED: {}"\
            .format(threads[0].get_author(), agg_stats["total_threads"], agg_stats["replies"],
            agg_stats["update_count"], agg_stats["replies"]/agg_stats["total_threads"], agg_stats["crawled"])
        print(strsand)
        print(agg_stats["years"])
    return {"data": agg_stats, "threads": threads}


def score_agg_stats(agg_stats):
    scoreboard = {}
    scoreboard["activity"] = math.log(agg_stats["update_count"]+1) / 2
    scoreboard["popularity"] = math.log(agg_stats["replies"]/agg_stats["total_threads"]+1) * 2
    scoreboard["quantity"] = math.log(agg_stats["total_threads"] + 5) - math.log(5)
    scoreboard["history"] = sum([e>0 for e in agg_stats["years"].values()])
    OLDEN_TIMES = {"2016", "2015", "2014", "2013", "2012"}
    scoreboard["total"] = sum(scoreboard.values())
    scoreboard["total"] += sum([v for k, v in agg_stats.items() if k in OLDEN_TIMES])
    return scoreboard

# ============================================
# FOR RUNNING FORUM THREADS
# ============================================

def store_info(image, thread, floor_num, create_time):
    dao = create.get_dao()
    src = image.attrs["src"]
    width = image.attrs["width"]
    height = image.attrs["height"]
    if "size" in image.attrs:
        size = image.attrs["size"]
    else:
        size = -1
    href = thread.get_href()
    author = thread.get_author()
    author_id = thread.get_author_id()
    imageria = ForumImage(src=src, href=href, image_size=size, image_width=width, image_height=height, author=author, author_id=author_id, floor_num=floor_num, create_time=create_time)
    return imageria


def run_post(post, thread):
    post_result = {
        "authfl": False,
        "images": 0,
    }
    auth_flag = post.select(AUTHOR_FLAG)
    if not auth_flag:
        return post_result
    post_result["authfl"] = True
    data_field = json.loads(post.attrs["data-field"])
    floor_num = data_field["content"]["post_index"]
    create_time = post.select(CREATE_TIME_SELECTOR)[-1].text
    content = post.select(CONTENT_SELECTOR)[0]
    if not content:
        print("NO CONTENT FOUND, LIKELY BAD PAGE LOAD")
    images = content.select(IMAGE_SELECTOR)
    post_result["images"] = len(images)
    imagelist = []
    for image in images:
        imagelist.append(store_info(image, thread, floor_num, create_time))
    if imagelist:
        dao = create.get_dao()
        dao.insert_items(imagelist)
    return post_result


def run_thread(thread):
    general_result = {
        "author_floor_count": 0,
        "image_count": 0,
    }
    if thread.get_crawled_status():
        print("Thread already crawled, passing")
        general_result["image_count"] = thread.get_image_count()
        return general_result
    thread_url = MAIN_URL + thread.get_href()
    ff = Selenium.get_instance()
    try:
        soup = ff.crawl(thread_url, 50, AUTHOR_FLAG)
    except:
        soup = ff.crawl(thread_url)
        delete_flag = soup.select(DELETED_FLAG)
        if not delete_flag:
            raise
        print("{} has been deleted, cannot access")
        dao = create.get_dao()
        crawled_thread = thread.mark_as_crawled(general_result["image_count"])
        dao.update_item(crawled_thread)
        return general_result
    posts = soup.select(MAIN_BLOCK_SELECTOR)[0]
    postlist = soup.select(FLOOR_SELECTOR)
    for post in postlist:
        post_result = run_post(post, thread)
        general_result["author_floor_count"] += int(post_result["authfl"])
        general_result["image_count"] += post_result["images"]
    dao = create.get_dao()
    crawled_thread = thread.mark_as_crawled(general_result["image_count"])
    dao.update_item(crawled_thread)
    return general_result


def run_threads(threads):
    general_result = {
        "author_floor_count": 0,
        "image_count": 0,
    }
    crawl_list = [thread for thread in threads if not thread.get_crawled_status()]
    print("{}/{} Crawled Already".format(len(threads) - len(crawl_list), len(threads)))
    for thread in crawl_list:
        print("Getting Images for {}".format(thread.get_title()))
        try:
            thread_result = run_thread(thread)
            print(thread_result)
            general_result["author_floor_count"] += thread_result["author_floor_count"]
            general_result["image_count"] += thread_result["image_count"]
        except Exception as e:
            print("Thread {} failed, continueing".format(thread.get_href()))
            traceback.print_exc()
    return general_result

