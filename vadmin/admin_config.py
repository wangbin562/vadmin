# !/usr/bin/python
# -*- coding=utf-8 -*-
"""
admin config
"""
from vadmin import const


class AdminListConfig(object):
    """
    admin配置结构
    """

    def __init__(self, request, model_admin):
        self.lst_display = model_admin.get_list_display(request)
        if self.lst_display == ('__str__',):
            self.lst_display = []

        self.lst_filter = model_admin.get_list_filter(request)
        self.lst_search = model_admin.get_search_fields(request)
        # self.lst_display = lst_display
        self.lst_display_links = model_admin.get_list_display_links(request, self.lst_display)
        self.lst_editable = model_admin.get_list_editable(request)

        # self.lst_actions = lst_actions
        # self.lst_sort = lst_sort
        # self.sortable = sortable
        self.export = model_admin.has_export(request)
        self.export_config = model_admin.get_export_config(request)
        # self.actions = model_admin.get_actions(request)
        # self.lst_v_button_list = lst_v_button_list
        self.change_list_url = model_admin.get_change_list_url(request)
        self.table_config = model_admin.get_change_list_config(request)
        self.table_order = model_admin.has_order(request)
        self.row_opera = model_admin.has_row_opera(request)
        # self.v_change_list_opera = v_change_list_opera  # 是否有操作列
