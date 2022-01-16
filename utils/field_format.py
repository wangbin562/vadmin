# !/usr/bin/python
# -*- coding: utf-8 -*-
"""
字段格式化
"""


def time_2_str(o_time, default=""):
    """
    # time对象转字符串，返回""或2015-12-12 10:10:10
    """
    if not o_time:
        return default

    s_time = str(o_time)
    s_time = s_time.strip()
    if len(s_time) >= 19:
        s_time = s_time[:19]

    return s_time


def file_2_str(obj, field_name):
    try:
        path = getattr(obj, field_name).get_url()
    except (BaseException,):
        try:
            path = getattr(obj, field_name).name
        except (BaseException,):
            path = ""

    from django.conf import settings
    if path == settings.MEDIA_URL:
        path = ""

    return path


def url_2_str(obj):
    """
    # 返回url对象
    :param obj:
    :return:
    """
    try:
        # 以/开头的直接返回该URL
        if str(obj).find('/') == 0:
            return str(obj)
        else:
            return obj.url
    except (BaseException,):
        return ""


def null_2_str(data, default=""):
    """
    # 空对象转字符串
    :param data:
    :param default:
    :return:
    """
    if data is None:
        return default

    elif isinstance(data, (type(0.0), type(0))):
        return str(data)

    return data


def null_2_number(data, default=0):
    """
    # 空对象转数字
    :param data:
    :param default:
    :return:
    """
    if data is None:
        return default

    return data


def null_2_int(data, default=0):
    """
    # 空对象转数字
    :param data:
    :param default:
    :return:
    """
    if data is None:
        return default

    return int(data)


def null_2_float(data, default=0.0):
    """
    # 空对象转数字(float)
    :param data:
    :param default:
    :return:
    """
    if data is None:
        return default

    return float(data)


def obj_2_int(obj, field):
    """
        # 判断对象是否为空，如是不为空，返回0
        :param obj:
        :param field:
        :return:
        """
    if not obj:
        return 0

    val = getattr(obj, field)
    return null_2_int(val)


def obj_2_str(obj, field, field_sub=None):
    """
    # 判断对象是否为空，如是不为空，返回对象字符串
    :param obj:
    :param field:
    :param field_sub:
    :return:
    """
    try:
        if field_sub:
            obj_sub = getattr(obj, field)
            return null_2_str(getattr(obj_sub, field_sub))
        else:
            return null_2_str(getattr(obj, field))
    except (BaseException,):
        return ""


def int_2_bool(obj):
    """
    # int 转 bool
    :param obj:
    :return:
    """
    return False if obj == 0 else True


def zero_2_none(data):
    """
    如果等于0，返回None
    """
    data = str_2_number(data)

    if data == 0:
        return None

    return data


def empty_2_none(data):
    """
    参数如果等于""，返回None
    :param val:
    :return:
    """
    if data == "":
        return None

    return data


def str_2_number(data):
    """
    如果等于None,返回None，否则返回数字
    :param data:
    :return:
    """
    if data is None:
        return data

    if data == "":
        return None

    if isinstance(data, type(1)) or isinstance(data, type(1.0)):
        return data

    if data.isdigit():
        return int(data)

    return float(data)
