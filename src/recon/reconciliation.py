import filecmp, json, os
from src.dao import create
from src.dao.image import ForumImage


with open('conf/conf.json') as conf:
    FAIL_FILE_PATH = json.load(conf)["FAIL_FILE_PATH"]


# Main func
def recon_id(author_id):
    dao = create.get_dao()
    images = dao.get_items(ForumImage, {"author_id": author_id})
    crawled_images = [im for im in images if im.get_crawled_status()]
    print("Found {} images to recon".format(len(crawled_images)))
    failed_images = []
    for image in crawled_images:
        real_path = image.get_file_path()
        if not os.path.isfile(real_path):
            print("{} is missing".format(real_path))
            failed_images.append(image)
        if filecmp.cmp(FAIL_FILE_PATH, real_path):
            print("{} has failed".format(real_path))
            os.remove(real_path)
            failed_images.append(image)
    for each in failed_images:
        each.mark_as_uncrawled()
    print("Found {} images in wrong state".format(len(failed_images)))
    if failed_images:
        dao.update_items(failed_images)


# Main func
def remove_id_images(author_id):
    dao = create.get_dao()
    images = dao.get_items(ForumImage, {"author_id": author_id})
    crawled_images = [im for im in images if im.get_crawled_status()]
    print("Found {} images to remove".format(len(crawled_images)))
    pardirs = set()
    for image in crawled_images:
        real_path = image.get_file_path()
        pardirs.add(os.path.dirname(real_path))
        os.remove(real_path)
        image.mark_as_uncrawled()
    print("Removing {}".format(" ".join(pardirs)))
    for directory in pardirs:
        os.rmdir(directory)


# Main func
def reconcile_multiple_auth_name(limit=500):
    if type(limit) is not int:
        limit = int(limit)
    dao = create.get_dao()
    auth_ids = dao.search_table("threads", {}, group_by=["author_id"], limit=limit)
    for auth_id in auth_ids:
        images = dao.get_items(ForumImage, {"author_id": auth_id["author_id"]})
        im_set = {}
        for image in images:
            if image.get_author() in im_set:
                im_set[image.get_author()] += 1
            else:
                im_set[image.get_author()] = 1
        if len(im_set) > 1:
            print("Differences in auth_names identified: {}".format(im_set))
    
