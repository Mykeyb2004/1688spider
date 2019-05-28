# coding=utf-8
import os
import time
import sys


def file_list(dirname, ext='.py'):
    """获取目录下所有特定后缀的文件
    @param dirname: str 目录的完整路径
    @param ext: str 后缀名, 以点号开头
    @return: list(str) 所有子文件名(不包含路径)组成的列表
    """
    return list(filter(
        lambda filename: os.path.splitext(filename)[1] == ext,
        os.listdir(dirname)))


# 统计一个文件的行数
def count_line(fname):
    count = 0
    for file_line in open(fname, encoding='utf-8').readlines():
        if file_line != '' and file_line != '\n':  # 过滤掉空行
            count += 1
    print(fname + ' ----', count)
    return count


if __name__ == '__main__':
    startTime = time.clock()
    file_lists = file_list(sys.path[0])
    total_line = 0
    for file_list in file_lists:
        total_line = total_line + count_line(file_list)
    print('Total lines:', total_line)
    print('Done! Cost Time: %0.2f second' % (time.clock() - startTime))
