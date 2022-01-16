#!/usr/bin/python
# -*- coding=utf-8 -*-

from vadmin import widgets


class TimeIntervalFilter(widgets.Panel):
    def lookups(self, request, model_admin, value, dict_filter):
        self.append(widgets.DateTimePicker(name="create_time_1", value=dict_filter.get("create_time_1", None),
                                           placeholder="开始时间"))
        self.append(widgets.Text(" -- "))
        self.append(widgets.DateTimePicker(name="create_time_2", value=dict_filter.get("create_time_1", None),
                                           placeholder="结束时间"))

    def queryset(self, request, queryset, value, dict_filter):
        # if value:
        #     import operator
        #     from django.db import models
        #     from functools import reduce
        #     # 自定义多个或查询
        #     or_queries = [models.Q(**{"multiple__icontains": sig_value})
        #                   for sig_value in value.split(",")]
        #     queryset = queryset.filter(reduce(operator.or_, or_queries))

        # 根据dict_filter过滤
        return queryset


class MultipleFilter(widgets.Select):
    def __init__(self, **kwargs):
        kwargs["name"] = "multiple"
        super().__init__(**kwargs)

    def lookups(self, request, model_admin, value=None, dict_filter=None):
        self.placeholder = "城市多选"
        self.multiple = True  # 可以多选
        self.value = value

        return [["1", u"北京"], ["2", u"上海"], ["3", u"武汉"], ["4", u"深圳"], ["5", u"成都"], ["6", u"西安"]]

    def queryset(self, request, queryset, value):
        if value:
            import operator
            from django.db import models
            from functools import reduce
            # 自定义多个或查询
            or_queries = [models.Q(**{"multiple__icontains": sig_value})
                          for sig_value in value.split(",")]
            queryset = queryset.filter(reduce(operator.or_, or_queries))

        return queryset


class MonthFilter(widgets.Select):

    def lookups(self, request, model_admin, value=None, dict_filter=None):
        self.multiple = True  # 可以多选
        self.value = value

        return [[1, 1], [2, 2], [3, 3]]

    def queryset(self, request, queryset, value):
        return queryset


class BeginDateFilter(widgets.DatePicker):
    def __init__(self, **kwargs):
        kwargs["name"] = "begin_date"
        super().__init__(**kwargs)

    def lookups(self, request, model_admin, value, dict_filter):
        self.placeholder = "开始日期"

        if "begin_date" in dict_filter:
            self.value = value
        else:
            # self.value = "2019-12-31"
            pass
        return None

    def queryset(self, request, queryset, value):
        queryset = queryset.filter(create_time__gte="%s 00:00:00" % value)
        return queryset


class EndDateTimeFilter(widgets.DateTimePicker):
    title = u'结束时间'
    parameter_name = 'end_date'

    def lookups(self, request, model_admin, value=None, dict_filter=None):
        self.value = value
        return None

    def queryset(self, request, queryset, value):
        if value:
            queryset = queryset.filter(create_time__lte=value)
        return queryset


class ProvinceFilter(widgets.Cascader):

    def lookups(self, request, model_admin, value=None, dict_filter=None):
        self.name = "province_cascader"
        self.placeholder = "省市区"

        self.data = [{"id": 1, "label": "湖北", "children": [{"id": 2, "label": "武汉"}, {"id": 3, "label": "武汉1"}, ]}]
        self.value = value
        self.any_level = True
        return self.data

    def queryset(self, request, queryset, value):
        # queryset = queryset.filter(create_time__lte=value)
        return queryset
