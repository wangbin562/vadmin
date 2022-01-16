#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
时间护展库(v1.1)
安装pip install python-dateutil
"""

import datetime


def subtract_time(end_time, begin_time, include_date=False):
    """
    减去时间
    :param end_time:结束时间（10:30)
    :param begin_time:开始时间(9:5)
    :param include_date:包含日期
    :return:秒（十进制,精确到小数点后两位)
    """
    o_begin = format_time(begin_time)
    o_end = format_time(end_time)
    if include_date:
        o_begin = datetime.datetime.strptime(o_begin.strftime("%Y-%m-%d %H:%M:%S"), "%Y-%m-%d %H:%M:%S")
        o_end = datetime.datetime.strptime(o_end.strftime("%Y-%m-%d %H:%M:%S"), "%Y-%m-%d %H:%M:%S")
    else:
        o_begin = datetime.datetime.strptime(o_begin.strftime("%H:%M:%S"), "%H:%M:%S")
        o_end = datetime.datetime.strptime(o_end.strftime("%H:%M:%S"), "%H:%M:%S")

    obj = o_end - o_begin
    return obj.days * 86400 + obj.seconds


def subtract_year(dt, years):
    return add_year(dt, -1 * years)


def subtract_month(dt, months):
    return add_month(dt, -1 * months)


def subtract_day(dt, days):
    return add_day(dt, -1 * days)


def subtract_minute(dt, minutes):
    """
    减去分钟
    :param dt: 日期时间
    :param minutes:分种,int类型
    :return:日期时间字符串
    """
    return add_minute(dt, -1 * minutes)


def subtract_second(dt, seconds):
    return add_second(dt, -1 * seconds)


def add_year(dt, years):
    """
    增加年
    :param dt:时间、日期
    :param years:增加的年（int类型，负数为减）
    :return:新的日期，datetime格式
    """
    o_dt = format_time(dt)
    from dateutil.relativedelta import relativedelta
    return o_dt + relativedelta(years=years)


def add_month(dt, months):
    """
    增加月
    :param dt:时间、日期
    :param months:增加的月（int类型，负数为减）
    :return:新的日期，datetime格式
    """
    from dateutil.relativedelta import relativedelta
    o_dt = format_time(dt)
    new_dt = o_dt + relativedelta(months=months)
    return new_dt


def add_day(dt, days):
    """
    增加天数
    :param dt:时间、日期
    :param days:天数（int类型，负数为减）
    :return:新的日期，datetime格式
    """
    from dateutil.relativedelta import relativedelta
    o_dt = format_time(dt)
    new_dt = o_dt + relativedelta(days=days)
    return new_dt


def add_minute(t, minutes):
    """
    增加分钟
    :param t: 时间
    :param minutes:分种,int类型
    :return:日期时间字符串
    """
    o = format_time(t)
    return o + datetime.timedelta(minutes=minutes)


def add_second(t, seconds):
    """
    增加秒
    :param t:时间
    :param seconds:
    :return:
    """
    o = format_time(t)
    return o + datetime.timedelta(seconds=seconds)


def comp_datetime(time1, time2, equal=True):
    """
    比较时间
    :param time1:
    :param time2:
    :param equal:是否比较等于
    :return:如果time1大于time2，则返回True
    """

    o_time1 = format_time(time1)
    o_time2 = format_time(time2)

    if equal:
        return o_time1 >= o_time2

    return o_time1 > o_time2


def comp_date(data1, data2, equal=False):
    """
    比较日期
    """
    o_time1 = format_time(data1)
    o_time2 = format_time(data2)

    if equal:
        return o_time1.strftime("%Y-%m-%d") >= o_time2.strftime("%Y-%m-%d")

    return o_time1.strftime("%Y-%m-%d") > o_time2.strftime("%Y-%m-%d")


def comp_time(time1, time2, equal=True):
    """
    比较时间
    :param time1:
    :param time2:
    :param equal:是否比较等于
    :return:如果time1大于time2，则返回True
    """

    o_time1 = format_time(time1)
    o_time2 = format_time(time2)

    if equal:
        return o_time1.strftime("%H:%M:%S") >= o_time2.strftime("%H:%M:%S")

    return o_time1.strftime("%H:%M:%S") > o_time2.strftime("%H:%M:%S")


def format_time(t):
    """
    格式化时间
    :param t:
    :return: datetime.datetime
    """
    if isinstance(t, datetime.datetime):
        o_time = datetime.datetime.strptime(t.strftime("%Y-%m-%d %H:%M:%S"), "%Y-%m-%d %H:%M:%S")
    elif isinstance(t, datetime.time):
        o_time = datetime.datetime.strptime("%02d:%02d:%02d" % (t.hour, t.minute, t.second), "%H:%M:%S")
    elif isinstance(t, datetime.date):
        o_time = datetime.datetime.strptime("%04d-%02d-%02d" % (t.year, t.month, t.day), "%Y-%m-%d")

    elif len(t) == 19:
        o_time = datetime.datetime.strptime(t, "%Y-%m-%d %H:%M:%S")

    elif 8 < len(t) <= 10:
        o_time = datetime.datetime.strptime(t, "%Y-%m-%d")

    elif 5 < len(t) <= 8:
        o_time = datetime.datetime.strptime(t, "%H:%M:%S")
    else:
        o_time = datetime.datetime.strptime(t, "%H:%M")

    return o_time


def is_equal_datetime(time1, time2):
    """比较两个时间是否相等"""
    return format_time(time1) == format_time(time2)


def is_equal_date(time1, time2):
    """比较两个时间是否相等"""
    return format_time(time1).strftime("%Y-%m-%d") == format_time(time2).strftime("%Y-%m-%d")


def is_equal_time(time1, time2):
    """比较两个时间是否相等"""
    return format_time(time1).strftime("%H:%M:%S") == format_time(time2).strftime("%H:%M:%S")


def is_datetime_period(begin_time, end_time, time, is_equal_begin=True, is_equal_end=True):
    o_begin_time = format_time(begin_time)
    o_end_time = format_time(end_time)
    o_time = format_time(time)

    if is_equal_begin and is_equal_end:
        return (o_time >= o_begin_time) and (o_time <= o_end_time)

    elif is_equal_begin:
        return (o_time >= o_begin_time) and (o_time < o_end_time)

    elif is_equal_end:
        return (o_time > o_begin_time) and (o_time <= o_end_time)

    return (o_time > o_begin_time) and (o_time < o_end_time)


def is_time_period(begin_time, end_time, time, is_equal_begin=True, is_equal_end=True):
    """
    # 是否在时间段内 begin_time=9:00, end_time=12:00 time=11:00 返回true
    :param begin_time:开始时间
    :param end_time:结束时间
    :param time:中间时间
    :param is_equal_begin:是否等于开始时间
    :param is_equal_end:是否等于结束时间
    :return:
    """
    o_begin_time = format_time(begin_time)
    o_end_time = format_time(end_time)
    o_time = format_time(time)

    begin_seconds = datetime.timedelta(hours=o_begin_time.hour, minutes=o_begin_time.minute,
                                       seconds=o_begin_time.second).total_seconds()
    end_seconds = datetime.timedelta(hours=o_end_time.hour, minutes=o_end_time.minute,
                                     seconds=o_end_time.second).total_seconds()
    seconds = datetime.timedelta(hours=o_time.hour, minutes=o_time.minute, seconds=o_time.second).total_seconds()

    if is_equal_begin and is_equal_end:
        return begin_seconds <= seconds <= end_seconds

    elif is_equal_begin and not is_equal_end:
        return begin_seconds <= seconds < end_seconds

    elif not is_equal_begin and is_equal_end:
        return begin_seconds < seconds <= end_seconds

    return begin_seconds < seconds < end_seconds


def is_date_period(begin_date, end_date, date, is_equal_begin=True, is_equal_end=True):
    """
    是否在日期之内
    begin_date:
    end_date:
    date:
    is_equal_begin: 等于开始也在日期段内
    is_equal_end:等于结否也在日期段内
    Returns:
    """
    if is_equal_begin and (
            begin_date.year == date.year and begin_date.month == date.month and begin_date.day == date.day):
        return True

    if is_equal_end and (end_date.year == date.year and end_date.month == date.month and end_date.day == date.day):
        return True

    flag_1 = comp_date(date, begin_date)
    flag_2 = comp_date(end_date, date)
    if flag_1 and flag_2:
        return True

    return False


def is_cycle_interval(now_time, cycle_minute=30, interval=3):
    """
    是否在周期区间内
    :param now_time: 日期时间字符串
    :param cycle_minute:周期分钟
    :param interval:区间分钟
    :return:
    """
    s_date, s_time = now_time.split(" ")
    begin_time = "%s %s:%02d:00" % (s_date, s_time.split(":")[0], cycle_minute % 60)
    end_time = "%s %s:%02d:00" % (s_date, s_time.split(":")[0], (cycle_minute + interval) % 60)
    return begin_time <= now_time <= end_time


def calc_day(begin_date, end_date):
    """
    计算天数
    :param begin_date:2016-05-31 字符串格式日期
    :param end_date:2016-06-03 字符串格式日期
    :return: 返回中间每一天的datetime对象
    """
    lst_day = []
    o_begin_day = format_time(begin_date)
    o_end_day = format_time(end_date)
    if o_end_day < o_begin_day:
        return lst_day

    o_datetime = datetime.timedelta(1)
    o_day = o_begin_day

    while o_day <= o_end_day:
        lst_day.append(o_day)
        o_day = (o_day + o_datetime)

    return lst_day


def calc_month(begin_year, begin_month, end_year, end_month):
    """
    计算月份
    :param begin_year:开始年
    :param begin_month:开始月
    :param end_year:结束年
    :param end_month:结束月
    :return:
    # begin_date:2015.10
    # end_date:2016.05
    # 返回 [[2015,10],[2015,11],[2015,12],[2016,01],[2016,02],[2016,03],[2016,04],[2016,05]]
    """
    lst_month = []
    for tmp_year in range(begin_year, end_year + 1):
        if tmp_year == begin_year and tmp_year == end_year:
            for tmp_month in range(begin_month, end_month + 1):
                lst_month.append([tmp_year, tmp_month])

        elif tmp_year == begin_year:
            for tmp_month in range(begin_month, 13):
                lst_month.append([tmp_year, tmp_month])

        elif tmp_year == end_year:
            for tmp_month in range(1, end_month + 1):
                lst_month.append([tmp_year, tmp_month])

        else:
            for tmp_month in range(1, 13):
                lst_month.append([tmp_year, tmp_month])

    return lst_month


def calc_cycle(begin_time=None, end_time=None, max_days=7, cycle_minute=30):
    """
    计算时间周期
    :param begin_time: 开始时间
    :param end_time: 结束时间
    :param max_days:计算的最大天数
    :param cycle_minute:周期分钟
    :return:
    """
    lst_time = []
    # 当天
    if (begin_time is None) and (end_time is None):
        now_day = "%s 00:00:00" % datetime.datetime.now().strftime("%Y-%m-%d")
        new_time = datetime.datetime.strptime(now_day, "%Y-%m-%d %H:%M:%S")
        lst_time.append(now_day)
        for i in range(1, int(1439 / cycle_minute) + 1):  # 1440是一天的分钟，最后一个时间不能取，转第2天的0点
            new_time = new_time + datetime.timedelta(minutes=cycle_minute)
            lst_time.append(new_time.strftime('%Y-%m-%d %H:%M:%S'))

    # 开始时间当天
    elif (begin_time is not None) and (end_time is None):
        now_day = "%s 00:00:00" % begin_time.split(" ")[0]
        new_time = datetime.datetime.strptime(now_day, "%Y-%m-%d %H:%M:%S")
        lst_time.append(now_day)
        for i in range(1, int(1439 / cycle_minute) + 1):  # 1440是一天的分钟，最后一个时间不能取，转第2天的0点
            new_time = new_time + datetime.timedelta(minutes=cycle_minute)
            lst_time.append(new_time.strftime('%Y-%m-%d %H:%M:%S'))

    elif (begin_time is None) and (end_time is not None):
        now_day = "%s 00:00:00" % end_time.split(" ")[0]
        new_time = datetime.datetime.strptime(now_day, "%Y-%m-%d %H:%M:%S")
        lst_time.append(now_day)
        for i in range(1, int(1439 / cycle_minute) + 1):  # 1440是一天的分钟，最后一个时间不能取，转第2天的0点
            new_time = new_time + datetime.timedelta(minutes=cycle_minute)
            lst_time.append(new_time.strftime('%Y-%m-%d %H:%M:%S'))
    else:
        o_begin_time = datetime.datetime.strptime(begin_time, "%Y-%m-%d %H:%M:%S")
        o_end_time = datetime.datetime.strptime(end_time, "%Y-%m-%d %H:%M:%S")
        begin_day = datetime.datetime.strptime("%s 00:00:00" % begin_time.split(" ")[0], "%Y-%m-%d %H:%M:%S")
        # end_day = datetime.datetime.strptime("%s 00:00:00" % end_time.split(" ")[0], "%Y-%m-%d %H:%M:%S")
        date = o_end_time - o_begin_time
        if date.seconds > 0:
            days = date.days + 1
        else:
            days = date.days

        if days <= 0:
            days = 1
        elif days > max_days:
            days = max_days

        new_time = begin_day
        lst_time.append(new_time.strftime('%Y-%m-%d %H:%M:%S'))
        for i in range(1, int((days * 24 * 60 - 1) / cycle_minute) + 1):
            new_time = new_time + datetime.timedelta(minutes=cycle_minute)
            lst_time.append(new_time.strftime('%Y-%m-%d %H:%M:%S'))

    return lst_time


def format_cycle_time(begin_time, current_time, cycle_minute=30):
    """
    格式化周期当前时间
    :param begin_time:开始时间
    :param current_time:当前时间
    :param cycle_minute:周期分钟
    :return:
    """
    o_begin_time = datetime.datetime.strptime(begin_time, "%Y-%m-%d %H:%M:%S")
    o_current_time = datetime.datetime.strptime(current_time, "%Y-%m-%d %H:%M:%S")
    o_time = o_current_time - o_begin_time
    quotient, remainder = divmod(o_time.total_seconds(), (cycle_minute * 60))
    o_format_begin_time = o_current_time - datetime.timedelta(seconds=remainder)
    o_format_end_time = o_format_begin_time + datetime.timedelta(minutes=cycle_minute)

    return o_format_begin_time.strftime('%Y-%m-%d %H:%M:%S'), o_format_end_time.strftime('%Y-%m-%d %H:%M:%S')


def hour_str_2_float(s_time):
    # 传入1:30,返回1.5
    hour, minute = s_time.split(":")
    hour, minute = int(hour), int(minute)

    return hour + round(minute / 60.0, 2)


def hour_float_2_str(f_time):
    # 传入1.5,返回1:30
    s_time = str(f_time)
    hour, minute = s_time.split(".")
    minute = float("0.%s" % minute)

    return u"%s:%02d" % (hour.zfill(2), int(round(minute * 60)))


def weekday_2_chinese(weekday):
    """
    星期转换成中文
    weekday: 0-6
    Returns:中文星期
    """
    if 1 == weekday:
        return u'星期二'

    elif 2 == weekday:
        return u'星期三'

    elif 3 == weekday:
        return u'星期四'

    elif 4 == weekday:
        return u'星期五'

    elif 5 == weekday:
        return u'星期六'

    elif 6 == weekday:
        return u'星期日'

    return u'星期一'


def format_time_duration(second):
    second = int(second)
    if second < 60:
        value = "%s秒" % second
    elif second < (60 * 60):
        # value = "%s分%s秒" % divmod(second, 60)
        value = "%s分钟" % round(second / 60, 2)
    elif second < (24 * 60 * 60):
        value = "%s小时" % round(second / 3600, 2)
        # h, s = divmod(second, 3600)
        # if s:
        #     m, s = divmod(s, 60)
        #     if s:
        #         value = "%s小时%s分%s秒" % (h, m, s)
        #     else:
        #         value = "%s小时%s分" % (h, m)
        # else:
        #     value = "%s小时" % h
    else:
        value = "%s天" % round(second / (24 * 3600), 2)
        # d, s = divmod(second, 24 * 3600)
        # if s:
        #     h, s = divmod(s, 3600)
        #     if s:
        #         m, s = divmod(s, 60)
        #         if s:
        #             value = "%s天%s小时%s分%s秒" % (d, h, m, s)
        #         else:
        #             value = "%s天%s小时%s分" % (d, h, m)
        #     else:
        #         value = "%s天%s小时" % (d, h)
        # else:
        #     value = "%s天" % d

    return value


def time_2_chinese(time, max=None):
    """
    时间转换成中文
    :param time:
    :param max:
    :return:
    """
    t = format_time(time)
    seconds = (datetime.datetime.now() - t).total_seconds()
    if seconds < 0:
        return t.strftime('%Y-%m-%d %H:%M:%S')
    elif (max is not None) and (max < seconds):
        return t.strftime('%Y-%m-%d %H:%M:%S')

    if 0 < seconds < 60:
        return "刚才"

    if seconds < 3600:
        return "%s分钟以前" % int(seconds / 60)

    if 3600 <= seconds < 60 * 60 * 24:
        return "%s小时以前" % int(seconds / (60 * 60))

    if 60 * 60 * 24 <= seconds < 60 * 60 * 24 * 30:
        return "%s天以前" % int(seconds / (60 * 60 * 24))

    if 60 * 60 * 24 * 30 <= seconds < 60 * 60 * 24 * 30 * 12:
        return "%s月以前" % int(seconds / (60 * 60 * 24 * 30))

    if 60 * 60 * 24 * 30 * 12 <= seconds:
        return "%s年以前" % int(seconds / (60 * 60 * 24 * 30 * 12))

    return t.strftime('%Y-%m-%d %H:%M:%S')


def second_2_chinese(second):
    second = int(second)
    if second < 60:
        value = "%s秒" % second
    elif second < (60 * 60):
        # value = "%s分%s秒" % divmod(second, 60)
        value = "%s分钟" % round(second / 60, 2)
    elif second < (24 * 60 * 60):
        value = "%s小时" % round(second / 3600, 2)
        # h, s = divmod(second, 3600)
        # if s:
        #     m, s = divmod(s, 60)
        #     if s:
        #         value = "%s小时%s分%s秒" % (h, m, s)
        #     else:
        #         value = "%s小时%s分" % (h, m)
        # else:
        #     value = "%s小时" % h
    else:
        value = "%s天" % round(second / (24 * 3600), 2)
        # d, s = divmod(second, 24 * 3600)
        # if s:
        #     h, s = divmod(s, 3600)
        #     if s:
        #         m, s = divmod(s, 60)
        #         if s:
        #             value = "%s天%s小时%s分%s秒" % (d, h, m, s)
        #         else:
        #             value = "%s天%s小时%s分" % (d, h, m)
        #     else:
        #         value = "%s天%s小时" % (d, h)
        # else:
        #     value = "%s天" % d

    return value


if __name__ == "__main__":
    # print(subtract_month(2017, 12, 12))
    # print(add_month(2018, 12, 11))
    # print(add_month(2018, 12, 1))
    # print(subtract_month(2018, 12, 1))
    # print(subtract_month(2018, 1, 1))
    # print(calc_month(2015, 12, 2016, 10))
    # print(subtract_time("10:30", "8:9"))
    # print(comp_time("10:30", "10:31"))
    # print(time_2_chinese("2019-07-26 10:10:10"))
    # print(time_2_chinese("2019-06-26 10:10:10"))
    # print(time_2_chinese("2019-05-27 10:10:10"))
    # print(time_2_chinese("2018-05-27 10:10:10"))
    # print(time_2_chinese("2019-08-26 10:10:10"))
    print(add_year("2019-08-26 10:10:10", 1))
    print(add_year("2019-08-26 10:10:10", 2))
    print(add_year("2019-08-26 10:10:10", -2))
