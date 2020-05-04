from sqlitedao import ColumnDict, SqliteDao

DB_NAME = "hard.shelve"
dao = SqliteDao.get_instance(DB_NAME)

def get_dao():
    return dao

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
        .add_column("crawled", "tinyint")\
        .add_column("image_count", "integer")
    index = {"author_index": ["author"], "author_id_index": ["author_id"]}
    dao.create_table("threads", columns, index)

def create_images():
    columns = ColumnDict()\
        .add_column("src", "text", "primary key")\
        .add_column("href", "text", "not null")\
        .add_column("image_size", "integer")\
        .add_column("image_height", "integer")\
        .add_column("image_width", "integer")\
        .add_column("author", "text", "not null")\
        .add_column("author_id", "text", "not null")\
        .add_column("floor_num", "integer")\
        .add_column("create_time", "text")\
        .add_column("insert_time", "integer")\
        .add_column("crawled", "tinyint")\
        .add_column("uuid", "text")
    index = {
        "href_index": ["href"],
        "author_index": ["author"],
        "author_id_index": ["author_id"],
    }
    dao.create_table("images", columns, index)
