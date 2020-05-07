from src.dao import create
from src.dao.thread import ForumThread
from src.dao.image import ForumImage
import random, math, time, sys
import socket
socket.setdefaulttimeout(30)


# Main func
def score_id(author_id, vis=True):
    """
    Determine the score of an author based on his/her thread popularity and picture count

    args:
        author_id: str - id of the author
        vis: bool - print the result to stdout
    """
    dao = create.get_dao()
    threads = dao.get_items(ForumThread, {"author_id": author_id})
    images = dao.get_items(ForumImage, {"author_id": author_id})
    replies = sum([t.get_replies() for t in threads])
    avg_popularity = replies/len(threads)
    score = math.log(len(images)+1) + (math.log(avg_popularity+1)-2)*2
    if vis:
        print("AVG_POPULARITY: {}, ASSET_COUNT: {}".format(avg_popularity, len(images)))
        print("SCORE: {}".format(score))
    return score


def load_random_images(limit=1, threshold=10):
    """
    Load images from random author who score pass threshold

    args:
        limit: int - number of authors to load from
        threshold: float - score threshold
    """
    if type(limit) is not int:
        limit = int(limit)
    if type(threshold) is not float:
        threshold = float(threshold)
    dao = create.get_dao()
    authors = dao.search_table("images", {}, group_by=["author", "author_id"])
    random.shuffle(authors)
    counter = 0
    for author in authors:
        score = score_id(author["author_id"])
        if score > threshold:
            print("CRAWLING FOR AUTHOR: {}".format(author["author"]))
            load_id_images(author["author_id"])
            counter += 1
        if counter >= limit:
            break


# Main func
def load_id_images(author_id):
    """
    Load the pictures from author to file based on info stored.

    args:
        author_id: id of the author
    """
    dao = create.get_dao()
    images = dao.get_items(ForumImage, {"author_id": author_id})
    print("Got {} assets".format(len(images)))
    imrun(dao, images)


def imrun(dao, images):
    updated_list = []
    new_images = [image for image in images if not image.get_crawled_status()]
    print("{}/{} images new".format(len(new_images), len(images)))
    counter = 0
    for image in new_images:
        updated_image = image.crawl()
        counter += 1
        sys.stdout.write(".")
        sys.stdout.flush()
        if updated_image.get_crawled_status():
            updated_list.append(updated_image)
        time.sleep(random.uniform(0.8,1.5))
        if counter >= 100:
            break
    if updated_list:
        dao.update_items(updated_list)
    print("\n{}/{} new images successfully loaded".format(len(updated_list), len(new_images)))

