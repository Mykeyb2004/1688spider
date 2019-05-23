# -*- encoding=utf8 -*-
__author__ = "Minni"

import sys
from airtest.core.api import *
# from poco.exceptions import PocoTargetRemovedException, PocoNoSuchNodeException, PocoNoSuchNodeException, \
#     InvalidOperationException, PocoTargetTimeout
from poco.drivers.android.uiautomation import AndroidUiautomationPoco
from base64 import b64decode
from PIL import Image

from config import *
from utils import *
from logfile import logger

auto_setup(__file__)
poco = AndroidUiautomationPoco(use_airtest_input=True, screenshot_each_action=False)

LIST_PAGE = 'list'
HOME_PAGE = 'home'
SEARCH_PAGE = 'search'
DETAIL_PAGE = 'detail'

PRICE_HEADER = 'price'
TRADE_INFO = 'trade_info_header'
RATING_HEADER = 'rating_header'
SELLER_INFO = 'seller_info_header'


def crawler():
    # 保存当前页商品标题，以备查重用。
    current_titles = []
    while True:
        # 获取当前页面商品列表
        goods_list = get_current_page()
        # 遍历操作每个商品（跳过重复项），进入详情页
        current_titles = walk_current_page(current_titles, goods_list)

        # 达到尾部停止翻页
        if is_ending():
            print("没有更多数据了。")
            break
        # 滚动列表页(滚动最后一项到顶部)
        scroll_list(goods_list)

    print("Done!")


def scroll_list(goods_list):
    # 获取商品列表，结构如下
    titles, goods_object_list = goods_list
    # 一种获取指定列的方法：list1 = [x[0] for x in mylist]
    # 获取商品列表中末尾项的左上角坐标，准备滚动到顶部
    print("本页商品列表项数", len(goods_object_list))
    # print(goods_object_list)
    if len(goods_object_list) > 0:
        # scroll_to_top(goods_list[-1])
        x, y = goods_object_list[-1].focus([0, 0]).get_position()
        print(x, y)
        scroll_to_top((x, y), top=0.15)
    else:
        logger.warning("商品列表长度为0，失败重试。", exc_info=True)
        return False

    return True


def walk_current_page(last_titles, goods_list):
    titles, goods = goods_list
    old_titles = []
    for i, title in enumerate(titles):
        if title not in last_titles:
            enter_detail_page(goods[i])
            old_titles.append(title)
    return old_titles


def enter_detail_page(goods):
    try:
        # 点击标题进入详情页
        goods.click()
        # 获取数据
        get_detail_data()
        # 详情页中的返回按钮（返回至列表页）
        back_btn = poco("com.alibaba.wireless:id/v5_common_return")
        back_btn.wait_for_appearance(5)
        back_btn.click()
    except Exception as e:
        print(e)
        snapshot("Error")


def get_detail_data():
    try:
        product_object = poco("com.alibaba.wireless:id/tv_detail_subject")
        product = product_object.get_text()
        product = product.strip(' ')
        print(product)
        price_exists = get_price()
        if not price_exists:
            logger.warning("[%s]无法找到价格标签，跳过采集" % product, exc_info=True)
            return False

        get_logistics()
        # get_share_text()

        check_page = 0
        trade_info_checked = False  # 保存是否扫描过交易信息
        seller_info_checked = False  # 保存是否扫描过厂家信息
        while check_page <= 2:  # 翻页3次扫描关键词
            headers = find_key_info()
            if not trade_info_checked:
                if headers[TRADE_INFO]:  # 若存在则滚动到顶部并读取
                    name, pos, key_obj = headers[TRADE_INFO]
                    if not object_in_view(TRADE_INFO, pos):
                        scroll_to_top(pos)
                    snapshot_log()
                    print("检查交易信息")

                    trade_info_checked = True
            if not seller_info_checked:
                if headers[SELLER_INFO]:
                    name, pos, key_obj = headers[SELLER_INFO]
                    if not object_in_view(SELLER_INFO, pos):
                        scroll_to_top(pos)
                    snapshot_log()
                    print("检查厂家信息")

                    seller_info_checked = True

            if trade_info_checked and seller_info_checked:
                break
            check_page += 1
            scroll_detail_page()
            print("第%d次扫描" % check_page)
    except Exception as e:
        print(e)
        snapshot("Error")
    return True


def scroll_detail_page():
    poco.swipe([0, 0.9], [0, 0.2], duration=0.6)


def find_key_info():
    headers = {TRADE_INFO: False,
               SELLER_INFO: False}

    # 查找交易信息
    trade_info_header = poco("com.alibaba.wireless:id/qx_trade_data_main_txt")
    if trade_info_header.exists():
        name = TRADE_INFO  # 信息对象名
        pos = trade_info_header.focus([0, 0]).get_position()  # 对象左上角坐标信息
        key_object = trade_info_header  # 传递对象
        headers[TRADE_INFO] = (name, pos, key_object)
    # 查找厂家信息
    seller_info_header = poco("com.alibaba.wireless:id/icon")
    if seller_info_header.exists():
        name = SELLER_INFO  # 信息对象名
        pos = seller_info_header.focus([0, 0]).get_position()  # 对象左上角坐标信息
        key_object = seller_info_header  # 传递对象
        headers[SELLER_INFO] = (name, pos, key_object)
    return headers


def scroll_to_top(poco_xy, top=0.2, duration=0.5):
    # 把指定坐标滚动到目标位置
    x, y = poco_xy
    poco.swipe(poco_xy, [x, top], duration=duration)


def get_trade_info():
    try:
        trade_30_object = poco("com.alibaba.wireless:id/qx_trade_data_maindata_txt1")
        logistics_percent_object = poco("com.alibaba.wireless:id/qx_trade_data_maindata_txt2")
        buyer_30_object = poco("com.alibaba.wireless:id/qx_trade_data_maindata_txt3")
        back_rate_30_object = poco("com.alibaba.wireless:id/qx_trade_data_subdata_txt1")
        delivery_time_object = poco("com.alibaba.wireless:id/qx_trade_data_subdata_txt2")
        order_quantity_object = poco("com.alibaba.wireless:id/qx_trade_data_subdata_txt3")
        # poco.wait_for_all(
        #     [trade_30_object, logistics_percent_object, buyer_30_object, back_rate_30_object, delivery_time_object,
        #      order_quantity_object])
        if trade_30_object.exists():
            print("30天成交：", trade_30_object.get_text())
        if logistics_percent_object.exists():
            print("可跟踪物流占比：", logistics_percent_object.get_text())
        if buyer_30_object.exists():
            print("30天买家：", buyer_30_object.get_text())
        if back_rate_30_object.exists():
            print("复购率：", back_rate_30_object.get_text())
        if delivery_time_object.exists():
            print("发货速度：", delivery_time_object.get_text())
        if order_quantity_object.exists():
            print("人均件数：", order_quantity_object.get_text())
    except Exception as e:
        print(e)
        snapshot("Error")
    return True


def get_rating_scores():
    try:
        rating_object = poco("com.alibaba.wireless:id/qx_comment_rating_score_txt")
        if rating_object.exists():
            print(rating_object.get_text())
        else:
            print("无评价记录")
    except Exception as e:
        print(e)
        snapshot("Error")


def get_seller_info():
    company_object = poco("com.alibaba.wireless:id/title")
    years_object = poco("com.alibaba.wireless:id/tv_tp_years")
    back_rate_object = poco("com.alibaba.wireless:id/back_rate")
    buyer_object = poco("com.alibaba.wireless:id/buyer")
    desc_object = poco("com.alibaba.wireless:id/value_v1")
    respo_object = poco("com.alibaba.wireless:id/value_v2")
    delivery_object = poco("com.alibaba.wireless:id/value_v3")
    poco.wait_for_all(
        [company_object, years_object, back_rate_object, buyer_object, desc_object, respo_object, delivery_object])
    print(company_object.get_text())
    print(years_object.get_text())
    print(back_rate_object.get_text())
    print(buyer_object.get_text())
    print(plus_or_minus(desc_object), desc_object.get_text())
    print(plus_or_minus(respo_object), respo_object.get_text())
    print(plus_or_minus(delivery_object), delivery_object.get_text())


def get_price():
    try:
        price_object = poco("com.alibaba.wireless:id/price_private_tip_container")
        if price_object.exists():
            print('Member price only.')
            return False
        price_object = poco("com.alibaba.wireless:id/current_range")
        if price_object.exists():
            price = price_object.get_text()
            print("1个价格区间")
            print(price)
            return 1
        price_object = poco("com.alibaba.wireless:id/textView1")
        if price_object.exists():
            print("3个价格")
            price_object2 = poco("com.alibaba.wireless:id/textView2")
            price_object3 = poco("com.alibaba.wireless:id/textView3")
            price1 = price_object.get_text()
            if price_object2.exists():
                price2 = price_object2.get_text()
            else:
                price2 = price1
            if price_object3.exists():
                price3 = price_object3.get_text()
            else:
                price3 = price2
            print(price1, price2, price3)
            return 3
        print("Can't identify price.")
        return False
    except Exception as e:
        print(e)
        snapshot("Error")


def get_logistics():
    try:
        logistics_city_object = poco("com.alibaba.wireless:id/qx_logistics_city_txt")
        logistics_price_object = poco("com.alibaba.wireless:id/qx_logistics_price_txt")
        # poco.wait_for_all([logistics_city_object, logistics_price_object])
        if logistics_city_object.exists():
            logistics_city = logistics_city_object.get_text()
        else:
            logistics_city = "物流信息不在本页"
        if logistics_price_object.exists():
            logistics_price = logistics_price_object.get_text()
        else:
            logistics_price = 0
        print(logistics_city, logistics_price)
    except Exception as e:
        print(e)
        snapshot("Error")


def get_share_text():
    try:
        share_btn = poco("com.alibaba.wireless:id/iv_detail_shared")
        share_btn.wait_for_appearance(5)
        share_btn.click()

        # 等待出现二维码后才能点击复制口令
        QR_obj = \
            poco("android:id/content").child("android.widget.FrameLayout").offspring(
                "android.webkit.WebView").child(
                "android.view.View").child("android.view.View")[0].child("android.view.View").offspring(
                type="android.widget.Image")[-1]
        QR_obj.wait_for_appearance()

        # 点击“复制口令”按钮
        copy_btn = poco("android:id/content").child("android.widget.FrameLayout").offspring(
            "com.alibaba.wireless:id/dynamic_share_channel_layout").offspring(
            "com.alibaba.wireless:id/dynamic_share_recycler_view").child("android.widget.LinearLayout")[0].child(
            "android.widget.LinearLayout").child(name="com.alibaba.wireless:id/item_name")
        copy_btn.wait_for_appearance()
        copy_btn.click()

        # 通过adb读取剪贴板中的分享口令
        output = exec_cmd(adb_get_clipboard)
        share_text = parse_outpost(output)
        print("获取分享口令：", share_text)
    except Exception as e:
        print(e)
        snapshot("Error")


def get_current_page():
    """
    获取当前页面上全部可见的商品组件列表
    :return: 返回过滤后的商品组件对象和标题文字

    """
    goods_object_list = []
    goods_title_list = []
    page_list = \
        poco("android:id/content").child("android.widget.FrameLayout").offspring(
            "com.alibaba.wireless:id/fragment_container").child("com.alibaba.wireless:id/v_loading").child(
            "android.widget.FrameLayout").child("android.widget.LinearLayout").child(
            "com.alibaba.wireless:id/cybertron_recyclerView").offspring("com.alibaba.wireless:id/v_loading").child(
            "android.widget.FrameLayout").offspring("com.alibaba.wireless:id/cybertron_recyclerView").child(
            "android.widget.FrameLayout").child("android.widget.FrameLayout").child(
            "android.widget.LinearLayout").child("android.widget.LinearLayout").child("android.widget.TextView")
    if page_list:
        for obj in page_list:
            title = obj.get_text()
            if len(title) > SHORTEST_TITLE_LEN:  # 文字长度太短不是商品名，则跳过（筛选）
                goods_object_list.append(obj)
                goods_title_list.append(title)
    return goods_title_list, goods_object_list


def plus_or_minus(poco_object):
    im = element_snapshot(poco_object)
    return color_to_sign(im)


def color_to_sign(image):
    """
    辨识红绿两色以决定前面的数值是正数还是负数
    :param image: PIL.Image对象
    :return: 正负号。若无法辨识是红色还是绿色，则返回0
    """
    # 红绿色的比照基准坐标
    pixel_xy = (59, 12)
    color = image.getpixel(pixel_xy)
    # print(color)
    # 红绿色的比照基准值
    green_arrow = (24, 185, 47)
    red_arrow = (255, 13, 30)
    # print("Green similar:", color_similar_degree(color, green_arrow))
    # print("Red similar:", color_similar_degree(color, red_arrow))
    if color_similar_degree(color, green_arrow) <= 150:
        result = -1
    elif color_similar_degree(color, red_arrow) <= 150:
        result = 1
    else:
        result = 0
        print("Can not identify color=", color, "return 0")
    # 测试取色点周围颜色的相似度
    # for xp in range(-3, 3):
    #     for yp in range(-3, 3):
    #         x_test, y_test = (x + xp), (y + yp)
    #         color_test = image.getpixel((x_test, y_test))
    #         similar_degree = color_similar_degree(color_test, (255, 13, 30))
    #         print("x,y:%s color:%s similar:%d" % ((x_test, y_test), color_test, similar_degree))
    # 观测像素坐标的测试代码
    # image.putpixel(pixel_xy, (0, 0, 0))
    # image.save('aa.jpg', image.format)
    return result


def element_snapshot(poco_object, save=False, filename="element"):
    """
    airtest目前只能对全屏截图，本函数可对指定组件截图，并返回一个PIL.Image对象。
    ps 保存临时文件再读出来的方式是影响效能的，要优化。
       计算左上角坐标的方式是无知的，肯定有我没找到原生api做到这个，可要优化。

    :param poco_object: poco对象
    :param save: 是否保存截图文件
    :param filename: 要保存的组件截图文件名
    :return: 返回PIL.Image对象
    """
    b64img, fmt = poco.snapshot(width=720)
    open('{}.{}'.format('temp', fmt), 'wb').write(b64decode(b64img))
    # TODO:载入二进制数据，生成Image对象。此处需优化，本无需保存到本地
    shot = Image.open("%s.%s" % ('temp', fmt))
    # shot = Image.frombytes('RGB', (720, 700), b64decode(b64img), 'raw')

    # 计算组件坐标
    (x, y) = poco_object.get_position()
    (w, h) = poco_object.get_size()
    (x, y) = (x - w / 2, y - h / 2)
    (xr, yr) = shot.size  # 获取图片尺寸
    x1, y1 = (int(xr * x), int(yr * y))  # 左上角图片坐标
    x2, y2 = (int(xr * (w + x)), int(yr * (h + y)))  # 右下角图片坐标

    box = (x1, y1, x2, y2)
    region = shot.crop(box)
    if save:
        region.save(filename + '.' + fmt, shot.format)
    return region


def is_ending():
    """
    判断是否到了列表尾部

    :return: True False
    """
    try:
        ending_obj = poco(name="com.alibaba.wireless:id/center_text", text="没有更多数据了")
        if ending_obj.exists():
            # print(ending_obj.get_text())
            return True
        else:
            return False
    except Exception as e:
        print(e)
        snapshot("Error")
    return False


@time_log
def which_page():
    view_obj = poco(name='com.alibaba.wireless:id/v8_search_bar_layout_iv')
    if view_obj.exists():
        return LIST_PAGE
    view_obj = poco(name='com.alibaba.wireless:id/search_navigator_scan')
    if view_obj.exists():
        return HOME_PAGE
    view_obj = poco(name='com.alibaba.wireless:id/v5_search_input_image')
    if view_obj.exists():
        return SEARCH_PAGE
    view_obj = poco(name='com.alibaba.wireless:id/title_bar_menu_1')
    if view_obj.exists():
        return DETAIL_PAGE
    return None


def snapshot(filename):
    b64img, fmt = poco.snapshot(width=720)
    path = r'%s\snap' % (sys.path[0])
    mkdir(path)
    open(r'{}\{}.{}'.format(path, filename, fmt), 'wb').write(b64decode(b64img))


def snapshot_log():
    filename = "snapshot" + time.strftime('%Y-%m-%d-%H-%M-%S', time.localtime(time.time()))
    snapshot(filename)


def object_in_view(_object, pos):
    if _object == TRADE_INFO:
        x, y = pos
        if y <= 0.815:  # 组件在底部的最低位置
            return True
    elif _object == SELLER_INFO:
        x, y = pos
        if y <= 0.753:  # 组件在底部的最低位置
            return True
    else:
        raise RuntimeError("Can't identify object in view")
    return False
