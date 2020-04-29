from src.dao.thread import ForumThread
from src.ingest.selenium import Selenium
import json, random

CONF_INI = open('conf/conf.json')
target = json.load(CONF_INI)["TARGET"]
URL_HEAD = "https://tieba.baidu.com/f?kw={}&ie=utf-8&pn=".format(target)

THREADLIST_SELECTOR = "ul#thread_list"
INDIVIDUAL_THREADOR = "li.j_thread_list.clearfix"
REP_NUM_CAPT = "span.threadlist_rep_num"
TITLE_BLOCK = "a.j_th_tit"
AUTH_DATA_CAPT = "span.tb_icon_author"
CREATE_TIME_CAPT = "span.is_show_create_time"
AUTH_STRING_RID = "主题作者: "

ff = Selenium.get_instance()

def get_batch(url):
    soup = ff.crawl(url, random.uniform(0.2, 1.2))
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

def runthreads(limit=20000):
    start = 0
    while True:
        if start > limit:
            break
        threadobjs = get_batch(URL_HEAD + str(start))
        start += 50
        yield threadobjs
