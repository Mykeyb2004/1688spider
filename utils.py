# -*- encoding=utf8 -*-
import subprocess
import os
import functools
import math
import time


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
        print('call %s():' % func.__name__)
        result = func(*args, **kw)
        elapsed_time = time.time() - start_time
        print("elapsed_time: %s" % format_time(elapsed_time))
        return result

    return wrapper


@time_log
def now(hint):
    t = 0
    for i in range(10000000):
        t += 1
    print(hint, t)
    return 'OK'


# execute command, and return the output
def exec_cmd(cmd):
    text = subprocess.check_output(cmd)
    return text.decode('utf-8')


def parse_outpost(outpost):
    if outpost:
        start_flag = '"'  # 首个引号为开始截取字符位置
        start_postion = outpost.find(start_flag)
        outpost = outpost[start_postion + 1:-3]
    else:
        outpost = "Not Matched"
        return outpost
    return outpost


def save_list(filename, text, list):
    with open(filename, "a+", encoding="utf-8") as file:
        if (text + '\n') not in list:
            file.writelines(text + '\n')
            list.append(text)
        else:
            print("[信息] 重复记录，已跳过。")
    return list
    # file.writelines([str(x) + "\n" for x in text])


def load_list(filename):
    # 文件不存在则返回空list
    if not os.path.exists(filename):
        return []

    with open(filename, "r", encoding="utf-8") as file:
        list = file.readlines()
    return list
