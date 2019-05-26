import dataset
import time

db = dataset.connect('sqlite:///1688.db')
table = db['origin']


def is_unique_title(text):
    """
    检查数据库中是否有重复的标题[title]
    :param text: 标题文本
    :return: 若为真则有，为假则不存在重复标题
    """
    if table.count(title=text) > 0:
        return True
    else:
        return False


def save_crawler(record, update=False):
    # if not update:
    #     with db as tx:
    #         tx['origin'].insert(record)
    #     print("Insert Datas.")
    # else:
    #     with db as tx:
    #         tx['origin'].update(record, ['share_text'])
    #     print("Update Datas.")

    # 如果是更新数据，则需将截图文件名的这个字段删除掉，以保证不会传入一个空值覆盖原数据，
    if update:
        # print("已删除snapshot字段")
        del record['snapshot']
    # 加入采集数据的时间
    record['crawl_time'] = time.strftime('%Y-%m-%d-%H-%M-%S', time.localtime(time.time()))
    table.upsert(record, ['share_text'])
    print("爬取数据已保存。")
