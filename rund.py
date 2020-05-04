"""

Main Screen Turn On

"""

from src.dao import create
from src.ingest import threadrunner
from src.ingest import authrunner
from src.ingest.selenium import Selenium
import sys
import random

# ============================================
# FOR INGESTING THREADS
# ============================================

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
                record[threadrunner.thread_helper(dao, thread)] += 1
            print("Batch record: {}".format(record))
    except Exception as e:
        print("Encountered exception: {}".format(e))
    finally:
        print("Total of {} threads stored".format(dao.get_row_count("threads")))
        shutdown()

# ============================================
# FOR GETTING INDIVIDUAL THREADS
# ============================================

def get_authors(limit=100, amount=5, threshold=10):
    if type(limit) is not int:
        limit = int(limit)
    if type(threshold) is not int:
        threshold = int(threshold)
    if type(amount) is not int:
        amount = int(amount)
    dao = create.get_dao()
    besties = dao.search_table("threads", {}, group_by=["author_id", "author"], limit=limit)
    random.shuffle(besties) # Add randomness
    counter = 0
    try:
        for each in besties:
            spoils = authrunner.get_author_aggregate_stat(dao, each["author_id"], False)
            score = authrunner.score(spoils["data"])
            if score["total"] > threshold:
                print("RUNNING INGEST FOR AUTHOR: {}".format(each["author"]))
                print(spoils["data"])
                summary = authrunner.run_threads(spoils["threads"])
                print("NEW RESULTS FOR {}: {}".format(each["author"], summary))
                counter += 1
            if counter >= amount:
                break
    finally:
        shutdown()

# ============================================
# TEST
# ============================================

def test_func():
    try:
        dao = create.get_dao()
        spoils = authrunner.get_author_aggregate_stat(dao, "907046376", True)
        score = authrunner.score(spoils["data"])
        print(score)
        result = authrunner.run_threads(spoils["threads"])
        print(result)
    finally:
        shutdown()


def shutdown():
    print("Selenium shutting down")
    ff = Selenium.get_instance()
    ff.quit()
    print("Selenium shuts down")


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


if __name__ == "__main__":
    args = sys.argv
    ARGS_SELECT = {
        'runthreads': get_threads,
        'runauths': get_authors,
        'runtest': test_func,
    }
    main(args)
