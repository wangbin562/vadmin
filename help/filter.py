#!/usr/bin/python
# -*- coding=utf-8 -*-

from vadmin import widgets


class HelpMenuFilter(widgets.Cascader):
    title = u'帮助菜单'
    parameter_name = 'help_menu'

    def lookups(self, request, model_admin, value=None, dict_filter=None):
        from vadmin import service
        from help.models import HelpMenu
        self.value = value
        data = []
        service.make_multilevel_data(HelpMenu.objects.all(), "name", "parent_id", None, data)

        return data

    def queryset(self, request, queryset, value=None, dict_filter=None):
        queryset = queryset.filter(help_menu_id=value)
        return queryset
