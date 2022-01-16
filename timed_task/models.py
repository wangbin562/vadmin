#!/usr/bin/python
# -*- coding=utf-8 -*-
"""
定时任务model

    创建对应的数据库
    python manage.py migrate timed_task

    还需要另开一个进程来处理这些定时任务
    python manage.py timed_task
    python manage.py timed_task --sleep 1000 # 可以增加参数，默认间隔休息时间1000秒

"""

from django.db import models

from vadmin.models import VModel


class TimedTask(VModel):
    """
    定时任务
    """
    name = models.CharField(verbose_name="任务名称", max_length=64)
    desc = models.CharField(verbose_name="任务描述", max_length=256, blank=True, null=True)
    script = models.CharField(verbose_name="任务执行脚本", max_length=200, db_index=True, unique=True,
                              help_text="类似于：'模块名称.文件名称.函数名称'")
    param = models.CharField(verbose_name="参数", max_length=256, blank=True, null=True)
    run_mode = models.IntegerField(verbose_name='执行模式', choices=((1, '周期执行'), (2, '间隔执行')))
    cycle_mode = models.CharField(verbose_name='周期执行模式', max_length=8, blank=True, null=True,
                                  choices=(('year', '每年'), ('month', '每月'), ('week', '每周'), ('day', '每日')))
    cycle_time = models.CharField(verbose_name='周期执行时间', max_length=32, blank=True, null=True,
                                  help_text="每年：10-01 08:00:00"
                                            "{{\n}}每月：01 08:00:00"
                                            "{{\n}}每周：0 08:00:00 0-6:周一到周日"
                                            "{{\n}}每日：08:00:00")
    interval_begin_time = models.DateTimeField(verbose_name="间隔执行开始时间", blank=True, null=True)
    interval_time = models.CharField(verbose_name="间隔时间", max_length=64, blank=True, null=True,
                                     help_text="单位：秒 可以使用计算模式，例如:"
                                               "{{\n}}一小时：60 * 60"
                                               "{{\n}}一天：24 * 60 * 60")
    max_run_number = models.IntegerField(verbose_name="单个任务最大执行次数", blank=True, null=True,
                                         help_text="为空时不限次数")
    max_log_number = models.IntegerField(verbose_name="单个任务最大记录日志条数", default=100)
    wait_last = models.BooleanField(verbose_name="等待上次执行完成", default=False,
                                    help_text="前一次执行完成后才能执行，不论是否到时间")
    run_number = models.IntegerField(verbose_name="已执行次数", default=0, blank=True, null=True)
    last_run_time = models.DateTimeField(verbose_name="最后执行时间", blank=True, null=True)
    last_exception_log = models.TextField(verbose_name="最后执行异常日志", blank=True, null=True)
    last_begin_time = models.DateTimeField(verbose_name=u"开始时间", blank=True, null=True)
    last_end_time = models.DateTimeField(verbose_name=u"结束时间", blank=True, null=True)
    create_time = models.DateTimeField(verbose_name=u"创建时间", auto_now_add=True)
    enable = models.BooleanField(verbose_name="启用", default=True)
    del_flag = models.BooleanField(verbose_name="删除", default=False)

    class Meta(object):  # pylint: disable=C0111
        db_table = "t_timed_task"
        verbose_name = verbose_name_plural = u"定时任务"

    def __str__(self):
        return self.name


class TimedTaskLog(VModel):
    """定时任务日志"""
    script = models.CharField(verbose_name="任务执行脚本", max_length=200, db_index=True)
    param = models.CharField(verbose_name="参数", max_length=256, blank=True, null=True)
    exception_log = models.TextField(verbose_name="异常日志", blank=True, null=True)
    begin_time = models.DateTimeField(verbose_name=u"开始时间", auto_now_add=True)
    end_time = models.DateTimeField(verbose_name=u"结束时间", blank=True, null=True)
    update_time = models.DateTimeField(verbose_name=u'修改时间', auto_now=True)

    class Meta(object):  # pylint: disable=C0111
        db_table = "t_timed_task_log"
        verbose_name = verbose_name_plural = u"定时任务日志"
        ordering = ("-begin_time",)

    def __str__(self):
        return "%s(%s)" % (self.script, self.begin_time)
