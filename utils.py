# -*- encoding=utf8 -*-
import subprocess


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


def save_list(filename, list):
    with open(filename, "a+", encoding="utf-8") as file:
        file.writelines([str(x) + "\n" for x in list])
