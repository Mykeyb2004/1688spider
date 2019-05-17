# -*- encoding=utf8 -*-
import subprocess


# execute command, and return the output
def exec_cmd(cmd):
    text = subprocess.check_output(cmd)
    return text.decode('utf-8')


def parse_url(text):
    if text:
        start_flag = '"'  # 首个引号为开始截取字符位置
        start_postion = text.find(start_flag)
        text = text[start_postion + 1:-3]
    else:
        text = "Not Matched"
        return text
    return text
