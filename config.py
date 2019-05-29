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

# 截图文件保存路径
SNAP_PATH = ''
# 保存采集数据的table对象
TABLE = None
# 累计保存记录条数
TOTAL_RECORDS = 0
# 强制更新模式，表示不检查标题是否在数据库中，直接更新数据
FORCE_UPDATE = False
