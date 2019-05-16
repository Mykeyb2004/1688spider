from config import *
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
        obj.click()
        if not get_url():
            print(obj.get_text(), "未能保存链接。")
        keyevent("BACK")


def get_url():
    timeout = 30

    # 点击“分享”按钮
    share_btn = poco("com.alibaba.wireless:id/share_text")
    try:
        print("正在等待点击分享按钮")
        poco.wait_for_any([share_btn], timeout=timeout)
    except:
        print("未找到分享按钮")
        return False
    share_btn.click()

    # 点击“短信”按钮
    copy_url = poco(text="短信")
    try:
        print("正在等待点击短信按钮")
        poco.wait_for_any([copy_url], timeout=timeout)
    except:
        print("未找到短信按钮")
        return False
    copy_url.click()

    # 进入系统短信界面
    sms_text = poco(name="com.android.mms:id/embedded_text_editor")
    try:
        print("正在等待出现复制完成信息")
        poco.wait_for_any([sms_text], timeout=timeout)
    except:
        print("未找到短信编辑组件")
        return False
    urls.append(sms_text.get_text())

    # 退出系统短信界面
    keyevent("BACK")
    sleep(0.3)
    keyevent("BACK")

    # 点击“确定”按钮，放弃编辑手机短信
    quit_btn = poco(text="确定")
    try:
        print("正在放弃编辑短信")
        poco.wait_for_any([quit_btn], timeout=timeout)
    except:
        print('未找到短信退出的确定按钮')
        return False
    quit_btn.click()
    return True
