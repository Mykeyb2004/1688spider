#!/usr/bin/env python
# -*- encoding=utf8 -*-
import sys

# 执行adb获取手机剪贴板命令
adb_get_clipboard = r"{}\{}\adb.exe -s e38c54e3 shell am broadcast -a clipper.get".format(sys.path[0], "adb")
# 启动手机app——clipper命令
adb_run_clipper = r"{}\{}\adb.exe -s e38c54e3 shell am startservice ca.zgrs.clipper/.ClipboardService".format(
    sys.path[0], "adb")
# 最短采集商品标题
SHORTEST_TITLE_LEN = 7
# 是否以更新的方式保存爬取数据
UPDATE = False
