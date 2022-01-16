# !/usr/bin/python
# -*- coding=utf-8 -*-

import datetime
import decimal
import json

from vadmin import animation
from vadmin import event
from vadmin import step
from vadmin import widgets
from vadmin import widgets_ex


class Encoder(json.JSONEncoder):

    def default(self, obj):
        if isinstance(obj, (step.Step, widgets.Widget, event.Event, widgets_ex.WidgetEx, animation.Animation)):
            return obj.render()
        elif isinstance(obj, decimal.Decimal):
            return float(obj)
        # elif isinstance(obj, (type(ugettext_lazy("")), type(gettext_lazy("")), type(pgettext_lazy("")))):
        elif "__proxy__'>" in str(type(obj)):
            return str(obj)
        elif isinstance(obj, datetime.datetime):
            return obj.strftime('%Y-%m-%d %H:%M:%S')
        elif isinstance(obj, datetime.date):
            return obj.strftime('%Y-%m-%d')
        elif isinstance(obj, datetime.time):
            return obj.strftime('%H:%M:%S')
        elif isinstance(obj, bytes):
            from base64 import b64encode
            # return b64encode(obj)
            return b64encode(obj).decode("utf-8")
        # elif isinstance(obj, bytes):
        #     return obj
        else:
            try:
                return json.JSONEncoder.default(self, obj)
            except (BaseException,):
                try:
                    return json.JSONEncoder.default(self, str(obj))
                except (BaseException, ):
                    pass
