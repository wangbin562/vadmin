# !/usr/bin/python
# -*- coding: utf-8 -*-
"""
共公函数
"""

import os, time, random
import re
from datetime import datetime
import socket


def make_name(name):
    """
    # 构造文件名称
    :param name:
    :return:
    """
    # 文件扩展名
    ext = os.path.splitext(name)[1]

    # 定义文件名，年月日时分秒随机数
    fn = time.strftime('%Y%m%d%H%M%S')
    fn += '_%d' % random.randint(1, 10000)
    # 重写合成文件名
    name = fn + ext
    return name


def random_code(length):
    """
    # 随机生成验证码
    :param length:
    :return:
    """
    num = '0123456789'
    return ''.join(random.sample(num, length))


# 清楚空格
def clear_str_space(s):
    """
    清楚空格
    """
    s = s.replace(' ', '')
    s = s.replace(u'　', '')
    return s


def generate_code(length):
    """
     取随机数
    """
    num = '0123456789'
    return ''.join(random.sample(num, length))


def the_months(dt):
    # 本月初
    month = dt.month
    year = dt.year
    day = 1
    return dt.replace(year=year, month=month, day=day)


def last_months(dt, m=1):
    # 上月初
    month = dt.month - m
    if month == 0:
        month = 12
    if month < 0:
        year = dt.year - ((abs(month) + 12) / 12)
        month += 12
    else:
        year = dt.year - month / 12
    day = 1
    return dt.replace(year=year, month=month, day=day)


def next_months(dt, m=1):
    # 下月初
    month = dt.month - 1 + m
    year = dt.year + month / 12
    month = month % 12 + 1
    day = 1
    return dt.replace(year=year, month=month, day=day)


def last_year(dt):
    # 明年初
    year = dt.year - 1
    month = 1
    day = 1
    return dt.replace(year=year, month=month, day=day)


def next_year(dt):
    # 明年初
    year = dt.year + 1
    month = 1
    day = 1
    return dt.replace(year=year, month=month, day=day)


def the_year(dt):
    # 年初
    year = dt.year
    month = 1
    day = 1
    return dt.replace(year=year, month=month, day=day)


def begin_time(dt):
    return dt.replace(minute=0, second=0)


def div_mod(a, b):
    """
    向上取整
    :param a:
    :param b:
    :return:
    """
    tmp1, tmp2 = divmod(a, b)
    if tmp2 > 0:
        return tmp1 + 1
    else:
        return tmp1


def get_date_to_number(date1):
    """
    将日期字符串中的减号冒号去掉:
    输入：2013-04-05，返回20130405
    输入：2013-04-05 22:11:23，返回20130405221123
    """
    return date1.replace("-", "").replace(":", "").replace("", "")


def get_current_date():
    """
    获取当前日期：2013-09-10这样的日期字符串
    """
    return time.strftime(format_date, time.localtime(time.time()))


def get_current_datetime():
    """
            获取当前时间：2013-09-10 11:22:11这样的时间年月日时分秒字符串
    """
    return time.strftime(format_datetime, time.localtime(time.time()))


def get_current_hour():
    """
    获取当前时间的小时数，比如如果当前是下午16时，则返回16
    """
    cur_datetime = get_current_datetime()
    return cur_datetime[-8:-6]


def get_host_ip():
    """
    获取当前IP地址
    """
    myname = socket.getfqdn(socket.gethostname())
    myaddr = socket.gethostbyname(myname)
    # ip = myaddr + ":8080"
    return myaddr


def get_full_sever_address():
    """
        获取服务器完url path地址
    """
    return "http://" + get_host_ip()


def get_expires(m):
    expires = datetime.datetime.now() + datetime.timedelta(minutes=m)
    timestamp = str(int(time.mktime(expires.timetuple()))) + '000'
    return timestamp


def mask_words(words, content):
    """
    功能说明：   替换敏感词
    """
    try:
        if words:
            lst = words.split(',')
            for w in lst:
                content = content.replace(w, '**')
    except Exception as e:
        pass
    return content


def delete_words(words, content):
    """
    功能说明：   替换敏感词
    """
    try:
        if words:
            lst = words.split(',')
            for w in lst:
                content = content.replace(w, '')
        content = content.replace('**', '')
    except Exception as e:
        pass
    return content


def remove_html_tag(html):
    """
    功能说明：去除html标签
    """
    reg = re.compile('<[^>]*>')
    return reg.sub('', html)


def parse_range(str):
    min = None
    max = None
    try:
        t = str.split('-')
        if len(t) == 2:
            min = int(t[0])
            max = int(t[1])
    except Exception as e:
        pass
    return min, max


def create_order_number():
    """
     生成唯一订单号
    """
    item_id = str(int(time.time() * 1000)) + str(int(time.clock() * 1000000))
    return item_id


def filter_invalid_str(text):
    """
    过滤非BMP字符
    """
    try:
        # UCS-4
        highpoints = re.compile(u'[\U00010000-\U0010ffff]')
    except re.error:
        # UCS-2
        highpoints = re.compile(u'[\uD800-\uDBFF][\uDC00-\uDFFF]')
    return highpoints.sub(u'', text)
