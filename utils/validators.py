#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
@version: V1.0
@author: Coffen
@license: Hui_yu Licence
@file: validate
@time: 2018/9/21 11:46
"""
import re
import os, time, random
import datetime
import types
import math
import socket


def check_identity_no(id):
    """
    身份证验证
    """
    id = id.upper()
    # 身份证验证
    c = 0
    for (d, p) in zip(map(int, id[:~0]), range(17, 0, -1)):
        c += d * (2 ** p) % 11
    return id[~0] == '10_x98765432'[c % 11]


# 验证账号格式
def is_mobile(mobile):
    """
     验证账号格式
    """
    if mobile:
        if len(mobile) == 11 and re.match("^(1[3456879]\d{9})$", mobile) != None:
            return True
        else:
            return False
    else:
        return False


# 判断是否为整数
def is_number(var_obj):
    """
    判断是否为整数
    """
    if var_obj:
        if re.match("^([0-9]*)$", var_obj) != None:
            return True
        else:
            return False
    else:
        return False


# 判断是否为字符串 string
def is_string(var_obj):
    """
    判断是否为字符串 string
    """
    return type(var_obj) is types.StringType


def is_float(var_obj):
    """
    # 判断是否为浮点数 1.324
    """
    return type(var_obj) is types.FloatType


def is_dict(var_obj):
    """
   # 判断是否为字典 {'a1':'1','a2':'2'}
    """
    return type(var_obj) is types.DictType


def is_tuple(var_obj):
    """
    # 判断是否为tuple [1,2,3]
    """
    return type(var_obj) is types.TupleType


def is_list(var_obj):
    '''

# 判断是否为List [1,3,4]
    '''
    return type(var_obj) is types.ListType


def is_boolean(var_obj):
    '''

    # 判断是否为布尔值 True
    '''
    return type(var_obj) is types.BooleanType


# 判断是否为货币型 1.32
def is_currency(var_obj):
    """
  数字是否为整数或浮点数
    """
    # 数字是否为整数或浮点数
    if is_float(var_obj) and is_number(var_obj):
        # 数字不能为负数
        if var_obj > 0:
            return True
    return False


# 判断某个变量是否为空 x
def is_empty(var_obj):
    """
    # 判断某个变量是否为空 x
    """
    if len(var_obj) == 0:
        return True
    return False


# 判断变量是否为None None
def is_none(var_obj):
    """
    # 判断变量是否为None None
    """
    return type(var_obj) is types.NoneType


# 判断是否为日期格式,并且是否符合日历规则 2010-01-31
def is_date(var_obj):
    """
    判断是否为日期格式,并且是否符合日历规则 2010-01-31
    """
    if len(var_obj) == 10:
        rule = '(([0-9]{3}[1-9]|[0-9]{2}[1-9][0-9]{1}|[0-9]{1}[1-9][0-9]{2}|[1-9][0-9]{3})-(((0[13578]|1[02])-(0[1-9]|[12][0-9]|3[01]))|((0[469]|11)-(0[1-9]|[12][0-9]|30))|(02-(0[1-9]|[1][0-9]|2[0-8]))))|((([0-9]{2})(0[48]|[2468][048]|[13579][26])|((0[48]|[2468][048]|[3579][26])00))-02-29)$/'
        match = re.match(rule, var_obj)
        if match:
            return True
        return False
    return False


# 判断是否为邮件地址
def is_email(var_obj):
    """
    判断是否为邮件地址
    """
    rule = '[\w-]+(\.[\w-]+)*@[\w-]+(\.[\w-]+)+$'
    match = re.match(rule, var_obj)
    if match:
        return True
    return False


# 判断是否为中文字符串
def is_chinese_char_string(var_obj):
    """
    判断是否为中文字符串
    """
    for x in var_obj:
        if (x >= u"\u4e00" and x <= u"\u9fa5") or (x >= u'\u0041' and x <= u'\u005a') or (
                        x >= u'\u0061' and x <= u'\u007a'):
            continue
        else:
            return False
    return True


# 判断是否为中文字符
def is_chinese_char(var_obj):
    """
    判断是否为中文字符
    """
    if var_obj[0] > chr(127):
        return True
    return False


# 判断帐号是否合法 字母开头，允许4-16字节，允许字母数字下划线
def is_legal_accounts(var_obj):
    """
    判断帐号是否合法 字母开头，允许4-16字节，允许字母数字下划线
    """
    rule = '[a-z_a-Z][a-z_a-Z0-9_]{3,15}$'
    match = re.match(rule, var_obj)

    if match:
        return True
    return False


def is_date_format(date_str):
    """
    判断日期的格式，如果是"%Y-%m-%d"格式则返回1，如果是"%Y-%m-%d %H:%M:%S"则返回2，否则返回0
    参数 datestr:日期字符串
    """
    try:
        format_date = "%Y-%m-%d"
        datetime.datetime.strptime(date_str, format_date)
        return 1
    except:
        pass

    try:
        format_datetime = "%Y-%m-%d %H:%M:%S"
        datetime.datetime.strptime(date_str, format_datetime)
        return 2
    except:
        pass

    return 0


def is_leap_year(pyear):
    """
    判断输入的年份是否是闰年
    """
    try:
        datetime.datetime(pyear, 2, 29)
        return True
    except ValueError:
        return False


def is_id_card(idcard):
    Errors = [u'验证通过!',
            u'身份证号码位数不对!',
            u'身份证号码出生日期超出范围或含有非法字符!',
            u'身份证号码校验错误!',
            u'身份证地区非法!']
    area = {
        "11": u"北京",
        "12": u"天津",
        "13": u"河北",
        "14": u"山西",
        "15": u"内蒙古",
        "21": u"辽宁",
        "22": u"吉林",
        "23": u"黑龙江",
        "31": u"上海",
        "32": u"江苏",
        "33": u"浙江",
        "34": u"安徽",
        "35": u"福建",
        "36": u"江西",
        "37": u"山东",
        "41": u"河南",
        "42": u"湖北",
        "43": u"湖南",
        "44": u"广东",
        "45": u"广西",
        "46": u"海南",
        "50": u"重庆",
        "51": u"四川",
        "52": u"贵州",
        "53": u"云南",
        "54": u"西藏",
        "61": u"陕西",
        "62": u"甘肃",
        "63": u"青海",
        "64": u"宁夏",
        "65": u"新疆",
        "71": u"台湾",
        "81": u"香港",
        "82": u"澳门",
        "91": u"国外"
    }
    idcard = str(idcard)
    idcard = idcard.strip()
    idcard_list = list(idcard)

    # 地区校验
    if(not area[(idcard)[0:2]]):
        return 50004
    # 15位身份号码检测
    if(len(idcard) == 15):
        if((int(idcard[6:8])+1900) % 4 == 0 or((int(idcard[6:8])+1900) % 100 == 0 and (int(idcard[6:8])+1900) % 4 == 0 )):
            erg=re.compile('[1-9][0-9]{5}[0-9]{2}((01|03|05|07|08|10|12)(0[1-9]|[1-2][0-9]|3[0-1])|(04|06|09|11)(0[1-9]|[1-2][0-9]|30)|02(0[1-9]|[1-2][0-9]))[0-9]{3}$')#//测试出生日期的合法性
        else:
            ereg=re.compile('[1-9][0-9]{5}[0-9]{2}((01|03|05|07|08|10|12)(0[1-9]|[1-2][0-9]|3[0-1])|(04|06|09|11)(0[1-9]|[1-2][0-9]|30)|02(0[1-9]|1[0-9]|2[0-8]))[0-9]{3}$')#//测试出生日期的合法性
        if(re.match(ereg,idcard)):
            return 0
        else:
            return 50002
    # 18位身份号码检测
    elif(len(idcard)==18):
        # 出生日期的合法性检查
        # 闰年月日:((01|03|05|07|08|10|12)(0[1-9]|[1-2][0-9]|3[0-1])|
        # (04|06|09|11)(0[1-9]|[1-2][0-9]|30)|02(0[1-9]|[1-2][0-9]))
        # 平年月日:((01|03|05|07|08|10|12)(0[1-9]|[1-2][0-9]|3[0-1])|
        # (04|06|09|11)(0[1-9]|[1-2][0-9]|30)|02(0[1-9]|1[0-9]|2[0-8]))
        if(int(idcard[6:10]) % 4 == 0 or (int(idcard[6:10]) % 100 == 0 and int(idcard[6:10]) % 4 == 0)):
            ereg = re.compile('[1-9][0-9]{5}(19[0-9]{2}|20[0-9]{2})((01|03|05|07|08|10|12)(0[1-9]|[1-2][0-9]|3[0-1])|'
                            '(04|06|09|11)(0[1-9]|[1-2][0-9]|30)|02(0[1-9]|[1-2][0-9]))[0-9]{3}[0-9_xx]$')
        else:
            ereg=re.compile('[1-9][0-9]{5}(19[0-9]{2}|20[0-9]{2})((01|03|05|07|08|10|12)(0[1-9]|[1-2][0-9]|3[0-1])|'
                            '(04|06|09|11)(0[1-9]|[1-2][0-9]|30)|02(0[1-9]|1[0-9]|2[0-8]))[0-9]{3}[0-9_xx]$')
        # //测试出生日期的合法性
        if(re.match(ereg,idcard)):
            # //计算校验位
            S = (int(idcard_list[0]) + int(idcard_list[10])) * 7 + (int(idcard_list[1]) + int(idcard_list[11])) * 9 +\
                (int(idcard_list[2]) + int(idcard_list[12])) * 10 + (int(idcard_list[3]) + int(idcard_list[13])) * 5 +\
                (int(idcard_list[4]) + int(idcard_list[14])) * 8 + (int(idcard_list[5]) + int(idcard_list[15])) * 4 +\
                (int(idcard_list[6]) + int(idcard_list[16])) * 2 + int(idcard_list[7]) * 1 + int(idcard_list[8]) * 6 + \
                int(idcard_list[9]) * 3
            Y = S % 11
            M = "F"
            JYM = "10_x98765432"
            M = JYM[Y]  # 判断校验位
            if(M == idcard_list[17]):  # 检测ID的校验位
                return 0
            else:
                return 50003
        else:
            return 50002
    else:
        return 50001


def is_email(email):
    if len(email) > 7:
        if re.match('^.+\\@(\\[?)[a-z_a-Z0-9\\-\\.]+\\.([a-z_a-Z]{2,3}|[0-9]{1,3})(\\]?)$', email) != None:
            return True
    return False


def is_float_or_int(string):
    try:
        float(string)
    except:
        return False
    else:
        return True


def validate_params_exist(*args):
    for i in args:
        if i == '' or i is None or i == []:
            return False
    return True


if __name__ == "__main__":
    # is_m = is_mobile('17720558002')
    is_m = is_mobile('16638843667')
    if is_m:
        print('ok')
    else:
        print('nok')
    pass
    # while True:
    #     cdcard = input(u"请输入你的身份证号：")
    #     if cdcard == "exit":
    #         print(u"程序已结束！")
    #         break
    #     else:
    #         is_id_card(cdcard)
