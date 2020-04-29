from sqlitedao import ColumnDict, SqliteDao

DB_NAME = "hard.shelve"
dao = SqliteDao.get_instance(DB_NAME)

def create_tables():
    if not dao.is_table_exist("threads"):
        create_threads()
    if not dao.is_table_exist("images"):
        create_images()
    # 7 manual index + primary key index
    assert len(dao.get_schema("*", "index")) == 7
    return dao

def create_threads():
    # Create threads table
    columns = ColumnDict()\
        .add_column("href", "text", "primary key")\
        .add_column("replies", "integer", "not null")\
        .add_column("title", "text")\
        .add_column("author", "text")\
        .add_column("author_id", "text")\
        .add_column("create_time", "text")\
        .add_column("insert_time", "integer")\
        .add_column("update_time", "integer")\
        .add_column("update_count", "integer")\
        .add_column("crawled", "tinyint")
    index = {"author_index": ["author"], "author_id_index": ["author_id"]}
    dao.create_table("threads", columns, index)

def create_images():
    columns = {
        "href": "text",
        "src": "text",
        "image_size": "integer",
        "image_width": "integer",
        "author": "text",
        "author_id": "text",
        "changed_size": "tinyint",
        "data_pid": "integer",
        "floor_num": "integer",
        "create_time": "text",
        "insert_time": "integer"
    }
    index = {
        "href_index": ["href"],
        "author_index": ["author"],
        "author_id_index": ["author_id"],
        "data_pid_index": ["data_pid"]
    }
    dao.create_table("images", columns, index)
