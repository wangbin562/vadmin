# !/usr/bin/python
# -*- coding=utf-8 -*-
from vadmin import admin_api


class Animation(object):
    def __init__(self, type=None, duration=None, timing_function=None, delay=None, iteration_count=None,
                 direction=None, keyframes=None, change_style=None):
        self.type = type
        self.duration = duration
        self.timing_function = timing_function
        self.delay = delay
        self.iteration_count = iteration_count
        self.direction = direction
        self.keyframes = keyframes
        self.change_style = change_style

    # def __setattr__(self, n, v):
    #     if n == "kwargs":
    #         self.__dict__["kwargs"] = v
    #     else:
    #         self.kwargs[n] = v
    #
    # def __getattr__(self, n):
    #     if n == "kwargs":
    #         return self.kwargs
    #     else:
    #         return self.kwargs.get(n, None)

    def render(self):
        dict_data = dict()
        for k, v in self.__dict__.items():
            if isinstance(v, bool):
                v = int(v)

            if v is not None:
                dict_data[k] = v

        return dict_data
