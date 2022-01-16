# -*- coding: utf-8 -*-
import datetime
import json


class DatetimeEncoder(json.JSONEncoder):

    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            return obj.strftime('%Y-%m-%d %H:%M')
        elif isinstance(obj, datetime.date):
            return obj.strftime('%Y-%m-%d')
        else:
            return json.JSONEncoder.default(self, obj)


class NoneEncoder(json.JSONEncoder):

    def default(self, obj):
        if isinstance(obj, None):
            return ''
        else:
            return json.JSONEncoder.default(self, obj)