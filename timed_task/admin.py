# !/usr/bin/python
# -*- coding=utf-8 -*-
# pylint: disable=C0111

from django.contrib import admin
from django.forms.models import ModelForm

from timed_task.models import TimedTask
from timed_task.models import TimedTaskLog
from utils import calc_time
from vadmin import const
from vadmin import step
from vadmin import widgets
from vadmin.admin import VModelAdmin


class TimedTaskForm(ModelForm):
    v_widgets = {
        'name': widgets.Widget(width=690),
        'desc': widgets.Widget(width=690),
        'script': widgets.Widget(width=690),
        'param': widgets.Widget(width=690),
        'run_mode': widgets.Radio(theme="button"),
        'cycle_mode': widgets.Radio(),
    }


@admin.register(TimedTask)
class TimedTaskAdmin(VModelAdmin):
    """
    定时任务
    """
    form = TimedTaskForm
    list_display = ['name', 'script', 'run_mode', 'cycle_mode', 'cycle_time',
                    'interval_time', 'max_log_number',
                    'run_number', 'last_run_time', 'wait_last', 'enable']
    search_fields = ['name', 'script']
    list_filter = ['enable']
    change_list_config = {
        "col_width": {'enable': 60, 'cycle_mode': 80, 'run_mode': 90, 'wait_last': 60,
                      "max_run_number": 80, "max_log_number": 80, "run_number": 80,
                      "cycle_time": 100, "interval_time": 120, "last_run_time": 110}
    }

    fieldsets = (
        (None, {'fields': ('name', 'script', "param", "run_mode",
                           ("cycle_mode", "cycle_time"), ("interval_begin_time", "interval_time"),
                           ("wait_last", "max_log_number"),
                           ("max_run_number", "run_number"),
                           ("last_run_time", "enable",),
                           "last_exception_log",
                           ("last_begin_time", "last_end_time",),
                           )}),
    )
    readonly_fields = ["run_number", "last_exception_log", "last_begin_time", "last_end_time"]

    def get_change_form_custom(self, request, obj=None):
        """
        获取form页面自定义功能按钮（在"保存"前面）
        """
        if obj and obj.script and request.user.is_superuser:
            url = const.URL_RUN_SCRIPT % ("timed_task.service.run_task_sync?script=" + obj.script)
            return widgets.Button(text="立即执行", step=step.Get(url=url))

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser

    def get_search_results(self, request, queryset, search_term):
        queryset, use_distinct = super().get_search_results(request, queryset, search_term)
        # queryset = queryset.filter(del_flag=False)
        return queryset, use_distinct

    def save_before(self, request, old_obj, data, dict_error, inline_data=None):
        if data["run_mode"] == 2:
            if not data["interval_time"]:
                dict_error['interval_time'] = "间隔执行模式，必须填写间隔时间!"
            else:
                try:
                    eval(data["interval_time"])
                except (BaseException,):
                    dict_error['interval_time'] = "间隔时间格式填写错误!"
        else:
            if not data["cycle_mode"]:
                dict_error['cycle_mode'] = "周期执行，必须填写周期执行模式!"
                return

            if not data["cycle_time"]:
                dict_error['cycle_time'] = "周期执行，必须填写周期执行时间!"
                return

            try:
                cycle_time = data["cycle_time"]
                if data["cycle_mode"] == "year":
                    s_date, s_time = cycle_time.split(" ")
                    month, day = s_date.split("-")
                    hour, minute, second = s_time.split(":")
                    if not (0 < int(month) < 12):
                        dict_error['cycle_time'] = "周期执行模式，周期执行时间格式错误，请查看帮助!"

                    if not (0 < int(day) < 31):
                        dict_error['cycle_time'] = "周期执行模式，周期执行时间格式错误，请查看帮助!"

                elif data["cycle_mode"] == "month":
                    day, s_time = cycle_time.split(" ")
                    hour, minute, second = s_time.split(":")
                    if not (0 < int(day) < 31):
                        dict_error['cycle_time'] = "周期执行模式，周期执行时间格式错误，请查看帮助!"

                elif data["cycle_mode"] == "week":
                    s_week, s_time = cycle_time.split(" ")
                    hour, minute, second = s_time.split(":")
                    if not (0 <= int(s_week) <= 6):
                        dict_error['cycle_time'] = "周期执行模式，周期执行时间格式错误，请查看帮助!"
                else:
                    hour, minute, second = cycle_time.split(":")

                if not (0 <= int(hour) < 24):
                    dict_error['cycle_time'] = "周期执行模式，周期执行时间格式错误，请查看帮助!"

                if not (0 <= int(minute) < 60):
                    dict_error['cycle_time'] = "周期执行模式，周期执行时间格式错误，请查看帮助!"

                if not (0 <= int(second) < 60):
                    dict_error['cycle_time'] = "周期执行模式，周期执行时间格式错误，请查看帮助!"

            except (BaseException,):
                dict_error['cycle_time'] = "周期执行模式，周期执行时间格式错误，请查看帮助!"


class TimedTaskLogForm(ModelForm):
    v_widgets = {
        'exception_log': widgets.Widget(width=690, height=240),
    }


@admin.register(TimedTaskLog)
class TimedTaskLogAdmin(VModelAdmin):
    """
    定时任务日志
    """
    form = TimedTaskLogForm
    list_v_display = ['script', 'param', 'begin_time', 'end_time', 'duration', 'exception_log']
    search_fields = ["script"]
    fieldsets = (
        (None, {'fields': ("script", "param", 'begin_time', 'end_time', 'exception_log')}),
    )

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def duration(self, request, obj):
        if obj.begin_time and obj.end_time:
            return calc_time.format_time_duration(calc_time.subtract_time(obj.end_time, obj.begin_time))

    duration.short_description = "执行时长"
