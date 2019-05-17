# -*- encoding=utf8 -*-

from airtest.core.api import *

from config import *
from utils import *

auto_setup(__file__)

from poco.drivers.android.uiautomation import AndroidUiautomationPoco

poco = AndroidUiautomationPoco(use_airtest_input=True, screenshot_each_action=False)

NAME = "name"
TEXT = "text"
NODE = "node"


def get_goods_objs(last_goods_titles):
    '''
    获取当前可见页面上的全部商品组件的列表
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
    titles = []
    for obj in obj_list:
        titles.append(obj.get_text())
    return titles


def get_detail_pages(obj_list):
    for obj in obj_list:
        print("正在读取产品：", obj.get_text())
        poco.wait_for_any([obj])
        obj.click()
        if not get_url():
            print(obj.get_text(), "未能保存链接。")
            missing_goods.append(obj.get_text())
        # 点击返回按钮，返回列表页
        wait_for_click("com.alibaba.wireless:id/v5_common_return", NAME, "查找返回列表按钮", "未找到返回列表按钮")


def wait_for_click(obj_name, type, wait_msg, missing_msg, timeout=30, click=True):
    if type == "name":
        obj = poco(name=obj_name)
    if type == "text":
        obj = poco(text=obj_name)
    if type == "node":
        obj = poco(eval(obj_name))
    try:
        print(wait_msg)
        # poco.wait_for_any([obj], timeout=timeout)
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
    ending_obj = poco(name="com.alibaba.wireless:id/center_text", textMatches='^没有.*$')
    if ending_obj:
        print(ending_obj.get_text())
        return True
    else:
        return False


def get_url():
    """
    通过点击并复制短信按钮，获取分享商品的链接，将之保存到一个list中

    :return:
    """
    timeout = 10

    # 点击“分享”按钮
    wait_for_click("com.alibaba.wireless:id/share_text", NAME, "查找“点击分享”按钮", "未找到分享按钮", timeout=timeout)

    # 等待二维码生成
    wait_for_QR()

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
    print("分享口令：", share_text)
    urls.append(share_text)

    return True


def wait_for_QR():
    obj_list = poco("android:id/content").child("android.widget.FrameLayout").offspring("android.webkit.WebView").child(
        "android.view.View").child("android.view.View")[0].child("android.view.View").offspring(
        type="android.widget.Image")

    for x in obj_list:
        # print(x.attr("type"))
        print("等待出现二维码")
        x.wait_for_appearance()
