from sqlitedao import TableItem
import urllib.request
import traceback
import uuid
import time
import os
import json


class ForumImage(TableItem):

    TABLE_NAME = "images"
    INDEX_KEYS = ["src"]
    with open('conf/conf.json') as conf:
        DROP_ZONE = json.load(conf)["IMSTORE"]

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

    def get_author_id(self):
        return str(self.row_tuple["author_id"])

    def get_author(self):
        return str(self.row_tuple["author"])

    def get_src(self):
        return str(self.row_tuple["src"])

    def get_uuid(self):
        if not "uuid" in self.row_tuple:
            return None
        return self.row_tuple["uuid"]

    def get_crawled_status(self):
        return bool(int(self.row_tuple["crawled"]))

    def mark_as_crawled(self):
        self.row_tuple["crawled"] = 1
        return self

    def set_uuid(self, imid):
        self.row_tuple["uuid"] = imid
        return self

    def crawl(self):
        # Get filename with UUID
        imid = self.get_uuid()
        if imid is None:
            imid = str(uuid.uuid4())
        extension = self.get_src().split(".")[-1]
        if extension != "jpg":
            raise # Just to make sure, haven't seen a single one so far
        filename = imid + ".jpg"

        # Get folder and make sure it exists
        folder = "{}_{}".format(self.get_author(), self.get_author_id())
        drop_folder = os.path.join(ForumImage.DROP_ZONE, folder)
        if not os.path.isdir(drop_folder):
            os.mkdir(drop_folder)

        # Actually make the file
        drop_target = os.path.join(ForumImage.DROP_ZONE, folder, filename)
        if os.path.isfile(drop_target):
            print("ERROR: file already crawled: {}".format(drop_target))
            self.mark_as_crawled()
            return self
        try:
            opener = urllib.request.build_opener()
            opener.addheaders = [('User-agent',"Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/43.0.2357.134 Safari/537.36")]
            urllib.request.install_opener(opener)
            urllib.request.urlretrieve(self.get_src(), drop_target)
        except e:
            print("ERROR: file download failed: {}".format(e))
            traceback.print_exc()
            return self
        self.set_uuid(imid)
        self.mark_as_crawled()
        return self


