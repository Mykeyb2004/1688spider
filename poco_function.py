from config import *
from airtest.core.api import *

auto_setup(__file__)

from poco.drivers.android.uiautomation import AndroidUiautomationPoco

poco = AndroidUiautomationPoco(use_airtest_input=True, screenshot_each_action=False)

NAME = "name"
TEXT = "text"
NODE = "node"


def get_goods_objs(last_goods_titles):
    '''
    获取全部商品组件的列表
    :param last_goods_title: 上页商品名，检查翻页之后是否重名用
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
        print("touch", obj.get_text())
        poco.wait_for_any([obj])
        obj.click()
        if not get_url():
            print(obj.get_text(), "未能保存链接。")
            missing_goods.append(obj.get_text())
        keyevent("BACK")


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

    # 点击“短信”按钮
    wait_for_click("短信", TEXT, "查找“短信”按钮", "未找到“短信”按钮", timeout=timeout)

    # 进入系统短信界面
    retries = 0
    while retries < 3:  # 未出现短信界面时，重试的次数
        if not wait_for_click("com.android.mms:id/embedded_text_editor", NAME, "查找手机短信界面", "未出现短信界面", timeout=timeout,
                              click=False):
            if retries == 0:
                print("第", retries + 1, "次重试点击短信按钮")
            wait_for_click("短信", TEXT, "查找“短信”按钮", "未找到“短信”按钮", timeout=timeout)
            retries += 1
        else:
            break  # 已出现短信界面
    # 读取短信界面中的分享链接信息，保存到urls列表中
    sms_text = poco(name="com.android.mms:id/embedded_text_editor")
    urls.append(sms_text.get_text())

    # 退出系统短信界面
    wait_for_click("com.android.mms:id/home", NAME, "查找短信退出按钮", "未找到短信退出按钮", timeout=timeout)

    # 点击“确定”按钮，退出编辑手机短信
    wait_for_click("确定", TEXT, "查找确定退出短信界面的按钮", "未找到确定退出短信界面的按钮", timeout=timeout)

    return True
