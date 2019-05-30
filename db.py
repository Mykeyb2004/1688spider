import dataset
import time
import os


def load_table(dbfile):
    db_name = 'sqlite:///' + dbfile

    is_newfile = not os.access(dbfile, os.X_OK)
    if is_newfile:
        print("创建数据文件")
        table = creat_table(dbfile)
        return table
    else:
        print("载入数据文件")
        db = dataset.connect(db_name)
        table = db['origin']
        return table


def creat_table(dbfile):
    db_name = 'sqlite:///' + dbfile
    db = dataset.connect(db_name)
    table = db.create_table('origin', primary_id='share_text', primary_type=db.types.string(100))
    table.create_column('snapshot', db.types.string(100))
    table.create_column('price1', db.types.string(20))
    table.create_column('price2', db.types.string(20))
    table.create_column('price3', db.types.string(20))
    table.create_column('logistics_city', db.types.string(20))
    table.create_column('logistics_price', db.types.string(20))
    table.create_column('trade1', db.types.string(20))
    table.create_column('trade2', db.types.string(20))
    table.create_column('trade3', db.types.string(20))
    table.create_column('trade4', db.types.string(20))
    table.create_column('trade5', db.types.string(20))
    table.create_column('trade6', db.types.string(20))
    table.create_column('trade7', db.types.string(20))
    table.create_column('trade8', db.types.string(20))
    table.create_column('company', db.types.string(30))
    table.create_column('years', db.types.string(10))
    table.create_column('back_rate', db.types.string(10))
    table.create_column('buyer', db.types.string(10))
    table.create_column('desc', db.types.string(10))
    table.create_column('respo', db.types.string(10))
    table.create_column('delivery', db.types.string(10))
    table.create_column('sign_desc', db.types.string(10))
    table.create_column('sign_respo', db.types.string(10))
    table.create_column('sign_delivery', db.types.string(10))
    table.create_column('title', db.types.string(20))
    table.create_column('crawl_time', db.types.string(20))
    return table


def is_unique_title(text, table):
    """
    检查数据库中是否有重复的标题[title]
    :param text: 标题文本
    :param table: 数据所在的table对象
    :return: 若为真则有，为假则不存在重复标题
    """
    if table.count(title=text) > 0:
        return True
    else:
        return False


def snap_exists(text, table):
    row = table.find_one(title=text)

    if not row:  # 查不到title记录，则为新爬取记录
        return False
    else:
        print(text, "row=", row['snapshot'])
        if row['snapshot']:  # 存在之前的截图文件名
            return True
        else:  # 之前没有截图名
            return False


def save_crawler(record, table):
    # 如果是更新数据，则需将截图文件名的这个字段删除掉，以保证不会传入一个空值覆盖原数据，
    # if update:
    #     del record['snapshot']
    # 加入采集数据的时间
    record['crawl_time'] = time.strftime('%Y-%m-%d-%H-%M-%S', time.localtime(time.time()))
    table.upsert(record, ['share_text'])
