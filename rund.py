"""

Main Screen Turn On

"""

from src.dao import create
from src.ingest import threadrunner
from src.ingest.selenium import Selenium
import sys
import sqlite3

def main(args):
    if len(args) > 1:
        if args[1] in ARGS_SELECT:
            func = ARGS_SELECT[args[1]]
            func_args = args[2:]
            func(*func_args)
        else:
            sys.exit("Cannot find corresponding function")
    else:
        sys.exit("Nothing to do")


def thread_helper(dao, thread):
    try:
        dao.insert_item(thread)
        return "NEW_ITEM"
    except sqlite3.IntegrityError:
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


def get_threads(limit=50000):
    if type(limit) is not int:
        limit = int(limit)
    try:
        dao = create.create_tables()
        threadgen = threadrunner.runthreads(limit)
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
    except Exception as e:
        print("Encountered exception: {}".format(e))
    finally:
        print("Total of {} threads stored".format(dao.get_row_count("threads")))
        shutdown()


def shutdown():
    ff = Selenium.get_instance()
    ff.quit()


if __name__ == "__main__":
    args = sys.argv
    ARGS_SELECT = {
        'runthreads': get_threads,
    }
    main(args)
