# !/usr/bin/python
# -*- coding=utf-8 -*-
import datetime
import importlib
import logging
import os
import sys
import time
import traceback
from concurrent.futures import ThreadPoolExecutor
from logging.handlers import RotatingFileHandler

from django.conf import settings
from django.core.management.base import BaseCommand

from timed_task.models import TimedTask
from timed_task.models import TimedTaskLog
from utils import calc_time

if settings.DEBUG:
    console = logging.StreamHandler()
    formatter = logging.Formatter(
        '%(asctime)s [%(threadName)s:%(thread)d] [%(name)s:%(lineno)d] [%(levelname)s]- %(message)s')
    console.setFormatter(formatter)
    logger = logging.getLogger('')
    logger.addHandler(console)
    logger.setLevel(logging.INFO)
else:
    file_path = sys.modules['__main__'].__file__
    file_name = os.path.split(file_path)[1]
    module_name = os.path.splitext(file_name)[0]
    o_handler = RotatingFileHandler('%s.log' % module_name, maxBytes=10 * 1024 * 1024, backupCount=5)
    formatter = logging.Formatter(
        '%(asctime)s [%(threadName)s:%(thread)d] [%(name)s:%(lineno)d] [%(levelname)s]- %(message)s')
    o_handler.setFormatter(formatter)
    logger = logging.getLogger('')
    logger.addHandler(o_handler)
    logger.setLevel(logging.INFO)


class Command(BaseCommand):
    OPTIONS = [
        (('--sleep',), {
            'action': 'store',
            'dest': 'sleep',
            'type': float,
            'default': 60.0,
            'help': 'Sleep for this many seconds before checking for new tasks (if none were found) - default is 5',
        })
    ]

    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)
        self.pool = ThreadPoolExecutor(100)
        self.query_interval = 0
        self.lst_wait_key = []

    def add_arguments(self, parser):
        for (args, kwargs) in self.OPTIONS:
            parser.add_argument(*args, **kwargs)

    def handle(self, *args, **options):
        logger.info('Run timed tasks successfully!')
        sleep_time = options.get("sleep", 600)

        queryset = list(TimedTask.objects.filter(del_flag=False, enable=True))
        while True:
            now = datetime.datetime.now()
            logger.info("run begin:%s" % now)

            try:
                if self.query_interval > 10 * 60:  # 大于10分钟查询一次
                    queryset = list(TimedTask.objects.filter(del_flag=False, enable=True))
                    self.query_interval = 0
                else:
                    self.query_interval += sleep_time

                for obj in queryset:
                    # 已超过最大执行次数
                    obj.run_number = obj.run_number or 0
                    if (obj.max_run_number is not None) and (obj.run_number >= obj.max_run_number):
                        continue

                    if obj.wait_last:
                        wait_key = obj.script + (obj.param or "")
                        if wait_key in self.lst_wait_key:
                            continue
                        else:
                            self.lst_wait_key.append(wait_key)

                    if obj.run_mode == 1:  # (1, '周期执行'), (2, '间隔执行')
                        if obj.last_run_time:
                            if calc_time.comp_date(obj.last_run_time, now, equal=True):
                                continue

                        if obj.cycle_mode == "year":
                            s_date, s_time = obj.cycle_time.split(" ")
                            month, day = s_date.split("-")
                            hour, minute, second = s_time.split(":")
                            last_run_time = datetime.datetime.strptime("%04d-%02d-%02d %02d:%02d:%02d" %
                                                                       (now.year, int(month), int(day),
                                                                        int(hour), int(minute), int(second)),
                                                                       "%Y-%m-%d %H:%M:%S")
                            last_run_time = calc_time.subtract_year(last_run_time, 1)

                        elif obj.cycle_mode == "month":
                            day, s_time = obj.cycle_time.split(" ")
                            hour, minute, second = s_time.split(":")
                            last_run_time = datetime.datetime.strptime("%04d-%02d-%02d %02d:%02d:%02d" %
                                                                       (now.year, now.month, int(day),
                                                                        int(hour), int(minute), int(second)),
                                                                       "%Y-%m-%d %H:%M:%S")
                            last_run_time = calc_time.subtract_month(last_run_time, 1)

                        elif obj.cycle_mode == "week":
                            s_week, s_time = obj.cycle_time.split(" ")
                            hour, minute, second = s_time.split(":")
                            last_run_time = datetime.datetime.strptime("%04d-%02d-%02d %02d:%02d:%02d" %
                                                                       (now.year, now.month, now.day,
                                                                        int(hour), int(minute), int(second)),
                                                                       "%Y-%m-%d %H:%M:%S")
                            week = last_run_time.weekday()
                            week2 = int(s_week)
                            if week > week2:
                                last_run_time = calc_time.subtract_day(last_run_time, week - week2)
                            else:
                                last_run_time = calc_time.subtract_day(last_run_time, week - week2 + 7)
                        else:
                            hour, minute, second = obj.cycle_time.split(":")
                            last_run_time = datetime.datetime.strptime("%04d-%02d-%02d %02d:%02d:%02d" %
                                                                       (now.year, now.month, now.day,
                                                                        int(hour), int(minute), int(second)),
                                                                       "%Y-%m-%d %H:%M:%S")
                            last_run_time = calc_time.subtract_day(last_run_time, 1)

                        if obj.cycle_mode == "year":
                            new_time = calc_time.add_year(last_run_time, 1)
                        elif obj.cycle_mode == "month":
                            new_time = calc_time.add_month(last_run_time, 1)
                        elif obj.cycle_mode == "week":
                            new_time = calc_time.add_day(last_run_time, 7)
                        else:  # 天
                            new_time = calc_time.add_day(last_run_time, 1)

                        if calc_time.comp_datetime(now, new_time):
                            obj.last_run_time = new_time
                            self.run(obj, now)

                    else:
                        if not obj.interval_begin_time:
                            obj.interval_begin_time = now
                            self.run(obj, now)
                            continue

                        if not calc_time.comp_datetime(now, obj.interval_begin_time):
                            continue

                        last_time = obj.last_run_time or obj.interval_begin_time
                        interval_time = eval(obj.interval_time)
                        if calc_time.comp_datetime(now, calc_time.add_second(last_time, interval_time)):
                            # 执行
                            seconds = calc_time.subtract_time(now, obj.interval_begin_time, True)
                            obj.last_run_time = calc_time.add_second(now, (seconds % interval_time) * -1)
                            self.run(obj, now)

            except (BaseException,):
                logger.error(traceback.format_exc())

            end = datetime.datetime.now()
            logger.info("run end:%s" % end)
            time.sleep(sleep_time)

    def run(self, obj, now):
        logger.info("begin:%s(%s)" % (obj.script, obj.param))
        obj.run_number += 1
        obj.save()

        lst_interface = obj.script.strip().split(".")
        o_module = importlib.import_module(".".join(lst_interface[0:-1]))
        fun = getattr(o_module, lst_interface[-1])

        queryset = TimedTaskLog.objects.filter(script=obj.script, param=obj.param)
        count = queryset.count()
        if count >= obj.max_log_number:
            queryset.last().delete()

        o_log = TimedTaskLog.objects.create(script=obj.script, param=obj.param)
        if obj.param:
            f = self.pool.submit(fun, None, obj.param)
        else:
            f = self.pool.submit(fun)

        # f.result(60) # 设置超时时间
        f.param = [obj, o_log.pk]
        f.add_done_callback(self.handle_complete)

    def handle_complete(self, res):
        # obj_id = res.result()
        obj, log_id = res.param

        if obj.wait_last:
            wait_key = obj.script + (obj.param or "")
            if wait_key in self.lst_wait_key:
                self.lst_wait_key.remove(wait_key)

        if log_id:
            exception_log = res.exception()
            try:
                o_log = TimedTaskLog.objects.filter(pk=log_id).first()
                o_log.exception_log = exception_log
                o_log.end_time = datetime.datetime.now()
                o_log.save()
            except (BaseException,):
                logger.error(traceback.format_exc())

            logger.info("end:%s(%s)" % (obj.script, obj.param))
        else:
            logger.info("end:")
