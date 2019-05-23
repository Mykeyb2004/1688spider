# -*- encoding=utf8 -*-

import datetime

from airtest.core.api import *
from poco.exceptions import PocoNoSuchNodeException

from config import *
from utils import *
from logfile import *

auto_setup(__file__)

from poco.drivers.android.uiautomation import AndroidUiautomationPoco

poco = AndroidUiautomationPoco(use_airtest_input=True, screenshot_each_action=False)

NAME = "name"
TEXT = "text"
NODE = "node"


def get_goods_objs(last_goods_titles):
    '''
    获取当前页面上全部可见的商品组件列表
    :param last_goods_titles: 上页商品名，检查翻页之后是否重名用
    :return: 返回过滤后的商品组件列表
    '''
    goods_obj_list = []

    obj_list = \
        poco("android:id/content").child("android.widget.FrameLayout").offspring(
            "com.alibaba.wireless:id/fragment_container").child("com.alibaba.wireless:id/v_loading").child(
            "android.widget.FrameLayout").child("android.widget.LinearLayout").child(
            "com.alibaba.wireless:id/cybertron_recyclerView").offspring("com.alibaba.wireless:id/v_loading").child(
            "android.widget.FrameLayout").offspring("com.alibaba.wireless:id/cybertron_recyclerView").child(
            "android.widget.FrameLayout").child("android.widget.FrameLayout").child(
            "android.widget.LinearLayout").child("android.widget.LinearLayout").child("android.widget.TextView")
    if obj_list:
        for obj in obj_list:
            title = obj.get_text()
            if len(title) > 8:  # 文字长度太短不是商品名，则跳过（筛选）
                if title not in last_goods_titles:  # 若存在商品名重复则舍弃（筛选）
                    goods_obj_list.append(obj)
    return goods_obj_list


def get_goods_title(obj_list):
    """
    获取列表中的产品名
    :param obj_list:
    :return:
    """
    titles = []
    for obj in obj_list:
        titles.append(obj.get_text())
    return titles


def walk_detail_pages(obj_list, list):
    """
    主要动作为：
    1. 遍历产品列表obj
    2. 从列表页点击进入详情页
    3. 调用详情页函数后返回到列表页

    :param obj_list:
    :param records:
    :return: 返回已遍历的总产品数
    """
    for obj in obj_list:
        print("[信息] 正在读取产品：", obj.get_text())
        page_start_time = time.process_time()  # 页面爬取启动时间
        poco.wait_for_any([obj])
        obj.click()  # 点击进入详情页

        # if not get_url():
        #     print(obj.get_text(), "未能保存链接。")

        result_list = get_url(list)

        # wait_for_QR_disappear()
        # 点击返回按钮，返回列表页
        wait_for_click("com.alibaba.wireless:id/v5_common_return", NAME, "[界面] 查找返回列表按钮", "未找到返回列表按钮")
        end_time = time.process_time()
        page_cost = end_time - page_start_time  # 单页面耗时
        cost = end_time - start_time  # 累计耗时

        # print("[信息] 累计耗时[%s]，页面耗时[%s]， 共计[%d]条数据已保存。" % (
        #     datetime.timedelta(seconds=cost), datetime.timedelta(seconds=page_cost), len(result_list)))
    return result_list


def get_url(list):
    """
    1. 点击分享按钮
    1. 点击复制分享口令按钮，获取分享产品的链接
    2. 保存产品链接到list中
    3. 保存到文件中

    :return:
    """
    timeout = 10

    # 点击“分享”按钮
    wait_for_click("com.alibaba.wireless:id/share_text", NAME, "[界面] 查找“点击分享”按钮", "[信息] 未找到分享按钮", timeout=timeout)

    # 等待出现二维码
    print("[界面] 查找二维码")
    QR_obj = poco("android:id/content").child("android.widget.FrameLayout").offspring("android.webkit.WebView").child(
        "android.view.View").child("android.view.View")[0].child("android.view.View").offspring(
        type="android.widget.Image")[-1]
    QR_obj.wait_for_appearance()

    # 点击“复制口令”按钮
    copy_obj = poco("android:id/content").child("android.widget.FrameLayout").offspring(
        "com.alibaba.wireless:id/dynamic_share_channel_layout").offspring(
        "com.alibaba.wireless:id/dynamic_share_recycler_view").child("android.widget.LinearLayout")[0].child(
        "android.widget.LinearLayout").child(name="com.alibaba.wireless:id/item_name")
    copy_obj.wait_for_appearance()
    copy_obj.click()

    # 通过adb读取剪贴板中的分享口令
    output = exec_cmd(adb_get_clipboard)
    share_text = parse_outpost(output)
    print("[信息] 获取分享口令：", share_text)
    result_list = save_list(DB, share_text, list)
    print("[信息] 累计保存%d条数据。" % len(result_list))

    # sleep(3)
    # print(QR_obj.attr('visible'))

    # sleep(0.5)
    # copy_obj.wait_for_disappearance()
    return result_list


# def wait_for_QR():
#     obj_list = poco("android:id/content").child("android.widget.FrameLayout").offspring("android.webkit.WebView").child(
#         "android.view.View").child("android.view.View")[0].child("android.view.View").offspring(
#         type="android.widget.Image")
#
#     try:
#         for i, x in enumerate(obj_list):
#             # print(x.attr("type"))
#             if i == len(obj_list) - 1:
#                 print("[界面] 正在等待出现二维码，执行点击复制口令动作...")
#             x.wait_for_appearance(60)
#     except PocoNoSuchNodeException:
#         print("[错误] 未出现二维码界面")
#         return False


def wait_for_QR_disappear():
    # 查找分享界面的外部容器
    container_obj = \
        poco("android:id/content").child("android.widget.FrameLayout").offspring("android.webkit.WebView").child(
            "android.view.View").child("android.view.View")[0].child("android.view.View")
    print("[界面] 等待二维码外部容器框架消失")
    container_obj.wait_for_disappearance(60)


def wait_for_click(obj_name, type, wait_msg, missing_msg, timeout=30, click=True):
    if type == "name":
        obj = poco(name=obj_name)
    if type == "text":
        obj = poco(text=obj_name)
    if type == "node":
        obj = poco(eval(obj_name))
    try:
        print(wait_msg)
        obj.wait_for_appearance(timeout=timeout)
    except:
        print(missing_msg)
        return False
    if click:
        obj.click()
    return True


def is_ending():
    """
    判断是否到了列表尾部

    :return: True False
    """
    # ending_obj = poco(name="com.alibaba.wireless:id/center_text", textMatches='^没有.*$')  # 通配符查找太消耗资源
    ending_obj = poco(name="com.alibaba.wireless:id/center_text", text="没有更多数据了")
    if ending_obj:
        print(ending_obj.get_text())
        return True
    else:
        return False


def QR():
    QR_obj = poco("android:id/content").child("android.widget.FrameLayout").offspring("android.webkit.WebView").child(
        "android.view.View").child("android.view.View")[0].child("android.view.View").offspring(
        type="android.widget.Image")[-1]
    return QR_obj
