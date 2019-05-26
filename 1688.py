#!/usr/bin/env python
# -*- encoding=utf8 -*-

__author__ = "Minni"

from ui_crawler import *

if __name__ == '__main__':
    # 启动手机剪贴板服务
    print("Start app clipboard ...")
    exec_cmd(adb_run_clipper)
    crawler()
