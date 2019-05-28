# -*- encoding=utf8 -*-
import subprocess
import os
import functools
import math
import time
from logfile import logger


def init_crawler_record():
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
    return crawler_record


def format_time(all_time):
    day = 24 * 60 * 60
    hour = 60 * 60
    min = 60
    if all_time < 60:
        return "%d sec" % math.ceil(all_time)
    elif all_time > day:
        days = divmod(all_time, day)
        return "%d days, %s" % (int(days[0]), format_time(days[1]))
    elif all_time > hour:
        hours = divmod(all_time, hour)
        return '%d hours, %s' % (int(hours[0]), format_time(hours[1]))
    else:
        mins = divmod(all_time, min)
        return "%d mins, %d sec" % (int(mins[0]), math.ceil(mins[1]))


def time_log(func):
    """
    测量函数执行时间的装饰函数
    :param func:
    :return:
    """

    @functools.wraps(func)
    def wrapper(*args, **kw):
        start_time = time.time()
        # logger.info('调用函数 = %s()' % func.__name__)
        result = func(*args, **kw)
        elapsed_time = time.time() - start_time
        logger.info("页面读取数据耗时 = %s" % format_time(elapsed_time))
        # print("elapsed_time: %d" % elapsed_time)
        return result

    return wrapper


# execute command, and return the output
def exec_cmd(cmd):
    text = subprocess.check_output(cmd)
    return text.decode('utf-8')


def parse_outpost(outpost):
    if outpost:
        start_flag = '"'  # 首个引号为开始截取字符位置
        start_position = outpost.find(start_flag)
        outpost = outpost[start_position + 1:-3]
    else:
        outpost = "Not Matched"
        return outpost
    return outpost


def color_similar_degree(rgb1, rgb2):
    r1, g1, b1 = rgb1
    r2, g2, b2 = rgb2
    r_mean = (r1 + r2) / 2
    r = r1 - r2
    g = g1 - g2
    b = b1 - b2
    return math.sqrt((2 + r_mean / 256) * (r ** 2) + 4 * (g ** 2) + (2 + (255 - r_mean) / 256) * (b ** 2))


def mkdir(path):
    # 去除首位空格
    path = path.strip()
    # 去除尾部 \ 符号
    path = path.rstrip("\\")

    # 判断路径是否存在
    # 存在     True
    # 不存在   False
    exists = os.path.exists(path)

    # 判断结果
    if not exists:
        # 如果不存在则创建目录
        # 创建目录操作函数
        os.makedirs(path)
        # print(path + ' 创建成功')
        return True
    else:
        # 如果目录存在则不创建，并提示目录已存在
        # print(path + ' 目录已存在')
        return False
