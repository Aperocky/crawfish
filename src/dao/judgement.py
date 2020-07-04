from sqlitedao import TableItem
import time

class Judgement(TableItem):

    TABLE_NAME = "auth_judge"
    INDEX_KEYS = ["author_id"]

    def __init__(self, row_tuple=None, author_id=None, author=None, l_judge=None, x_judge=None, thread_count=None, image_count=None, avg_replies=None, update_count=None):
        if row_tuple is not None:
            self.row_tuple = row_tuple
        else:
            currtime = int(time.time())
            self.row_tuple = {
                "author_id": author_id,
                "author": author,
                "l_judge": l_judge,
                "x_judge": x_judge,
                "thread_count": thread_count,
                "image_count": image_count,
                "avg_replies": avg_replies,
                "update_count": update_count,
                "insert_time": currtime,
                "update_time": currtime,
                "judge_update_count": 0,
            }

    def update(self, thread_count, image_count, avg_replies, update_count, l_judge, x_judge):
        self.row_tuple["thread_count"] = thread_count
        self.row_tuple["image_count"] = image_count
        self.row_tuple["update_count"] = update_count
        self.row_tuple["avg_replies"] = avg_replies
        self.row_tuple["l_judge"] = l_judge
        self.row_tuple["x_judge"] = x_judge
        self.row_tuple["update_time"] = int(time.time())
        self.row_tuple["judge_update_count"] += 1
        return self

    def get_l_judge(self):
        return int(self.row_tuple["l_judge"])

    def get_x_judge(self):
        return int(self.row_tuple["x_judge"])

    def get_thread_count(self):
        return int(self.row_tuple["thread_count"])

    def get_image_count(self):
        return int(self.row_tuple["image_count"])

    def get_update_count(self):
        return int(self.row_tuple["update_count"])

    def get_avg_replies(self):
        return int(self.row_tuple["avg_replies"])
