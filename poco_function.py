from airtest.core.api import *

auto_setup(__file__)

from poco.drivers.android.uiautomation import AndroidUiautomationPoco

poco = AndroidUiautomationPoco(use_airtest_input=True, screenshot_each_action=False)


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
            if len(title) > 8:  # 文字长度太短不是商品名，则跳过
                if title not in last_goods_titles:  # 若存在商品名重复则舍弃
                    goods_obj_list.append(obj)
    return goods_obj_list


def get_goods_title(obj_list):
    titles = []
    for obj in obj_list:
        titles.append(obj.get_text())
    return titles
