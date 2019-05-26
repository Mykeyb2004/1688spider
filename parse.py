import dataset
from utils import *

db = dataset.connect('sqlite:///1688.db')
# 数据表
source_table = db['origin']
target_table = db['parse']

crawler_record = {
    "share_text": "",  # 分享口令
    "snapshot": "",  # 产品截图文件名
    "price1": "",  # 价格1
    "price2": "",  # 价格2
    "price3": "",  # 价格3
    "logistics_city": "",  # 物流城市
    "logistics_price": "",  # 物流价格
    "trade1": "",  # 交易数据
    "trade2": "",  # 交易数据
    "trade3": "",  # 交易数据
    "trade4": "",  # 交易数据
    "trade5": "",  # 交易数据
    "trade6": "",  # 交易数据
    "trade7": "",  # 交易数据
    "trade8": "",  # 交易数据
    "company": "",  # 公司名
    "years": "",  # 成立年限
    "back_rate": "",  # 回头率
    "buyer": "",  # 90天内买家
    "desc": "",  # 货描
    "respo": "",  # 响应
    "delivery": "",  # 发货
    "sign_desc": "",  # 货描符号
    "sign_respo": "",  # 响应符号
    "sign_delivery": "",  # 发货符号
    "title": ""  # 商品标题
}


def get_fields():
    return source_table.columns


def parse_record(record):
    fields = get_fields()
    crawler = init_crawler_record()
    for field in fields:
        crawler[field] = record[field]

    crawler['price1'], crawler['price2'], crawler['price3'] = parse_price(
        (crawler['price1'], crawler['price2'], crawler['price3']))
    print(crawler)
    return crawler


def parse_price(price):
    price1, price2, price3 = price
    price1 = 10
    price2 = 15
    price3 = 20

    return price1, price2, price3


def parse_trade_info():
    pass


def parse():
    # with db as tx:
    #     results = tx[SOURCE].all()
    results = source_table.all()
    print("载入数据。")
    for record in results:
        parse_record(record)
