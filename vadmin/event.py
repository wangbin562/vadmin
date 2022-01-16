# !/usr/bin/python
# -*- coding=utf-8 -*-
import collections


class Event(object):
    def __init__(self, type="click", step=None, param=None):
        """
        :param type:事件类型
        :param step:事件对应的事件列表
        :param param:事件对应的事件列表
        """
        self.type = type
        if step is None:
            self.step = []
        elif isinstance(step, (tuple, list)):
            self.step = step
        else:
            self.step = [step, ]
        self.param = param

    def render(self):
        dict_data = collections.OrderedDict()
        dict_data["type"] = self.type
        dict_data["step"] = self.step
        if self.param is not None:
            dict_data["param"] = self.param

        return dict_data
