import filecmp, json, os
import hashlib, uuid, shutil
from PIL import Image
from src.dao import create
from src.dao.image import ForumImage
from src.dao.thread import ForumThread
from sqlitedao import DuplicateError


with open('conf/conf.json') as conf:
    FAIL_FILE_PATH = json.load(conf)["FAIL_FILE_PATH"]


# Main func
def recon_id(author_id, remove_duplicate=False):
    if remove_duplicate:
        remove_duplicate=True
    dao = create.get_dao()
    images = dao.get_items(ForumImage, {"author_id": author_id})
    crawled_images = [im for im in images if im.get_crawled_status() and not im.is_duplicate()]
    print("Found {} images to recon".format(len(crawled_images)))
    failed_images = []
    fubar_images = []
    for image in crawled_images:
        real_path = image.get_file_path()
        if not os.path.isfile(real_path):
            print("{} is missing".format(real_path))
            failed_images.append(image)
            continue
        if filecmp.cmp(FAIL_FILE_PATH, real_path):
            print("{} has failed".format(real_path))
            os.remove(real_path)
            failed_images.append(image)
            continue
        try:
            Image.open(real_path)
        except IOError:
            print("{} is fubar".format(real_path))
            fubar_images.append(image)
    for each in failed_images:
        each.mark_as_uncrawled()
    print("Found {} images in wrong state".format(len(failed_images)))
    if failed_images:
        dao.update_items(failed_images)
    for each in fubar_images:
        each.mark_as_duplicate()
    print("Found {} images in fubar".format(len(fubar_images)))
    if fubar_images:
        dao.update_items(fubar_images)
    reconcile_duplicates(author_id, remove_duplicate)


# Main func
def remove_id_images(author_id):
    dao = create.get_dao()
    images = dao.get_items(ForumImage, {"author_id": author_id})
    crawled_images = [im for im in images if im.get_crawled_status()]
    print("Found {} images to remove".format(len(crawled_images)))
    pardirs = set()
    for image in crawled_images:
        if image.is_duplicate():
            continue
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


def hashstr(fname):
    hash_md5 = hashlib.md5()
    with open(fname, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


def reconcile_duplicates(author_id, remove=False):
    dao = create.get_dao()
    images = dao.get_items(ForumImage, {"author_id": author_id})
    crawled_images = [im for im in images if im.get_crawled_status() and not im.is_duplicate()]
    print("Found {} images to recon".format(len(crawled_images)))
    hash_records = {}
    for image in crawled_images:
        real_path = image.get_file_path()
        hastr = hashstr(real_path)
        if hastr in hash_records:
            hash_records[hastr].append(image)
        else:
            hash_records[hastr] = [image]
    for hastr, imlist in hash_records.items():
        if len(imlist) > 1:
            print("Found duplicate imgs: {}".format(hastr))
            for image in imlist:
                print("{} belongs to {}".format(image.get_file_path(), image.get_href()))
            if remove:
                sourced = [im for im in imlist if im.get_href().startswith("/p")]
                if sourced:
                    kept = sourced.pop()
                else:
                    kept = imlist[0]
                imlist.remove(kept)
                print("Keeping: {} from {}".format(kept.get_file_path(), kept.get_href()))
                for dup in imlist:
                    os.remove(dup.get_file_path())
                    dup.mark_as_duplicate()
                dao.update_items(imlist)


def add_historic_thread(dao, author, author_id, flist):
    href = "/h/" + author_id
    title = author + "_history"
    history_thread = ForumThread(href=href, replies=365, title=title, author=author, author_id=author_id, create_time="1991-12")
    history_thread.mark_as_crawled(len(flist))
    try:
        dao.insert_item(history_thread)
    except DuplicateError:
        print("Historic thread already exists")
    add_historic_images(dao, flist, href, author, author_id)


def add_historic_images(dao, flist, href, author, author_id):
    imlist = []
    for f in flist:
        try:
            src = "history://" + f.split("/")[-1]
            image = Image.open(f)
            width, height = image.size
            size = os.stat(f).st_size
            imageria = ForumImage(src=src, href=href, image_size=size, image_width=width, image_height=height, author=author, author_id=author_id, floor_num=69, create_time="1991-12")
            imageria.mark_as_crawled()
            imageria.set_uuid(str(uuid.uuid4()))
            new_file_path = imageria.get_file_path()
            print("Moving {} to {}".format(f, new_file_path))
            shutil.move(f, new_file_path)
            imlist.append(imageria)
        except Exception as e:
            print("Operation for {} failed due to {}".format(f, e))
    if imlist:
        print("Inserting {} converted images in batches".format(len(imlist)))
        batch_size = 10
        i = 0
        while i < len(imlist):
            print("INSERT BATCH {}".format(i))
            dao.insert_items(imlist[i:i+batch_size])
            i += batch_size


# Main func
def induct_history(author_id):
    dao = create.get_dao()
    # Find all inductee
    images = dao.get_items(ForumImage, {"author_id": author_id})
    # Move forward if all author agree:
    author_set = set()
    for image in images:
        author_set.add(image.get_author())
    if len(author_set) > 1:
        print("Conflicting author information, exiting")
        return
    author = author_set.pop()
    crawled = [im for im in images if im.get_crawled_status() and not im.is_duplicate()]
    uuid_set = {im.get_uuid() for im in crawled}
    if not crawled:
        print("No crawled images belong to this author")
        return
    ops_dir = os.path.dirname(crawled[0].get_file_path())
    img_files = [f for f in os.listdir(ops_dir) if f.endswith("jpg")]
    historics = list(filter(lambda f: f.split(".jpg")[0] not in uuid_set, img_files))
    print("Found {} historic files to induct".format(len(historics)))
    if not historics:
        return
    for f in historics:
        fname = os.path.join(ops_dir, f)
        print("FILEPATH: {}".format(fname))
    if not str(input("Convert? y/n")) == "y":
        print("Not converting history today")
        return
    flist = [os.path.join(ops_dir, f) for f in historics]
    add_historic_thread(dao, author, author_id, flist)

