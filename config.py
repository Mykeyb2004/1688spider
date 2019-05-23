#!/usr/bin/env python
# -*- encoding=utf8 -*-
# import logging


# 记录程序起始时间
start_time = 0
# 上翻屏幕的距离
scroll_percent = 0.7
# 上翻屏幕的滑动时间
scroll_duration = 0.4
# 翻页间隔时间
scroll_time = 3

# 执行adb获取手机剪贴板命令
adb_get_clipboard = r"D:\python\airtest\venv\lib\site-packages\airtest\core\android\static\adb\windows\adb.exe -s e38c54e3 shell am broadcast -a clipper.get"
# 启动手机app——clipper命令
adb_run_clipper = r"D:\python\airtest\venv\lib\site-packages\airtest\core\android\static\adb\windows\adb.exe -s e38c54e3 shell am startservice ca.zgrs.clipper/.ClipboardService"

# 保存数据的文件名
DB = "list.txt"
# 最短采集商品标题
SHORTEST_TITLE_LEN = 7
