from sqlitedao import TableItem
import time

class ForumThread(TableItem):

    TABLE_NAME = "threads"
    INDEX_KEYS = ["href"]

    def __init__(self, row_tuple=None, href=None, replies=None, title=None, author=None, author_id=None, create_time=None):
        if row_tuple is not None:
            self.row_tuple = row_tuple
        else:
            currtime = int(time.time())
            self.row_tuple = {
                "href": href,
                "replies": replies,
                "title": title,
                "author": author,
                "author_id": author_id,
                "create_time": create_time,
                "insert_time": currtime,
                "update_time": currtime,
                "update_count": 0,
                "crawled": 0,
            }

    def update(self, replies, create_time):
        self.row_tuple["replies"] = replies
        self.row_tuple["create_time"] = create_time
        self.row_tuple["update_time"] = int(time.time())
        self.row_tuple["update_count"] = self.get_update_count() + 1
        return self

    def __str__(self):
         return "TITLE: {}\nHREF: {}\nREPLY COUNT: {}\nAUTHOR: {}\nAUTHOR_ID: {}\nCREATE_TIME: {}"\
            .format(self.row_tuple["title"],\
                    self.row_tuple["href"],\
                    self.row_tuple["replies"],\
                    self.row_tuple["author"],\
                    self.row_tuple["author_id"],\
                    self.row_tuple["create_time"])

    def same(self, other):
        if self.get_author_id() == other.get_author_id() and\
                self.get_title() == other.get_title() and\
                self.get_href() == other.get_href():
            return True
        return False

    def mark_as_crawled(self, image_count):
        self.row_tuple["crawled"] = 1
        self.row_tuple["image_count"] = image_count
        return self

    def mark_for_recrawl(self):
        self.row_tuple["crawled"] = 0
        return self

    def get_crawled_status(self):
        if not "crawled" in self.row_tuple:
            return False
        else:
            return bool(self.row_tuple["crawled"])

    def get_image_count(self):
        if not "image_count" in self.row_tuple:
            return 0
        else:
            return int(self.row_tuple["image_count"])

    def get_replies(self):
        return int(self.row_tuple["replies"])

    def get_create_time(self):
        return str(self.row_tuple["create_time"])

    def get_author_id(self):
        return str(self.row_tuple["author_id"])

    def get_author(self):
        return str(self.row_tuple["author"])

    def get_href(self):
        return str(self.row_tuple["href"])

    def get_title(self):
        return str(self.row_tuple["title"])

    def get_update_count(self):
        return int(self.row_tuple["update_count"])

    def get_insert_time(self):
        return int(self.row_tuple["insert_time"])

    def get_update_time(self):
        return int(self.row_tuple["update_time"])
