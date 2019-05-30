# -*- encoding=utf8 -*-
__author__ = "Minni"

from airtest.core.api import *
from poco.drivers.android.uiautomation import AndroidUiautomationPoco
from base64 import b64decode
from PIL import Image

from config import *
from utils import *
from logfile import logger
from db import *

auto_setup(__file__)
poco = AndroidUiautomationPoco(use_airtest_input=True, screenshot_each_action=False)

PRICE_HEADER = 'price'
TRADE_INFO = 'trade_info_header'
RATING_HEADER = 'rating_header'
SELLER_INFO = 'seller_info_header'


def crawler():
    config = load_config('config.json')
    base_dir = config['dir']
    keyword = config['keyword']
    snap_dir = base_dir + keyword
    db_name = keyword + '.db'
    global SNAP_PATH
    SNAP_PATH = snap_dir
    global FORCE_UPDATE
    FORCE_UPDATE = config['force_update']

    print("扫描关键词 = %s" % keyword)
    print("数据储存目录 = %s" % base_dir)
    print("截图储存目录 = %s" % snap_dir)
    print("数据库文件名 = %s" % db_name)
    print("强制更新模式 = ", FORCE_UPDATE)
    mkdir(base_dir)
    global TABLE
    TABLE = load_table(base_dir + db_name)

    # 保存当前页商品标题，以备查重用。
    current_titles = []
    retry_times = 0
    while True:
        # 获取当前页面商品列表
        goods_list = get_current_page_objects()
        # 遍历操作每个商品（跳过重复项），进入详情页
        current_titles = walk_current_page(current_titles, goods_list)

        # 达到尾部停止翻页
        if is_ending():
            print("没有更多数据了。")
            break
        # 滚动列表页(滚动最后一项到顶部)
        if not scroll_list(goods_list):
            retry_times += 1
        if retry_times > 4:
            print("页面异常，退出本次采集。")
            break
    print("Done!")


def scroll_list(goods_list):
    # 获取商品列表，结构如下
    titles, goods_object_list = goods_list
    # 获取商品列表中末尾项的左上角坐标，准备滚动到顶部
    print("本页扫描到%d个商品" % len(goods_object_list))
    if len(goods_object_list) > 0:
        x, y = goods_object_list[-1].focus([0, 0]).get_position()
        scroll_to_top((x, y), top=0.15)
    else:
        logger.warning("商品列表长度为0，失败重试。")
        return False
    return True


def walk_current_page(last_titles, goods_list):
    titles, goods = goods_list
    old_titles = []  # 上一页扫描的商品标题
    for i, title in enumerate(titles):
        if title not in last_titles:  # 不重复爬取上个页面中已爬取过的标题
            if FORCE_UPDATE:
                # 无论之前数据库中是否存在该title，均扫描一遍以更新数据。
                enter_detail_page(goods[i])
            else:
                # 如果数据库中存在标题，则跳过扫描
                if not is_unique_title(title, TABLE):
                    enter_detail_page(goods[i])
                else:
                    print("已扫描过该商品，跳过扫描")
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
        back_btn.wait_for_appearance(15)
        back_btn.click()
    except Exception as e:
        capture_error(e)
        print("enter_detail_page")


@time_log
def get_detail_data():
    # crawler_record = init_crawler_record()
    crawler_record = {}  # 初始化采集数据的dict对象
    trade_data = []
    seller_info = ()

    try:
        product_object = poco("com.alibaba.wireless:id/tv_detail_subject")
        product = product_object.get_text()
        product = product.strip(' ')
        logger.info("扫描商品 = {}".format(product))

        price1, price2, price3 = get_price()
        logistics_city, logistics_price = get_logistics()

        # 获取分享口令和商品截图
        share_text, snap_filename = get_share_text(product, TABLE)
        crawler_record['share_text'] = share_text
        if snap_filename is not None:
            crawler_record['snapshot'] = snap_filename

        check_page_no = 0  # 详情页当前页面数
        trade_info_checked = False  # 保存是否扫描过交易信息
        seller_info_checked = False  # 保存是否扫描过厂家信息
        while check_page_no <= 2:  # 翻页3次扫描关键词
            headers = find_key_info()
            if not trade_info_checked:
                if headers[TRADE_INFO]:  # 若存在但不是完整的在页面中，则滚动到顶部
                    name, pos, key_obj = headers[TRADE_INFO]
                    if not object_in_view(TRADE_INFO, pos):
                        print("找到部分交易数据，翻动到顶部")
                        scroll_to_top(pos, top=0.2)
                        sleep(0.5)  # 滑动后需要暂停，否则无法按到按钮
                    logger.info("读取交易信息")
                    # 点击查看按钮，读取详细交易信息
                    trade_data = get_trade_info()
                    trade_info_checked = True
            headers = find_key_info()
            if not seller_info_checked:
                if headers[SELLER_INFO]:  # 回传是否存在组件
                    name, pos, key_obj = headers[SELLER_INFO]
                    if not object_in_view(SELLER_INFO, pos):
                        scroll_to_top(pos, top=0.3)
                    logger.info("读取厂家信息")
                    seller_info = get_seller_info()
                    seller_info_checked = True
            # 都找到了，退出本次扫描
            if trade_info_checked and seller_info_checked:
                break
            # 先找到了厂家，则说明没有交易信息，直接退出扫描
            if (trade_info_checked is False) and (seller_info_checked is True):
                break
            check_page_no += 1
            scroll_detail_page()  # 滚动一整页

        # 组合采集的数据
        crawler_record['title'] = product
        crawler_record['share_text'] = share_text
        # crawler_record['snapshot'] = snap_filename
        crawler_record['price1'] = price1
        crawler_record['price2'] = price2
        crawler_record['price3'] = price3
        crawler_record['logistics_city'] = logistics_city
        crawler_record['logistics_price'] = logistics_price
        # 保存交易信息的列表
        for i, trade in enumerate(trade_data):
            trade_keyword = 'trade' + str(i + 1)
            crawler_record[trade_keyword] = trade
        # 解包已读取的厂家信息数据
        crawler_record['company'], crawler_record['years'], crawler_record['back_rate'], crawler_record['buyer'], \
        crawler_record['desc'], crawler_record['respo'], crawler_record['delivery'], crawler_record['sign_desc'], \
        crawler_record['sign_respo'], crawler_record['sign_delivery'] = seller_info
        # if crawler_record['desc'] is None:
        #     crawler_record['desc'] = ''
        # if crawler_record['respo'] is None:
        #     crawler_record['respo'] = ''
        # if crawler_record['delivery'] is None:
        #     crawler_record['delivery'] = ''
        save_crawler(crawler_record, TABLE)
    except Exception as e:
        capture_error(e)
        print("get_detail_data")


def get_trade_info():
    trade_data = []

    # 点击查看交易数据详情的右边按钮
    show_btn = poco("com.alibaba.wireless:id/qx_right_arrow")
    show_btn.click()
    try:
        # 读取交易数据
        msg1 = poco("com.alibaba.wireless:id/lv_board").offspring("com.alibaba.wireless:id/title")
        for x in msg1:
            trade_data.append(x.get_text())
        msg2 = poco("com.alibaba.wireless:id/lv_board").offspring("com.alibaba.wireless:id/subTitle")
        for x in msg2:
            trade_data.append(x.get_text())
    except Exception as e:
        capture_error(e)
        print("get_trade_info")
    # 点击交易数据详情退出按钮
    quit_btn = poco("com.alibaba.wireless:id/btn_board")
    quit_btn.click()
    return trade_data


def get_seller_info():
    company_object = poco("com.alibaba.wireless:id/title")[-1]  # 因为有多个相同的标识，其中最后一个可能是公司名
    years_object = poco("com.alibaba.wireless:id/tv_tp_years")
    back_rate_object = poco("com.alibaba.wireless:id/back_rate")
    buyer_object = poco("com.alibaba.wireless:id/buyer")
    desc_object = poco("com.alibaba.wireless:id/value_v1")
    respo_object = poco("com.alibaba.wireless:id/value_v2")
    delivery_object = poco("com.alibaba.wireless:id/value_v3")
    company = company_object.get_text()
    years = years_object.get_text()
    back_rate = back_rate_object.get_text()
    buyer = buyer_object.get_text()
    desc = desc_object.get_text()
    respo = respo_object.get_text()
    delivery = delivery_object.get_text()
    sign_desc = plus_or_minus(desc_object)
    sign_respo = plus_or_minus(respo_object)
    sign_delivery = plus_or_minus(delivery_object)
    return company, years, back_rate, buyer, desc, respo, delivery, sign_desc, sign_respo, sign_delivery


def get_price():
    price = ""
    price2 = ""
    price3 = ""
    try:
        price_object = poco("com.alibaba.wireless:id/price_private_tip_container")
        if price_object.exists():
            logger.warning('Member price only.')
            return "", "", ""
        price_object = poco("com.alibaba.wireless:id/current_range")
        if price_object.exists():
            price = price_object.get_text()
            return price, "", ""
        price_object1 = poco("com.alibaba.wireless:id/textView1")
        if price_object1.exists():
            price_object2 = poco("com.alibaba.wireless:id/textView2")
            price_object3 = poco("com.alibaba.wireless:id/textView3")
            price1 = price_object1.get_text()
            price = price1
            if price_object2.exists():
                price2 = price_object2.get_text()
            if price_object3.exists():
                price3 = price_object3.get_text()
    except Exception as e:
        capture_error(e)
        print("get_price")
    logger.info("已读取价格信息。")
    return price, price2, price3


def get_logistics():
    try:

        logistics_city_object = poco("com.alibaba.wireless:id/qx_logistics_city_txt")
        logistics_price_object = poco("com.alibaba.wireless:id/qx_logistics_price_txt")
        if logistics_city_object.exists():
            logistics_city = logistics_city_object.get_text()
        else:
            logistics_city = "无"
        if logistics_price_object.exists():
            logistics_price = logistics_price_object.get_text()
        else:
            logistics_price = 0
        logger.info("已读取物流信息。")
        return logistics_city, logistics_price
    except Exception as e:
        capture_error(e)
        print("get_logistics")


def get_share_text(title, table):
    share_text = ''
    snap_filename = None
    try:
        # 点击分享按钮
        share_btn = poco("com.alibaba.wireless:id/iv_detail_shared")
        share_btn.wait_for_appearance(5)
        share_btn.click()

        # 等待出现二维码后才能点击复制口令
        QR_obj = \
            poco("android:id/content").child("android.widget.FrameLayout").offspring(
                "android.webkit.WebView").child(
                "android.view.View").child("android.view.View")[0].child("android.view.View").offspring(
                type="android.widget.Image")
        poco.wait_for_all(list(QR_obj), timeout=20)
        sleep(0.5)

        # 截图
        # 若不在数据库中，则为新增爬取数据，需传递截图的文件名
        if not snap_exists(title, table):
            snap_filename = get_goods_snapshot(SNAP_PATH)
        else:
            snap_filename = None

        # 点击“复制口令”按钮
        copy_btn = poco("android:id/content").child("android.widget.FrameLayout").offspring(
            "com.alibaba.wireless:id/dynamic_share_channel_layout").offspring(
            "com.alibaba.wireless:id/dynamic_share_recycler_view").child("android.widget.LinearLayout")[0].child(
            "android.widget.LinearLayout").child(name="com.alibaba.wireless:id/item_name")
        copy_btn.wait_for_appearance()
        copy_btn.click()
        # # 再点击一次，防止点击复制按钮失效
        # if copy_btn.exists():
        #     copy_btn.click()

        # 通过adb读取剪贴板中的分享口令
        output = exec_cmd(adb_get_clipboard)
        share_text = parse_outpost(output)
        logger.info("读取分享口令")
    except Exception as e:
        capture_error(e)
        print("get_share_text")

    return share_text, snap_filename


def get_current_page_objects():
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


def scroll_detail_page():
    poco.swipe([0, 0.9], [0, 0.2], duration=0.6)


def find_key_info():
    """
    扫描屏幕内是否存在交易信息、厂家信息等组件
    :return: 返回组件的名字、坐标、对象信息
    """
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
    # print(headers)
    return headers


def scroll_to_top(poco_xy, top=0.2, duration=0.5):
    # 把指定坐标滚动到目标位置
    x, y = poco_xy
    poco.swipe(poco_xy, [x, top], duration=duration)


def plus_or_minus(poco_object):
    im = element_snapshot(poco_object)
    return color_to_sign(im)


def color_to_sign(image):
    """
    辨识红绿两色以决定前面的数值是正数还是负数
    :param image: PIL.Image对象
    :return: 正负号。若无法辨识是红色还是绿色，则返回0
    """
    # 红绿色比照的基准坐标
    pixel_xy = (59, 12)
    color = image.getpixel(pixel_xy)
    # 红绿色比照的基准rgb值
    green_arrow = (24, 185, 47)
    red_arrow = (255, 13, 30)
    # print("Green similar:", color_similar_degree(color, green_arrow))
    # print("Red similar:", color_similar_degree(color, red_arrow))
    # print("Color:", color)
    if color_similar_degree(color, green_arrow) <= 150:
        return -1
    if color_similar_degree(color, red_arrow) <= 150:
        return 1
    logger.warning("未识别红绿色color={}，可能为空".format(color))
    return 0


def get_goods_snapshot(path):
    """
    保存商品图片
    :return: 返回保存的文件名
    """
    # path = r'%s\%s' % (sys.path[0], 'snap')
    mkdir(path)
    filename = path + r"\snapshot" + time.strftime('%Y-%m-%d-%H-%M-%S', time.localtime(time.time()))
    # goods_snapshot = poco("com.alibaba.wireless:id/image")
    goods_snapshot = \
        poco("android:id/content").child("android.widget.FrameLayout").offspring("android.webkit.WebView").child(
            "android.view.View").child("android.view.View")[0]
    if not goods_snapshot.exists():
        print("未获取到商品分享口令的组件，无法截图。")
        return None
    goods_snapshot.wait_for_appearance(5)
    element_snapshot(goods_snapshot, save=True, filename=filename, width=380)
    return "snapshot" + time.strftime('%Y-%m-%d-%H-%M-%S', time.localtime(time.time()))


def element_snapshot(poco_object, save=False, filename="ele", width=720):
    """
    airtest目前只能对全屏截图，本函数可对指定组件截图，并返回一个PIL.Image对象。
    ps 保存临时文件再读出来的方式是影响效能的，要优化。
       计算左上角坐标的方式是无知的，肯定有我没找到原生api做到这个，可要优化。

    :param poco_object: poco对象
    :param save: 是否保存截图文件
    :param filename: 保存的文件名
    :param width: 图片宽度
    :return: 返回PIL.Image对象
    """
    b64img, fmt = poco.snapshot(width=width)
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
        # filename = "ele" + time.strftime('%Y-%m-%d-%H-%M-%S', time.localtime(time.time()))
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
            return True
        else:
            return False
    except Exception as e:
        capture_error(e)
        print("is_ending")
    return False


def snapshot(filename, subdirectory='snap'):
    b64img, fmt = poco.snapshot(width=720)
    path = r'%s\%s' % (sys.path[0], subdirectory)
    mkdir(path)
    open(r'{}\{}.{}'.format(path, filename, fmt), 'wb').write(b64decode(b64img))


def capture_error(msg):
    filename = "error" + time.strftime('%Y-%m-%d-%H-%M-%S', time.localtime(time.time()))
    snapshot(filename, "error")
    logger.error("Error captured, Message:[{}], snapshot={}".format(msg, filename))


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
        logger.error("未识别的组件对象(object_in_view)")
    return False
