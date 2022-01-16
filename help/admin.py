# !/usr/bin/python
# -*- coding=utf-8 -*-
# pylint: disable=C0111

from django.contrib import admin
from django.forms.models import ModelForm

from help import filter
from help.models import HelpContent
from help.models import HelpMenu
from help.models import HelpMenuLeft
from help.models import HelpWidgetEvent
from help.models import HelpWidgetParam
from vadmin import widgets
from vadmin.admin import VModelAdmin
from vadmin import const


@admin.register(HelpMenu)
class HelpMenuAdmin(VModelAdmin):
    """
    帮助菜单
    """
    list_display = ['label', 'key', 'create_time', 'del_flag']
    exclude = ['order', 'create_time', 'update_time']
    change_list_config = {"order": True}


class HelpWidgetParamForm(ModelForm):
    v_widgets = {
        'desc': widgets.Input(input_type="textarea", width="95%"),
        'value': widgets.Input(input_type="textarea", width="95%"),
        'type': widgets.Widget(width="100%"),
    }


@admin.register(HelpWidgetParam)
class HelpWidgetParamAdmin(VModelAdmin):
    """组件参数"""
    form = HelpWidgetParamForm
    list_display = ['help_menu_left', 'name', 'desc', 'type', 'value', 'default', 'required', 'pc', 'phone']
    change_list_config = {
        "order": True,
        "col_width": {"name": 160, "type": 100, "default": 120, "required": 60, 'pc': 60, "phone": 60}
    }


class HelpWidgetEventForm(ModelForm):
    v_widgets = {
        'desc': widgets.Input(input_type="text", width="90%"),
        'param': widgets.Input(input_type="text", width="90%"),
    }


@admin.register(HelpWidgetEvent)
class HelpWidgetEventAdmin(VModelAdmin):
    """组件事件"""
    form = HelpWidgetEventForm
    list_display = ['help_menu_left', 'name', 'desc', 'param']
    change_list_config = {"order": True}


class HelpContentForm(ModelForm):
    v_widgets = {
        'title': widgets.Widget(width=600),
        'sub_title': widgets.Widget(width=600),
        'content': widgets.Widget(width="90%", height=400),
        'code': widgets.Widget(width="90%", height=600),
    }


@admin.register(HelpContent)
class HelpContentAdmin(VModelAdmin):
    """
    帮助内容
    """
    form = HelpContentForm
    list_display = ['help_menu_left', 'title', 'sub_title', 'create_time']
    list_v_filter = ['help_menu_left', ]
    search_fields = ['title', 'sub_title', 'content']
    exclude = ['link', 'order', 'create_time', 'update_time']
    change_list_config = {"order": True}

    # def form_help_menu(self, request, obj=None):
    #     if obj:
    #         value = obj.help_menu_id
    #     else:
    #         value = None
    #
    #     data = []
    #     service.make_multilevel_data(HelpMenu.objects.all(), "name", "parent_id", None, data)
    #
    #     return {"name": "帮助菜单", "widget": widgets.Cascader(name="help_menu_id", data=data, value=value, value_type="str")}


@admin.register(HelpMenuLeft)
class HelpMenuLeftAdmin(VModelAdmin):
    """
    帮助菜单
    """
    list_display = ['help_menu', 'label', 'key', 'create_time', 'del_flag']
    exclude = ['order', 'create_time', 'update_time']
    change_list_config = {"order": True, }
    list_v_filter = ['help_menu']
    search_fields = ['label']
    tabs = [
        {"label": "基本信息", "icon": "", "fieldsets": (
            (None, {'fields': ('help_menu', 'label', 'key', 'del_flag')}),
            ("组件参数", {'fields': (HelpWidgetParamAdmin,)}),
            ("组件事件", {'fields': (HelpWidgetEventAdmin,)}),
        )},
        {"label": "内容", "icon": "", "fieldsets": (
            (None, {'fields': (HelpContentAdmin,)}),
        )}
    ]

    inline_config = {
        HelpContentAdmin: {
            "display": const.INLINE_DISPLAY_LIST,
            # "fields": ["course", "type", "name", "content", "answer", "update_time"]
        },
    }
