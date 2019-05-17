#!/usr/bin/env python
# -*- encoding=utf8 -*-
# import logging


# 上翻屏幕的距离
scroll_percent = 0.6
# 上翻屏幕的滑动时间
scroll_duration = 0.3
# 翻页间隔时间
scroll_time = 3

# urls链接汇总列表
urls = []
missing_goods = []

# 执行adb获取手机剪贴板命令
adb_get_clipboard = r"D:\python\airtest\venv\lib\site-packages\airtest\core\android\static\adb\windows\adb.exe -s e38c54e3 shell am broadcast -a clipper.get"
# 启动手机app——clipper命令
adb_run_clipper = r"D:\python\airtest\venv\lib\site-packages\airtest\core\android\static\adb\windows\adb.exe -s e38c54e3 shell am startservice ca.zgrs.clipper/.ClipboardService"
