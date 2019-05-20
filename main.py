#!/usr/bin/env python
# -*- encoding=utf8 -*-

__author__ = "Minni"

from poco_function import *
from config import *

# 上页中的商品名，为检查是否在翻页后重复之用
goods_titles = []
goods_obj_list = []

if __name__ == '__main__':
    # 分享口令的汇总列表
    share_list = load_list(DB)
    # 页面数
    scroll_pages = 1

    print(exec_cmd((adb_run_clipper)))
    start_time = time.process_time()

    while True:
        print("[信息] 当前为第{}页".format(scroll_pages))
        goods_obj_list = get_goods_objs(goods_titles)
        goods_titles = get_goods_title(goods_obj_list)

        print("[信息] 本页发现{}个商品。".format(len(goods_titles)))
        share_list = walk_detail_pages(goods_obj_list, share_list)


        if not is_ending():
            scroll_pages += 1
            poco().scroll(percent=scroll_percent, duration=scroll_duration)
        else:
            break

        # 调试时限制翻页数用，正式运行时记得注释掉
        # if scroll_pages >= 2:
        #     break

    print("It's DONE!\n {} records saved.".format(len(share_list)))
