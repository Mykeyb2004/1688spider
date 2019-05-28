import dataset
import re
from utils import *
from progressbar import *

target_db = dataset.connect('sqlite:///parsed1688.db')
target_table = target_db['parse']


def parse():
    config = load_config('config.json')
    source_dir = config['dir']
    keyword = config['keyword']

    source_db = dataset.connect('sqlite:///' + source_dir + keyword + '.db')
    source_table = source_db['origin']

    results = source_table.all()
    total = source_table.count()
    fields = get_fields(source_table)

    print("载入数据...")
    pbar = ProgressBar().start()
    for i, record in enumerate(results):
        pbar.update(int((i / (total - 1)) * 100))
        save_parsed_record(record, keyword, fields)
    pbar.finish()


def save_parsed_record(record, keyword, fields):
    """
    解析原始数据记录，保存到新的数据表中
    :param record: 传入的原数据结构
    :param keyword: 搜索的关键词
    :param fields: 字段列表
    :return: 无返回
    """
    crawler = {}
    # 将一条记录的所有字段读入dict对象
    for field in fields:
        crawler[field] = record[field]

    # 准备拼装新的dict对象保存到数据库中
    save_record = {}
    # 分享口令
    save_record['share_text'] = crawler['share_text']
    # 截图文件名
    save_record['snapshot'] = crawler['snapshot']
    # 解析价格
    save_record['price1'], save_record['price2'], save_record['price3'] = parse_price(crawler['price1'],
                                                                                      crawler['price2'],
                                                                                      crawler['price3'])
    save_record['logistics_city'] = crawler['logistics_city']
    # 解析物流价格
    save_record['logistics_price'] = parse_logistics_price(crawler['logistics_price'])
    # 解析并对齐交易信息
    trade_info_list = []
    trade_info_list.append(crawler['trade1'])
    trade_info_list.append(crawler['trade2'])
    trade_info_list.append(crawler['trade3'])
    trade_info_list.append(crawler['trade4'])
    trade_info_list.append(crawler['trade5'])
    trade_info_list.append(crawler['trade6'])
    trade_info_list.append(crawler['trade7'])
    trade_info_list.append(crawler['trade8'])
    trade_info_dict = parse_trade_info(trade_info_list)
    save_record['orders_30'] = trade_info_dict.get('orders_30', None)
    save_record['logistics'] = trade_info_dict.get('logistics', None)
    save_record['buyers_30'] = trade_info_dict.get('buyers_30', None)
    save_record['taobao'] = trade_info_dict.get('taobao', None)
    save_record['rebuy_30'] = trade_info_dict.get('rebuy_30', None)
    save_record['delivery_time'] = trade_info_dict.get('delivery_time', None)
    save_record['order_quantity'] = trade_info_dict.get('order_quantity', None)
    save_record['one_order'] = trade_info_dict.get('one_order', None)
    # 公司名
    save_record['company'] = crawler['company']
    # 成立年限
    save_record['years'] = parse_years(crawler['years'])
    # 回头率
    save_record['back_rate'] = parse_back_rate(crawler['back_rate'])
    # 90天内买家
    save_record['buyer'] = int(parse_number(crawler['buyer']))
    # 货描
    if crawler['desc']:
        save_record['desc'] = parse_number(crawler['desc']) * float(crawler['sign_desc'])
    else:
        save_record['desc'] = None
    # 响应
    if crawler['respo']:
        save_record['respo'] = parse_number(crawler['respo']) * float(crawler['sign_respo'])
    else:
        save_record['respo'] = None
    # 发货
    if crawler['delivery']:
        save_record['delivery'] = parse_number(crawler['delivery']) * float(crawler['sign_delivery'])
    else:
        save_record['delivery'] = None
    save_record['title'] = crawler['title']
    save_record['keyword'] = keyword
    title, url = parse_share_text(crawler['share_text'])
    save_record['url'] = url
    # print(save_record)
    target_table.upsert(save_record, ['share_text'])


def parse_back_rate(item):
    if item == '暂无数据':
        return -100
    else:
        return parse_number(item)


def parse_price(price1_string, price2_string, price3_string):
    price_list = []  # 暂存所有价格

    def price_to_list(item):
        vlist = []
        if item == '' or item is None:
            return []
        item = item.replace('¥', '')
        item = item.replace('-', '~')  # 替换掉不规则的连接符合
        position = item.find('~')
        if position > 0:
            p1 = re.findall(r"\d+\.?\d*", item)[0]
            p2 = re.findall(r"\d+\.?\d*", item)[1]
            vlist.append(float(p1))
            vlist.append(float(p2))
        else:
            vlist.append(float(item))
        return vlist

    for x in price_to_list(price1_string):
        price_list.append(x)
    for x in price_to_list(price2_string):
        price_list.append(x)
    for x in price_to_list(price3_string):
        price_list.append(x)

    price_list.sort(reverse=True)
    count = len(price_list)
    if count == 0:
        return None, None, None
    elif count == 1:
        return price_list[0], None, None
    elif count == 2:
        return price_list[0], price_list[1], None
    elif count == 3:
        return price_list[0], price_list[1], price_list[2],


def parse_logistics_price(item):
    if item == '卖家包邮':
        price = 0
    elif item == '运费待议':
        price = 999
    elif item.startswith('快递'):
        item = item.replace('快递 ¥', '')
        item = item.replace(',', '')
        price = float(item)
    else:
        price = 100000
    return price


def parse_years(item):
    return int(re.findall('\d+', item)[0])


def parse_trade_info(trade_info_list):
    """

    :param trade_info_list:
    :return: 返回交易信息的dict对象
    """
    # 近30天成交26个  orders_30
    # 可跟踪物流占比100.00%    logistics
    # 近30天采购3人  buyers_30
    # 淘宝会员占比33.33%  taobao
    # 复购率0.00%  rebuy_30
    # 72小时以上发货  delivery_time
    # 人均件数8  order_quantity
    # 一件成交0.00% one_order
    trade_info = {}
    for item in trade_info_list:
        if item is None:
            break
        if item.startswith('近30天成交'):
            string = re.findall('\d+', item)[-1]
            trade_info['orders_30'] = float(string)
        elif item.startswith('可跟踪物流占比'):
            trade_info['logistics'] = parse_number(item)
        elif item.startswith('近30天采购'):
            value = re.findall('\d+', item)[-1]
            trade_info['buyers_30'] = int(value)
        elif item.startswith('淘宝会员占比'):
            trade_info['taobao'] = parse_number(item)
        elif item.startswith('复购率'):
            trade_info['rebuy_30'] = parse_number(item)
        elif item.endswith('发货'):
            trade_info['delivery_time'] = item
        elif item.startswith('人均件数'):
            trade_info['order_quantity'] = int(re.findall('\d+', item)[-1])
        elif item.startswith('一件成交'):
            trade_info['one_order'] = parse_number(item)
    return trade_info


def parse_number(item):
    """
    分解字符串中的百分号数字（只取字符串中首次出现的数字）
    :param item: 待解析字符
    :return: 百分比，但单位放大了100倍
    """
    digital = re.findall(r"\d+\.?\d*", item)
    return float(digital[0])


def parse_share_text(text):
    if not text:
        return [], []

    title_end_flag = "】"
    url_start_flag = "查看："

    title_position = text.find(title_end_flag)
    title = text[1:title_position]

    url_postion = text.find(url_start_flag) + len(url_start_flag)
    url = text[url_postion:]
    # 仅仅截取https的链接，后面可能会有其他字符，全部去掉。链接长度仅为46
    url = url[:46]

    return title, url


def get_fields(table):
    return table.columns
