from src.dao import create
from src.dao.thread import ForumThread
from src.ingest.selenium import Selenium
from sqlitedao import DuplicateError
import json, random


CONF_INI = open('conf/conf.json')
target = json.load(CONF_INI)["TARGET"]
URL_HEAD = "https://tieba.baidu.com/f?kw={}&ie=utf-8&pn=".format(target)
URL_HEAD_TOP = "https://tieba.baidu.com/f?kw={}&ie=utf-8&tab=good&pn=".format(target)
THREADLIST_SELECTOR = "ul#thread_list"
INDIVIDUAL_THREADOR = "li.j_thread_list.clearfix"
REP_NUM_CAPT = "span.threadlist_rep_num"
TITLE_BLOCK = "a.j_th_tit"
AUTH_DATA_CAPT = "span.tb_icon_author"
CREATE_TIME_CAPT = "span.is_show_create_time"
AUTH_STRING_RID = "主题作者: "


# Main func
def get_threads(limit=500, top=False):
    """
    Get a list of thread and its info from the forum.

    args:
        limit: int - the amount of newest thread to ingest based on forum ranking
    """
    if type(limit) is not int:
        limit = int(limit)
    if type(top) is not bool:
        top = top == "true"
        if top:
            print("getting top threads instead")
    dao = create.get_dao()
    create.create_tables()
    threadgen = runthreads(limit, top)
    for threadbatch in threadgen:
        record = {
            "NEW_ITEM": 0,
            "NOT_UPDATED": 0,
            "UPDATED": 0,
            "CANNOT_UPDATE": 0,
            "SHIT": 0,
        }
        for thread in threadbatch:
            record[thread_helper(dao, thread)] += 1
        print("Batch record: {}".format(record))
    print("Total of {} threads stored".format(dao.get_row_count("threads")))


def get_batch(url):
    ff = Selenium.get_instance()
    soup = ff.crawl(url, 20, TITLE_BLOCK)
    threadblock = soup.select(THREADLIST_SELECTOR)[0]
    threadobjs = []
    for thread in threadblock.select(INDIVIDUAL_THREADOR):
        rep_count = int(thread.select(REP_NUM_CAPT)[0].text)
        title = thread.select(TITLE_BLOCK)[0]
        author = thread.select(AUTH_DATA_CAPT)[0].attrs["title"].replace(AUTH_STRING_RID, "")
        author_id = json.loads(thread.select(AUTH_DATA_CAPT)[0].attrs["data-field"])["user_id"]
        create_time = thread.select(CREATE_TIME_CAPT)[0].text
        href = title.attrs["href"]
        title_str = title.attrs["title"]
        threadobj = ForumThread(href=href, replies=rep_count, title=title_str, author=author, author_id=author_id, create_time=create_time)
        threadobjs.append(threadobj)
    return threadobjs


def runthreads(limit=20000, top=False):
    start = 0
    while True:
        if start > limit:
            break
        if top:
            threadobjs = get_batch(URL_HEAD_TOP + str(start))
        else:
            threadobjs = get_batch(URL_HEAD + str(start))
        start += 50
        yield threadobjs


def thread_helper(dao, thread):
    try:
        dao.insert_item(thread)
        return "NEW_ITEM"
    except DuplicateError:
        existing_thread = dao.find_item(thread)
        if existing_thread.same(thread):
            if existing_thread.get_replies() == thread.get_replies():
                return "NOT_UPDATED"
            else:
                update_thread = existing_thread.update(thread.get_replies(), thread.get_create_time())
                dao.update_item(update_thread)
                return "UPDATED"
        else:
            print("UNRECONCILABLE DIFF FOUND:")
            print("EXISTING: {}".format(existing_thread))
            print("NEW: {}".format(thread))
            print("===========")
            return "CANNOT_UPDATE"
    except Exception as e:
        print("CAUGHT EXCEPTION: {}".format(e))
        return "SHIT"
