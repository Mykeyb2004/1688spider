import dataset

TABLE = 'origin'
db = dataset.connect('sqlite:///1688.db')
table = db[TABLE]


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
    try:
        with db as tx:
            tx[TABLE].upsert(record, ['share_text'])
        print("爬取数据已保存。")
    except Exception as e:
        print(e)
