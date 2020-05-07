"""

Main Screen Turn On

"""
import os, sys
abspath = os.path.abspath(__file__)
os.chdir(os.path.dirname(abspath))
from src.ingest import threadrunner
from src.ingest import authrunner
from src.ingest import imrunner
from src.ingest.selenium import Selenium


def selenium_wrap(func):
    def wrapper(*args, **kwargs):
        if len(args) == 1 and args[0] == 'help':
            help(func)
            sys.exit()
        try:
            result = func(*args, **kwargs)
        finally:
            shutdown()
        return result
    return wrapper


def shutdown():
    if Selenium.is_initiated():
        print("Shutting down initiated selenium instance")
        ff = Selenium.get_instance()
        ff.quit()


def main(args):
    ARGS_SELECT = {
        'get_threads': threadrunner.get_threads,
        'get_random_images': authrunner.get_random_images,
        'get_id_images': authrunner.get_id_images,
        'loadrandom': imrunner.load_random_images,
        'load_id_images': imrunner.load_id_images,
        'score_id': imrunner.score_id,
    }
    if len(args) > 1:
        if args[1] in ARGS_SELECT:
            func = ARGS_SELECT[args[1]]
            func_args = args[2:]
            selenium_wrap(func)(*func_args)
        elif args[1] == "help":
            print("Available functions:")
            for k, v in ARGS_SELECT.items():
                print("\t{}".format(k))
        else:
            sys.exit("Cannot find corresponding function")
    else:
        sys.exit("Nothing to do")


if __name__ == "__main__":
    main(sys.argv)
