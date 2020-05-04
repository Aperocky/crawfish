from sqlitedao import TableItem
import urllib.request
import uuid
import time

class ForumImage(TableItem):

    TABLE_NAME = "images"
    INDEX_KEYS = ["src"]

    def __init__(self, row_tuple=None, src=None, href=None, image_size=None, image_height=None,
            image_width=None, author=None, author_id=None, floor_num=None, create_time=None):
        if row_tuple is not None:
            self.row_tuple = row_tuple
        else:
            currtime = int(time.time())
            self.row_tuple = {
                "src": src,
                "href": href,
                "image_size": image_size,
                "image_height": image_height,
                "image_width": image_width,
                "author": author,
                "author_id": author_id,
                "floor_num": floor_num,
                "create_time": create_time,
                "insert_time": currtime,
                "crawled": 0,
            }

    def crawl(self, drop_zone):
        pass

