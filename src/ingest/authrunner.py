from sqlitedao import SqliteDao, ColumnDict
from bs4 import BeautifulSoup
from src.dao.thread import ForumThread
from src.dao.image import ForumImage
from src.dao import create
from src.ingest.selenium import Selenium
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


def score(agg_stats):
    scoreboard = {}
    scoreboard["activity"] = math.log(agg_stats["update_count"]+1)
    scoreboard["popularity"] = math.log(agg_stats["replies"]/agg_stats["total_threads"]+1)
    scoreboard["quantity"] = math.log(agg_stats["total_threads"] + 5) - math.log(5)
    scoreboard["history"] = sum([e>0 for e in agg_stats["years"].values()])
    scoreboard["total"] = sum(scoreboard.values())
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
    try:
        dao.insert_item(imageria)
    except:
        potential = dao.find_item(imageria)
        if potential is None:
            raise


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
    for image in images:
        store_info(image, thread, floor_num, create_time)
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
        soup = ff.crawl(thread_url, 20, AUTHOR_FLAG)
    except:
        soup = ff.crawl(thread_url)
        delete_flag = soup.select(DELETED_FLAG)
        if not delete_flag:
            print(soup)
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
        thread_result = run_thread(thread)
        print(thread_result)
        general_result["author_floor_count"] += thread_result["author_floor_count"]
        general_result["image_count"] += thread_result["image_count"]
    return general_result

