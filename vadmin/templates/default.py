# !/usr/bin/python
# -*- coding=utf-8 -*-
"""
默认模板样式（样式参考element UI)
"""
import copy
import importlib
import random
import json

from django.conf import settings
from django.contrib import admin
from django.contrib.auth import get_user_model
from django.utils.translation import ugettext_lazy as _
from django.db.models import Q

from vadmin import admin_api
from vadmin import admin_config
from vadmin import common
from vadmin import const
from vadmin import event
from vadmin import field_translate
from vadmin import menu
from vadmin import step
from vadmin import step_ex
from vadmin import widget_view
from vadmin import widgets
from vadmin import animation


class Style(object):
    """
    布局的位置配置
    """

    def __init__(self):
        self.HEIGHT_TOP = 70  # 头部高度
        self.WIDTH_LEFT = 220  # 左边宽度
        self.HEIGHT_TITLE = 50  # 标题高度
        self.HEIGHT_BOTTOM = 50  # 底部高度
        self.MARGIN_TOP = 10  # 内容区域顶部填充
        self.MARGIN_BOTTOM = 10  # 内容区域底部填充
        self.MARGIN_LEFT = 10  # 内容区域左边填充
        self.MARGIN_RIGHT = 10  # 内容区域右边填充
        self.MARGIN = "10,10,10,10"


class Page(Style):
    def __init__(self, request, o_theme):
        Style.__init__(self)
        self.request = request
        self.o_theme = o_theme
        self.lst_menu = menu.get_menu(self.request)

        if const.UPN_TOP_ID in request.GET and const.UPN_LEFT_ID in request.GET:
            self.top_id = request.GET[const.UPN_TOP_ID].lower()
            self.menu_id = self.left_id = request.GET[const.UPN_LEFT_ID].lower()

        if const.UPN_MENU_ID in request.GET:
            self.menu_id = request.GET[const.UPN_MENU_ID].lower()
            self.top_id, self.left_id = menu.get_top_left_id(request, self.menu_id)
        else:
            path = request.path.strip("/")
            lst_path = path.split("/")
            if "v_list" in lst_path:
                idx = lst_path.index("v_list")
                self.left_id = "model:%s.%s" % (lst_path[idx + 1], lst_path[idx + 2])
            elif self.lst_menu:
                self.top_id, self.left_id = menu.get_first_top_left_id(self.lst_menu[0])
            else:
                self.top_id = None
                self.left_id = None
                self.menu_id = None

        if self.left_id:
            self.menu_id = self.left_id
        else:
            self.menu_id = self.top_id

        self.screen_width = int(request.GET.get(const.UPN_SCREEN_WIDTH, 1920))

    def create(self, o_content=None):
        o_page = widgets.Page(bg_color=self.o_theme.bg_color)
        url = common.make_url(const.URL_TOP, self.request)
        o_top = widgets.Panel(height=self.HEIGHT_TOP, width="100%", float={"top": 0, "left": 0},
                              bg_color=self.o_theme.top_bg_color, url=url)
        o_page.add_widget(o_top)

        if settings.V_TOP_HOVER:
            o_page.append(widgets.Row(height=self.HEIGHT_TOP))

        o_grid = widgets.Grid(name=const.WN_CONTENT, col_num=2, height="100vh-%s" % self.HEIGHT_TOP, vertical="top",
                              bg={"color": self.o_theme.bg_color})
        # o_grid.set_col_attr(col=0, width=0)

        if self.left_id is not None:
            url = common.make_url(const.URL_LEFT, param={const.UPN_MENU_ID: self.menu_id})
            o_grid.set_col_attr(col=0, width=self.WIDTH_LEFT, url=url, scroll={"y": "auto"})
            o_grid.set_col_attr(col=1, width="100%%-%s" % self.WIDTH_LEFT)
        else:
            o_grid.set_col_attr(col=0, width=0, scroll={"y": "auto"})
            o_grid.add_widget(col=0, widget=self.create_left())  # 位置打桩

        if o_content:
            o_grid.add_widget(col=1, widget=o_content)
        else:
            url, href = menu.get_url_by_menu_id(self.menu_id)
            if href:
                o_panel = widgets.Panel(name=const.WN_CONTENT_RIGHT, vertical="top", width="100%", height="100%",
                                        href=href)
                o_grid.add_widget(col=1, widget=o_panel)
            else:
                url = common.make_url(url, self.request)
                o_panel = widgets.Panel(name=const.WN_CONTENT_RIGHT, vertical="top", width="100%", height="100%",
                                        url=url)
                o_grid.add_widget(col=1, widget=o_panel)

        o_page.add_widget(o_grid)

        return o_page

    def create_top(self):
        menu_position = self.o_theme.menu_position
        o_top = widgets.Grid(name=const.WN_TOP, col_num=2, vertical="center",
                             height=self.HEIGHT_TOP, bg_color=self.o_theme.top_bg_color, width="100%")
        o_title = self.make_title()
        o_top.add_widget(o_title, col=0)
        font_color = common.calc_black_white_color(self.o_theme.top_bg_color)
        bg_color = common.calc_hover_color(self.o_theme.top_bg_color)
        font_size = self.o_theme.font["size"] + 2
        font = {"color": font_color, "size": font_size}

        if menu_position == "top":
            hover = self.o_theme.menu.get("hover", {})
            hover["bg_color"] = bg_color
            hover["font_color"] = font_color
            focus = self.o_theme.menu.get("focus", {})
            if "bg_color" not in focus:
                focus["bg_color"] = bg_color

            top_menu = widgets.Menu(name=const.WN_MENU_TOP,
                                    width="100%%-%s" % o_title.width, height=self.HEIGHT_TOP,
                                    direction="horizontal", bg={"color": self.o_theme.top_bg_color},
                                    font=font, focus=focus, hover=hover)

            for dict_item in self.lst_menu:
                top_id, left_id = menu.get_first_top_left_id(dict_item)
                dict_menu = copy.deepcopy(dict_item)
                if "children" in dict_menu:
                    del dict_menu["children"]

                dict_menu["id"] = top_id
                url = common.make_url(const.URL_HOME,
                                      param={const.UPN_TOP_ID: top_id, const.UPN_MENU_ID: left_id,
                                             const.UPN_SCREEN_WIDTH: "{{window.innerWidth}}"})
                dict_menu["step"] = step.Post(url=url, jump=True, submit_type="hide")

                top_menu.add_item(dict_menu)

            top_menu.value = self.top_id
            o_top.add_widget(top_menu, col=0)

        width = 30
        # 自定义的
        lst_widget = []
        if callable(settings.V_TOP_ADD_ITEMS):
            for o_widget in settings.V_TOP_ADD_ITEMS(self.request):
                lst_widget.append(o_widget)
        else:
            for o_widget in settings.V_TOP_ADD_ITEMS or []:
                lst_widget.append(o_widget)

        if settings.V_TOP_ICON:
            if settings.V_TOP_THEME:
                o_widget = widgets.Button(prefix="el-icon-brush", tooltip=u"设置主题和布局", tooltip_interval_time=100,
                                          step=step.Post(url="v_theme_view/", jump=True, submit_type="hide"))
                lst_widget.append(o_widget)

            if settings.V_TOP_UPDATE_PWD:
                o_step = widget_view.make_update_pwd(self.request, self.o_theme)
                o_widget = widgets.Button(prefix="el-icon-unlock", tooltip=u"修改密码", tooltip_interval_time=100,
                                          step=o_step)
                lst_widget.append(o_widget)

            o_widget = widgets.Button(prefix="el-icon-switch-button", tooltip=u"退出", tooltip_interval_time=100,
                                      step=step.Get(url="v_logout/", submit_type="hide"))
            lst_widget.append(o_widget)

            o_widget = widgets.Button(prefix="el-icon-user", tooltip=u"欢迎您，%s" % self.request.user,
                                      tooltip_interval_time=100)
            lst_widget.append(o_widget)

        all_width = 6
        for o_widget in lst_widget:
            o_widget.bg = {"color": self.o_theme.top_bg_color}
            o_widget.border = {"radius": 0}
            if o_widget.get("width", None) is None:
                o_widget.width = width
            all_width += o_widget.width
            o_widget.height = self.HEIGHT_TOP
            o_widget.font = {"color": font_color}
            o_widget.hover = {"bg_color": bg_color}

        o_top.add_widget(lst_widget, col=1)
        o_top.set_col_attr(col=0, width="100%%-%s" % all_width)
        o_top.set_col_attr(col=1, width=all_width, horizontal="right")
        return o_top

    def create_left(self):
        font_color = common.calc_black_white_color(self.o_theme.left_bg_color)
        font_size = self.o_theme.font["size"] + 1
        font = {"color": font_color, "size": font_size}

        o_menu_left = None
        if self.o_theme.menu_position == "left":
            menu_data = list()
            menu.make_left_menu_list(self.request, self.lst_menu, menu_data)
            o_menu_left = widgets.Menu(name=const.WN_CONTENT_LEFT, width="100%",
                                       height="100vh-%s" % self.HEIGHT_TOP,
                                       value=self.left_id, data=menu_data,
                                       font=font)
        else:
            for i, dict_item in enumerate(self.lst_menu):
                menu_id = menu.get_menu_id(dict_item)
                if menu_id == self.top_id:
                    if "children" in dict_item:
                        menu_data = list()
                        menu.make_left_menu_list(self.request, dict_item["children"], menu_data)
                        o_menu_left = widgets.Menu(name=const.WN_CONTENT_LEFT, width="100%",
                                                   height="100vh-%s" % self.HEIGHT_TOP,
                                                   value=self.left_id, data=menu_data,
                                                   font=font)
                    break

        if o_menu_left:
            hover = self.o_theme.menu.get("hover", {})
            hover["bg_color"] = common.calc_focus_color(self.o_theme.left_bg_color)
            hover["font_color"] = common.calc_black_white_color(self.o_theme.left_bg_color)
            focus = self.o_theme.menu.get("focus", {})
            focus["bg_color"] = hover["bg_color"]

            o_menu_left.hover = hover
            o_menu_left.focus = focus
            o_menu_left.bg = {"color": self.o_theme.left_bg_color}

        return o_menu_left

    def make_title(self):
        left_width = self.WIDTH_LEFT
        logo = settings.V_LOGO
        title = settings.V_TITLE
        o_panel = widgets.Panel(height="100%")
        if logo:
            import os
            from PIL import Image
            logo_path = os.path.abspath(settings.BASE_DIR + settings.STATIC_URL + logo)
            im = Image.open(logo_path)
            image_height = self.HEIGHT_TOP - 10
            if im.height <= image_height:
                image_height = im.height
                image_width = im.width
            else:
                image_width = int(float(image_height) / im.height * im.width)
            im.close()

            width = len(title) * 22 + image_width + 20
            width = left_width if width < left_width else width
            o_panel.width = width
            o_panel.add_widget(widgets.Image(href=settings.STATIC_URL + logo, width=image_width,
                                             height=image_height, margin_left=10))

        else:
            width = len(title) * 22 + 10
            width = left_width if width < left_width else width
            o_panel.width = width

        font_color = common.calc_black_white_color(self.o_theme.top_bg_color)
        o_text = widgets.Text(text=title, margin_left=10, font={"size": 20, "color": font_color})
        o_panel.add_widget(o_text)
        return o_panel


class ChangeList(Style):
    def __init__(self, request, app_label, model_name, o_theme):
        Style.__init__(self)
        self.request = request
        self.app_label = app_label.lower()
        self.model_name = model_name.lower()
        self.o_theme = o_theme
        self.model_admin = admin_api.get_model_admin(app_label, model_name)

        p_name = const.WN_PAGINATION % self.model_name
        self.page_index = int(request.GET.get(p_name, 1))

        self.config = admin_config.AdminListConfig(request, self.model_admin)
        self.lst_display = self.config.lst_display  # 显示的列
        self.filter_name = []  # 过滤的字段名称
        self.row_id = None  # 选择的行ID
        self.row_id_field = "pk"  # 行ID字段
        self.queryset = None  # 过滤后内容

        self.is_title = True  # 是否构造标题
        self.is_top = True  # 是否构造顶部区域
        self.is_bottom = True  # 是否构造底部区域

        self.readonly = False

        # 子表嵌入显示、关联字段选择
        self.display_mode = request.GET.get(const.UPN_DISPLAY_MODE, None)  # "popup": 弹出选择 "child":子表

        self.related_field_name = request.GET.get(const.UPN_RELATED_FIELD, None)  # 关联的字段名称（此表作为外键子表）
        self.related_object_id = request.GET.get(const.UPN_RELATED_ID, None)  # 关联的对象ID
        self.related_app_label = request.GET.get(const.UPN_RELATED_APP, None)
        self.related_model_name = request.GET.get(const.UPN_RELATED_MODEL, None)

    def make_list_view(self, queryset=None, row_id=None, row_id_field=None):
        """
        构造列表页
        """
        if self.display_mode == const.DM_LIST_SELECT:
            self.config.row_opera = False

        self.row_id = row_id
        self.row_id_field = row_id_field or "pk"
        if queryset is None:
            queryset = admin_api.get_filter_queryset(self.request, self.model_admin)

        o_panel = widgets.Panel(name=const.WN_CONTENT_RIGHT,
                                vertical="top",
                                height="100vh-%s" % self.HEIGHT_TOP,
                                width="100%",
                                bg={"color": self.o_theme.bg_color},
                                padding=self.MARGIN)

        if self.is_title:
            title_area = self.make_title()
            o_panel.add_widget(title_area)

        o_panel_sub = self.make_list_view_child(queryset)
        o_panel.add_widget(o_panel_sub)
        return o_panel

    def make_list_view_child(self, queryset):
        if self.display_mode == const.DM_LIST_SELECT:
            self.config.row_opera = False

        self.queryset = queryset
        o_panel = widgets.Panel(name=const.WN_CHANGE_LIST % (self.app_label, self.model_name),
                                vertical="top", width="100%",
                                height="100%%-%s" % self.HEIGHT_TITLE)
        if self.is_top:
            top_area = self.make_top_area()
            top_area.name = const.WN_CONTENT_FILTER
            o_panel.add_widget(top_area)

        result = self.model_admin.make_list_table(self.request, self, queryset)
        if isinstance(result, (tuple, list)):
            o_table, queryset = result
        else:
            o_table = result

        if o_table is None:
            o_table = self.make_list_table(queryset)

        o_table.value = self.row_id
        if self.display_mode == const.DM_LIST_SELECT:
            o_table.select = "single"
            o_table.submit_format = "select"
            o_table.height = "90vh-%s-%s" % (self.HEIGHT_TITLE + self.MARGIN_TOP + self.MARGIN_BOTTOM + 4 +
                                             self.HEIGHT_BOTTOM, const.WN_CONTENT_FILTER)

        elif self.display_mode == const.DM_LIST_CHILD:
            # o_table.height = "100vh-%s-%s" % (
            #     (self.HEIGHT_TOP + 16 + self.HEIGHT_TOP + self.MARGIN_BOTTOM + self.HEIGHT_BOTTOM),
            #     const.WN_CONTENT_FILTER)
            pass
        else:
            height = "100vh-%s-%s" % (self.HEIGHT_TOP + self.MARGIN_TOP +
                                      self.HEIGHT_TITLE + self.HEIGHT_BOTTOM + self.MARGIN_BOTTOM + 4,
                                      const.WN_CONTENT_FILTER)
            o_table.height = height

        o_panel.add_widget(widgets.Row(height=2))
        o_panel.add_widget(o_table)
        o_panel.add_widget(widgets.Row(height=2, bg_color=self.o_theme.bg_color))

        if self.is_bottom:
            bottom_area = self.make_bottom_area(queryset)
            o_panel.add_widget(bottom_area)

        return o_panel

    def make_title(self, title=None):
        o_title = self.model_admin.make_list_title(self.request, self)

        if o_title is None:
            o_title = widgets.Panel(width="100%", height=self.HEIGHT_TITLE,
                                    bg_image=settings.STATIC_URL + self.o_theme.title_image)
            font = {"size": self.o_theme.font["size"] + 2, "color": "#FFFFFF"}

            if title is None:
                menu_id = self.request.GET.get(const.UPN_MENU_ID, None)
                if menu_id:
                    title = menu.get_label(menu_id)

                if not title:
                    title = str(self.model_admin.opts.verbose_name)

            o_text = widgets.Text(text=title, padding_left=10, font=font)
            o_title.add_widget(o_text)

        return o_title

    def make_top_area(self):
        """构造头部区域"""
        o_grid = self.model_admin.make_list_top_area(self.request, self)
        if o_grid:
            return o_grid

        o_grid = widgets.Grid(col_num=3, bg={"color": self.o_theme.right_bg_color}, min_height=44)
        o_grid.set_col_attr(col=0, width=10)

        o_panel = self.make_opera()
        if const.UPN_SCREEN_WIDTH in self.request.GET:
            screen_width = int(self.request.GET[const.UPN_SCREEN_WIDTH])
            o_panel_filter = self.make_filter(screen_width - o_panel.width - self.WIDTH_LEFT - 20 -
                                              self.MARGIN_LEFT - self.MARGIN_RIGHT)
        else:
            o_panel_filter = self.make_filter()

        o_grid.set_col_attr(col=2, horizontal="right", width=o_panel.width)
        o_grid.append(o_panel)
        o_grid.append(o_panel_filter, col=1)

        return o_grid

    def make_bottom_area(self, queryset):
        """构造底部区域"""
        bottom_area = self.model_admin.make_list_bottom_area(self.request, self)
        if bottom_area is None:
            bottom_area = widgets.Panel(bg_color=self.o_theme.right_bg_color, height=self.HEIGHT_BOTTOM)
            # if not self.display_mode:
            lst_widget = self.make_batch_area()
            bottom_area.add_widget(lst_widget)

            lst_widget = self.model_admin.make_list_pagination(self.request, self, queryset)
            if lst_widget == const.USE_TEMPLATE:
                lst_widget = self.make_list_pagination(queryset)

            if lst_widget:
                bottom_area.add_widget(lst_widget)

        bottom_area.width = "100%"
        return bottom_area

    def make_batch_area(self):
        """构造底部批量操作区域"""
        lst_widget = []

        if self.display_mode != const.DM_LIST_SELECT:
            o_button = self.model_admin.make_list_select_all(self.request, self, self.filter_name)
            if o_button:
                if isinstance(o_button, (tuple, list)):
                    lst_widget.extend(o_button)
                else:
                    lst_widget.append(o_button)

        # 导出
        if self.display_mode != const.DM_LIST_SELECT and self.config.export:
            o_button = self.model_admin.make_list_export(self.request, self)
            if o_button:
                lst_widget.append(o_button)

        # 批量删除
        if not self.display_mode and self.model_admin.has_delete_permission(self.request):
            o_button = self.model_admin.make_list_delete(self.request, self, self.filter_name)
            if o_button:
                lst_widget.append(o_button)

        # 自定义
        if self.display_mode != const.DM_LIST_SELECT:
            # 保存
            if self.config.lst_editable:
                o_button = self.model_admin.make_list_save(self.request, self)
                if o_button:
                    lst_widget.append(o_button)

            lst_custom = self.model_admin.get_change_list_batch_custom(self.request, self)
            if lst_custom:
                if isinstance(lst_custom, (tuple, list)):
                    # lst_widget.extend(lst_custom)
                    pass
                else:
                    lst_custom = [lst_custom, ]

                filter_name = copy.copy(self.filter_name)
                for o_custom in lst_custom:
                    o_step = o_custom.get("step", None)
                    if o_step and "request" in o_step.type:
                        if o_step.get("splice"):
                            if isinstance(o_step.splice, str):
                                o_step.splice = [o_step.splice]
                            o_step.splice += filter_name
                        else:
                            o_step.splice = filter_name
                    lst_widget.append(o_custom)

        return lst_widget

    def make_search_widget(self):
        """构造搜索组件"""
        dict_para = self.request.GET
        o_widget = None
        lst_search = self.model_admin.get_search_fields(self.request)
        if lst_search:
            if self.model_admin.search_placeholder:
                placeholder = self.model_admin.search_placeholder
            else:
                lst_placeholder = []
                for field_name in lst_search:
                    if "__" in field_name:
                        field, field_sub = field_name.split("__")[0:2]
                        db_field = admin_api.get_field(self.model_admin, field)
                        db_field_sub = admin_api.get_field_by_model(db_field.related_model, field_sub)
                        name1 = str(db_field.verbose_name)
                        name2 = str(db_field_sub.verbose_name)
                        if name2.find(name1) == 0:
                            verbose_name = name2
                        else:
                            verbose_name = name1 + name2
                        if verbose_name not in lst_placeholder:
                            lst_placeholder.append(verbose_name)

                    else:
                        try:
                            db_field = admin_api.get_field(self.model_admin, field_name)
                            verbose_name = str(db_field.verbose_name)
                            if verbose_name not in lst_placeholder:
                                lst_placeholder.append(verbose_name)
                        except (BaseException,):
                            pass

                placeholder = "/".join(lst_placeholder)

            search_name = const.WN_SEARCH % (self.app_label, self.model_name)
            self.filter_name.append(search_name)
            o_widget = widgets.Input(name=search_name, value=dict_para.get(search_name, ""), placeholder=placeholder,
                                     padding_right=10, prefix=widgets.Icon(icon="el-icon-search"),
                                     tooltip=placeholder)

            if self.display_mode:
                p_name = const.WN_PAGINATION % self.model_name
                url = const.URL_LIST_FILTER % (self.model_admin.opts.app_label,
                                               self.model_admin.opts.model_name)

                dict_para = {
                    const.UPN_RELATED_APP: self.related_app_label,
                    const.UPN_RELATED_MODEL: self.related_model_name,
                    const.UPN_RELATED_FIELD: self.related_field_name,
                    const.UPN_RELATED_ID: self.related_object_id,
                    const.UPN_DISPLAY_MODE: self.display_mode}

                url = common.make_url(url, param=dict_para, filter=[p_name])
                o_step = step.Get(url=url, jump=False, splice=copy.copy(self.filter_name))

            else:
                # if not (self.is_popup or self.is_child):
                change_list = self.model_admin.get_change_list_url(self.request, self.page_index)
                o_step = step.Get(url=change_list, jump=True, splice=copy.copy(self.filter_name))
            o_event = event.Event(type="keydown", param=[13, 108], step=o_step)
            o_widget.add_event(o_event)

        return o_widget

    def make_opera(self):
        o_panel = widgets.Panel()
        if self.display_mode == const.DM_LIST_SELECT:
            o_button = self.make_ok_button()
            o_panel.append(o_button)

            o_button = self.make_close_button()
            o_panel.append(o_button)

        elif not self.readonly:
            o_button = self.make_add_button()
            o_panel.append(o_button)

        width = 0
        for o_widget in o_panel.get_children():
            if isinstance(o_widget, (dict, widgets.Widget)):
                o_widget.margin_top = "4px"
                width += o_widget.get("width", admin_api.get_widget_width(self.request, o_widget, 80))
            else:
                width += 80

        o_panel.width = width
        return o_panel

    def make_filter(self, panel_width=None):
        """构造过滤项"""
        dict_para = {}
        for k, v in self.request.GET.items():
            if k.find(const.WN_FILTER_KEY) == 0:
                k = k.replace(const.WN_FILTER_KEY, "", 1)
            dict_para[k] = v

        change_list_filter_config = self.model_admin.get_change_list_filter_config(self.request)
        fold = change_list_filter_config.get("fold", True)

        name = const.WN_CONTENT_RIGHT_FILTER
        value = int(self.request.GET.get(const.WN_CONTENT_FILTER_FOLD, 0))

        height = 44
        o_panel = widgets.Panel(name=name, height=height)
        if value:
            o_panel.height = "auto"

        margin = [4, 10, 4, 0]
        config_width = change_list_filter_config.get("width", 220)
        if panel_width:
            row_width = int(panel_width - 80 - 70)
            insert_number = 0
        else:
            row_width = None
            insert_number = 4

        width = 0
        filter_number = 0
        o_widget = self.make_search_widget()
        if o_widget:
            width = config_width + margin[1]
            o_widget.width = config_width
            o_widget.margin = margin
            o_panel.append(o_widget)
            filter_number += 1

        for field_name in self.model_admin.get_list_filter(self.request):
            if self.related_field_name == field_name:
                continue

            if isinstance(field_name, str):
                db_field = admin_api.get_field(self.model_admin, field_name)
                if "__" not in field_name:
                    field_name = db_field.get_attname()

                # 过滤外键也调用foreign_key_filter
                o_widget = field_translate.field_2_widget(self.request, self.model_admin, field_name,
                                                          is_filter=True,
                                                          value=dict_para.get(field_name, None))
                if o_widget is None:
                    continue

                o_widget.name = const.WN_FILTER_KEY + o_widget.name
                o_widget.submit = 0
                if o_widget.get_attr_value("placeholder") is None:
                    o_widget.placeholder = str(db_field.verbose_name)

            else:
                if callable(field_name):  # 回调自定义过滤器
                    o_widget = field_name()
                    o_widget.name = getattr(o_widget, "name", None) or getattr(o_widget, "parameter_name", None)
                    o_widget.value = dict_para.get(o_widget.name, None)
                    data = o_widget.lookups(self.request, self.model_admin, o_widget.value, dict_para)

                    if isinstance(o_widget, widgets.Panel):
                        for item in o_widget.get_children():
                            if item.get("name"):
                                self.filter_name.append(item.name)
                    else:
                        o_widget.placeholder = str(getattr(o_widget, "title", ""))
                        if data:
                            o_widget.data = data
                else:
                    o_widget = field_name
                    o_widget.value = dict_para.get(o_widget.name, None)

            if isinstance(o_widget, widgets.Widget):
                o_widget.margin = margin
                widget_width = admin_api.get_widget_width(self.request, o_widget, config_width)
                if widget_width > config_width:
                    o_widget.width = widget_width
                else:
                    o_widget.width = config_width

                if fold:
                    if row_width and (insert_number == 0) and ((width + widget_width + margin[1]) > row_width):
                        insert_number = filter_number
                        o_panel.append(widgets.Row())
                    elif (not row_width) and (filter_number == insert_number):
                        o_panel.append(widgets.Row())
                    else:
                        width += (widget_width + margin[1])

                o_panel.append(o_widget)
                self.filter_name.append(o_widget.name)
                filter_number += 1

        self.filter_name.append(const.WN_CONTENT_FILTER_FOLD)

        if filter_number > 0:
            o_button_search = self.make_search_button()
            if fold:
                if (filter_number > insert_number) and (insert_number > 0):
                    o_button_more = self.make_fold_button(height)
                    o_panel.insert(insert_number, o_button_search)
                    o_panel.insert(insert_number, o_button_more)
                else:
                    o_panel.append(o_button_search)
            else:
                o_panel.append(o_button_search)

        return o_panel

    def make_fold_button(self, height):
        name = const.WN_CONTENT_RIGHT_FILTER
        value = int(self.request.GET.get(const.WN_CONTENT_FILTER_FOLD, 0))
        show_animation = animation.Animation(change_style={"height": "auto"}, duration="0.3s")

        hide_animation = animation.Animation(change_style={"height": height}, duration="0.3s")

        table_height = "100vh-%s-%s" % (self.HEIGHT_TOP + self.MARGIN_TOP +
                                        self.HEIGHT_TITLE + self.HEIGHT_BOTTOM + self.MARGIN_BOTTOM + 4,
                                        const.WN_CONTENT_FILTER)
        table_name = const.WN_TABLE % (self.app_label, self.model_name)
        change_table_height = animation.Animation(change_style={"height": table_height}, duration="0.3s")
        o_button = widgets.ButtonMutex(name=const.WN_CONTENT_FILTER_FOLD, text="更多", active_text="折叠",
                                       prefix=widgets.Icon(icon="el-icon-caret-bottom",
                                                           margin="0 -5px 0 0"),
                                       active_prefix=widgets.Icon(icon="el-icon-caret-top",
                                                                  margin="0 -5px 0 0"),
                                       width=60,
                                       bg={"color": "transparent"},
                                       # focus={"bg_color": "transparent", "font_color": "#409EFF"},
                                       hover={"bg_color": "transparent", "font_color": "#409EFF"},
                                       font={"color": "#409EFF"},
                                       border={"color": "transparent", "width": 0},
                                       margin=4,
                                       value=value,
                                       event={
                                           "click": [
                                               step.RunAnimation(name=name, animation=show_animation),
                                               step.RunAnimation(name=table_name,
                                                                 animation=change_table_height)
                                           ]},
                                       active_event={
                                           "click": [
                                               step.RunAnimation(name=name, animation=hide_animation),
                                               step.RunAnimation(name=table_name,
                                                                 animation=change_table_height)
                                           ]}
                                       )
        return o_button

    def make_search_button(self):
        o_button = None
        filter_name = copy.copy(self.filter_name)
        if self.filter_name or self.model_admin.get_search_fields(self.request):
            if self.display_mode:
                p_name = const.WN_PAGINATION % self.model_name
                url = const.URL_LIST_FILTER % (self.model_admin.opts.app_label,
                                               self.model_admin.opts.model_name)

                dict_para = {
                    const.UPN_RELATED_APP: self.related_app_label,
                    const.UPN_RELATED_MODEL: self.related_model_name,
                    const.UPN_RELATED_FIELD: self.related_field_name,
                    const.UPN_RELATED_ID: self.related_object_id,
                    const.UPN_DISPLAY_MODE: self.display_mode}

                url = common.make_url(url, self.request, param=dict_para, filter=[p_name])
                o_button = self.model_admin.make_list_search(self.request, self, filter_name, url)

                if o_button:
                    if isinstance(o_button, (tuple, list)):
                        o_button[0].step.jump = False
                    else:
                        o_button.step.jump = False

            else:
                o_button = self.model_admin.make_list_search(self.request, self, filter_name)

        return o_button

    def make_add_button(self):
        lst_button = []
        # 添加自定义
        lst_custom = self.model_admin.get_change_list_custom(self.request)
        if not isinstance(lst_custom, (list, tuple)):
            lst_custom = [lst_custom, ]

        for o_button in lst_custom:
            lst_button.append(o_button)
            lst_button.append(widgets.Col(width=10))

        # 增加按钮
        if self.model_admin.has_add_permission(self.request):
            if self.display_mode:
                if self.related_object_id:  # 子表是弹出增加，必须先有父类
                    filter_name = copy.copy(self.filter_name)
                    url = const.URL_FORM_CHILD_POPUP % (self.app_label, self.model_name)
                    url = common.make_url(url, self.request, param={
                        const.UPN_DISPLAY_MODE: const.DM_FORM_POPUP,
                        const.UPN_RELATED_ID: self.related_object_id,
                        const.UPN_RELATED_FIELD: self.related_field_name,
                        const.UPN_RELATED_APP: self.related_app_label,
                        const.UPN_RELATED_MODEL: self.related_model_name,
                    }, filter=["id"])

                    o_step = step.Get(url=url, submit_type="hide", splice=filter_name)
                    prefix = widgets.Icon(icon="el-icon-circle-plus-outline")
                    o_button = widgets.Button(prefix=prefix, text="增加", step=o_step)
                else:
                    prefix = widgets.Icon(icon="el-icon-circle-plus-outline")
                    o_button = widgets.Button(prefix=prefix, text="增加", step=step.Msg(text="请先保存父类数据，才能增加子条目！"))

            else:
                filter_name = copy.copy(self.filter_name)
                o_button = self.model_admin.make_list_add(self.request, self, filter_name)
                if o_button is None:
                    url = self.model_admin.get_change_form_add_url(self.request)
                    if url is None:
                        url = const.URL_FORM_ADD % (self.app_label, self.model_name)

                    o_step = step.Post(url=url, submit_type="hide", jump=True, splice=filter_name)
                    prefix = widgets.Icon(icon="el-icon-circle-plus-outline")
                    o_button = widgets.Button(prefix=prefix, text="增加", step=o_step)

            lst_button.append(o_button)

        return lst_button

    def make_close_button(self):
        """关闭弹出层按钮"""
        o_step = step.LayerClose()
        o_button = widgets.Button(text="关闭", step=o_step, margin=4)
        return o_button

    def make_ok_button(self):
        """在弹出层上选择确定按钮"""
        url = const.URL_LIST_SELECT_CLOSE % (self.app_label, self.model_name)
        url = common.make_url(url, self.request,
                              param={
                                  const.UPN_RELATED_FIELD: self.related_field_name,
                                  const.UPN_RELATED_ID: self.related_object_id,
                                  const.UPN_RELATED_APP: self.related_app_label,
                                  const.UPN_RELATED_MODEL: self.related_model_name
                              })
        o_step = step.Post(url=url, submit_type="section",
                           section=[const.WN_TABLE % (self.app_label, self.model_name), self.related_field_name])
        o_button = widgets.Button(text="确定", event={"click": o_step}, margin=4)
        return o_button

    def make_head(self):
        """构造表头"""
        head = []  # 表格头部
        col_width = {}  # 列宽
        col_horizontal = {}  # 列对齐
        add_col = 0
        table_config = self.config.table_config

        dict_sort = admin_api.parse_sort_para(self.request, self.model_admin, True)
        col_sort = {}  # 支持的列排序
        col = 0

        for field_name in self.lst_display:
            fun = None
            if "col_width" in table_config:
                if field_name in table_config["col_width"]:
                    col_width[col + add_col] = table_config["col_width"][field_name]

            if "col_horizontal" in table_config:
                if field_name in table_config["col_horizontal"]:
                    col_horizontal[col + add_col] = table_config["col_horizontal"][field_name]

            # 自定义字段名称
            if ("col_name" in table_config) and \
                    (field_name in table_config["col_name"]):
                col_name = table_config["col_name"][field_name]
                head.append(col_name)

            # 外键字段
            elif "__" in field_name:
                field1, field2 = field_name.split("__")[0:2]
                db_field1 = admin_api.get_field(self.model_admin, field1)
                db_field = admin_api.get_field_by_model(db_field1.related_model, field2)
                if db_field.help_text:
                    o_icon = widgets.Icon(icon="el-icon-info", tooltip=str(db_field.help_text),
                                          tooltip_interval_time=100, margin_left=2)
                    head.append([str(db_field.verbose_name), o_icon])
                else:
                    head.append(str(db_field.verbose_name))
            else:
                try:
                    db_field = admin_api.get_field(self.model_admin, field_name)
                    if db_field.help_text:
                        o_icon = widgets.Icon(icon="el-icon-info", tooltip=str(db_field.help_text),
                                              tooltip_interval_time=100, margin_left=2)
                        head.append([str(db_field.verbose_name), o_icon])
                    else:
                        head.append(str(db_field.verbose_name))
                except (BaseException,):
                    # 自定义字段
                    fun = getattr(self.model_admin, field_name, None) or \
                          getattr(self.model_admin, "list_v_%s" % field_name, None)

                    if callable(fun):
                        if getattr(fun, "multiple_col", False):
                            lst_name = getattr(self.model_admin, "%s_short_description" % fun.__name__)(self.request)
                            head.extend(lst_name)

                        elif hasattr(fun, 'short_description'):
                            head.append(getattr(fun, 'short_description'))
                        else:
                            head.append(field_name)

            if fun is None:
                url = const.URL_LIST_FILTER % (self.app_label, self.model_name)

                dict_para = {
                    const.UPN_RELATED_APP: self.related_app_label,
                    const.UPN_RELATED_MODEL: self.related_model_name,
                    const.UPN_RELATED_FIELD: self.related_field_name,
                    const.UPN_RELATED_ID: self.related_object_id,
                    const.UPN_DISPLAY_MODE: self.display_mode
                }
                url = common.make_url(url, self.request, param=dict_para)
                col_sort[col + add_col] = {"url": url, "sort_type": dict_sort.get(field_name, None)}

            col += 1

        if self.config.row_opera and self.display_mode != const.DM_LIST_SELECT:
            head.append("操作")
            col_width[len(head) - 1] = 60

        return head, col_width, col_sort, col_horizontal

    def make_row_field(self, field_name, obj):
        # 第一列默认是排序列

        fun = getattr(self.model_admin, field_name, None) or getattr(self.model_admin, "list_v_%s" % field_name, None)
        # 回调自定义列
        if callable(fun):
            o_widget = fun(self.request, obj)

        elif (not self.display_mode) and (field_name in self.config.lst_display_links) and \
                self.model_admin.has_change_permission(self.request, obj):
            o_widget = field_translate.field_2_list_links(self.request, self.model_admin,
                                                          field_name, obj, self.filter_name)

        # 外键字段
        elif "__" in field_name:
            field1, field2 = field_name.split("__")[0:2]  # 只支持两级，多级自定义函数处理
            try:
                fk_obj = getattr(obj, field1)
            except (BaseException,):
                fk_obj = None

            if fk_obj is not None:
                # model_admin = admin.site._registry.get(fk_obj._meta.model)
                model_admin = admin_api.get_model_admin(model_name=fk_obj._meta.model_name)
                o_widget = field_translate.field_2_list_widget(self.request, model_admin, field2, fk_obj)
            else:
                o_widget = ""

        else:
            is_edit = field_name in self.config.lst_editable and \
                      self.model_admin.has_change_permission(self.request, obj)

            if is_edit:
                o_widget = field_translate.field_2_widget(self.request, self.model_admin,
                                                          field_name, obj, is_edit=is_edit, is_list=True)
            # elif self.is_child:
            #     o_widget = field_translate.field_2_widget(self.request, self.model_admin,
            #                                               field_name, obj)
            #     o_widget.readonly = True
            else:
                o_widget = field_translate.field_2_list_widget(self.request, self.model_admin, field_name, obj)

        if isinstance(o_widget, widgets.Text):
            o_widget.set("line_number", 2)  # 显示2行

        elif isinstance(o_widget, str):
            o_widget = widgets.Text(text=o_widget, line_number=2)

        return o_widget

    def make_row_delete(self, obj):
        app_label = self.app_label
        model_name = self.model_name
        if self.display_mode:
            text = "确定删除 %s?" % obj
            url = const.URL_LIST_DELETE_CLOSE % (self.app_label, self.model_name)
            url = common.make_url(url, self.request, param={
                const.UPN_DISPLAY_MODE: const.DM_LIST_CHILD,
                const.UPN_RELATED_ID: self.related_object_id,
                const.UPN_RELATED_FIELD: self.related_field_name,
                const.UPN_RELATED_APP: self.related_app_label,
                const.UPN_RELATED_MODEL: self.related_model_name,
                "id": obj.pk
            })
            o_step2 = step.Post(url=url)
            o_step = step_ex.MsgBox(text=text, step=o_step2)

        else:
            url = common.make_url(const.URL_FORM_DEL_VIEW % (app_label, model_name, obj.pk), self.request)
            o_step = step.Post(url=url, jump=True, submit_type="no")
        hover = {"font_color": common.calc_hover_color(self.o_theme.theme_color)}
        o_icon = widgets.Icon(icon="el-icon-delete", hover=hover, step=o_step, margin=[0, 5, 0, 5], tooltip="行删除")
        return o_icon

    def make_row_save(self, obj):
        app_label = self.app_label
        model_name = self.model_name
        url = const.URL_LIST_ROW_SAVE % (app_label, model_name)
        table_name = const.WN_TABLE % (app_label, model_name)
        data = {"url": url, "row_id": obj.pk}
        # o_step = step.WidgetOpera(name=table_name, opera=const.TABLE_ROW_SAVE, data={"id": obj.pk}, url=url)
        o_step = step.WidgetOpera(name=table_name, opera=const.OPERA_TABLE_ROW_SAVE, data=data)
        o_icon = widgets.Icon(icon="v-save", size=16, step=o_step, margin=[0, 5, 0, 5], tooltip="行保存")
        return o_icon

    def make_row_edit(self, obj, filter_name):
        # if self.display_mode == const.DM_LIST_CHILD:
        if self.display_mode:
            url = const.URL_FORM_CHILD_POPUP % (self.app_label, self.model_name)
            url = common.make_url(url, self.request, param={
                const.UPN_DISPLAY_MODE: const.DM_FORM_POPUP,
                const.UPN_RELATED_ID: self.related_object_id,
                const.UPN_RELATED_FIELD: self.related_field_name,
                const.UPN_RELATED_APP: self.related_app_label,
                const.UPN_RELATED_MODEL: self.related_model_name,
                "id": obj.pk
            })
            o_step = step.Get(url=url, splice=filter_name)
            o_icon = widgets.Icon(icon="el-icon-edit", size=14, step=o_step, margin=[0, 5, 0, 5], tooltip="行编辑")
        else:
            url = self.model_admin.get_change_form_url(self.request, obj)
            url = common.make_url(url, self.request)
            if self.display_mode:
                o_step = step.Post(url=url, splice=filter_name)
            else:
                o_step = step.Post(url=url, jump=True, splice=filter_name)
            o_icon = widgets.Icon(icon="el-icon-edit", size=14, step=o_step, margin=[0, 5, 0, 5], tooltip="行编辑")
        return o_icon

    def make_row_opera(self, obj):
        """构造行操作组件"""
        lst_opera_widget = []
        # 删除
        row_opera = self.config.row_opera
        if row_opera:
            if self.model_admin.has_delete_permission(self.request, obj):
                if self.display_mode == const.DM_LIST_CHILD:
                    o_icon_del = self.model_admin.make_inline_delete(self.request, obj)
                else:
                    o_icon_del = self.model_admin.make_list_row_delete(self.request, obj)

                if o_icon_del == const.USE_TEMPLATE:
                    o_icon_del = self.make_row_delete(obj)

                if o_icon_del:
                    lst_opera_widget.append(o_icon_del)

            # 编辑
            # if self.config.lst_display_links and self.model_admin.has_change_permission(self.request, obj):
            filter_name = copy.copy(self.filter_name)
            o_icon_edit = self.model_admin.make_list_row_edit(self.request, obj, filter_name)
            if o_icon_edit == const.USE_TEMPLATE:
                o_icon_edit = self.make_row_edit(obj, filter_name)

            if o_icon_edit:
                lst_opera_widget.append(o_icon_edit)

            # 保存
            if self.config.lst_editable and \
                    self.model_admin.has_change_permission(self.request, obj):
                o_icon_save = self.model_admin.make_list_row_save(self.request, obj)
                if o_icon_save == const.USE_TEMPLATE:
                    o_icon_save = self.make_row_save(obj)

                if o_icon_save:
                    lst_opera_widget.append(o_icon_save)

            # 新增加的行操作按钮
            lst_opera = self.model_admin.get_row_opera_custom(self.request, obj)
            if isinstance(lst_opera, (tuple, list)):
                lst_opera_widget.extend(lst_opera)
            elif lst_opera is not None:
                lst_opera_widget.append(lst_opera)

        return lst_opera_widget

    def make_list_row(self, obj):
        """构造一行数据"""
        row_data = []
        order = self.config.table_order

        for field_name in self.lst_display:
            if order and field_name == "order":
                continue

            o_widget = self.make_row_field(field_name, obj)
            fun = getattr(self.model_admin, field_name, None) or \
                  getattr(self.model_admin, "list_v_%s" % field_name, None)

            if callable(fun) and getattr(fun, "multiple_col", False):
                row_data.extend(o_widget)
            else:
                row_data.append(o_widget)

        if self.config.row_opera and self.display_mode != const.DM_LIST_SELECT:
            row_data.append(self.make_row_opera(obj))

        return row_data

    def make_list_table(self, queryset, call_model_admin=True):
        if call_model_admin:
            o_table = self.model_admin.make_list_table(self.request, self, queryset)
        else:
            o_table = None

        if not o_table:
            change_list_config = self.model_admin.get_change_list_config(self.request)
            if change_list_config.get("tree_table", False):
                o_table = self.make_list_tree_table(queryset, change_list_config.get("tree_level", None))
                return o_table

        total, page_total, begin, end = \
            admin_api.get_queryset_total(self.request, self.model_admin, queryset, self.page_index)
        data = []
        row_id = []
        for obj in queryset[begin: end]:
            row_data = self.make_list_row(obj)
            data.append(row_data)
            row_id.append(getattr(obj, self.row_id_field))

        order_url = None
        table_config = self.config.table_config
        order = table_config.get("order", None)
        if order:  # 物理拖动排序
            order_url = const.URL_LIST_ORDER % (self.app_label, self.model_name)

        head_data, col_width, sort, col_horizontal = self.make_head()
        if self.config.row_opera and (self.display_mode != const.DM_LIST_SELECT) and col_width:
            key = list(col_width.keys())[-1]
            col_width[key] = admin_api.get_opera_col_width(data)

        col_fixed = table_config.get("col_fixed", {})

        # 最后操作列要固定
        if ("right" not in col_fixed) and self.config.row_opera:
            col_fixed["right"] = -1

        head = {"fixed": True, "data": head_data, "show": True, "sort": sort or None,
                "row_border": {"color": "#EBEEF5"}, }
        row = {"id": row_id, "zebra": self.o_theme.table.get("zebra", None), "min_height": 60}
        col = {"width": col_width, "fixed": col_fixed, "horizontal": col_horizontal}
        name = const.WN_TABLE % (self.app_label, self.model_name)
        # event = {"select_all": step.WidgetUpdate(data={"name": const.WN_SELECT_ALL,
        #                                                "value": "{{js.getCurrentAttrValue('select_all_value')}}"})}
        # height = "100vh-%s-%s" % (self.HEIGHT_TOP + self.MARGIN_TOP +
        #                           self.HEIGHT_TITLE + self.HEIGHT_BOTTOM + self.MARGIN_BOTTOM,
        #                           const.WN_CONTENT_FILTER)
        o_table = widgets.Table(name=name, head=head, row=row, col=col,
                                data=data,
                                order_url=order_url,
                                width="100%",
                                height="100%",
                                select="multiple",
                                bg={"color": self.o_theme.right_bg_color},
                                focus={"color": self.o_theme.table.get("focus", {}).get("color", None)},
                                space_left=10, space_right=10,
                                # row_border={"color": "#EBEEF5"},
                                # col_border={"color": "#EBEEF5"},
                                # event=event
                                border={"color": self.o_theme.bg_color, "width": [1, 0, 1, 0]}
                                )
        return o_table

    def make_list_tree_table(self, queryset, tree_level=None):
        change_list_config = self.model_admin.get_change_list_config(self.request)
        parent_field = change_list_config.get("parent_field", "parent_id")
        foreign_key_field = change_list_config.get("foreign_key_field", "pk")

        def deep(o, lst_item, level):
            level += 1
            sub_filter = {parent_field: getattr(o, foreign_key_field)}
            for sub_obj in self.model_admin.model.objects.filter(**sub_filter):
                sub_children = []
                sub_row_data = self.make_list_row(sub_obj)
                if tree_level > level:
                    deep(sub_obj, sub_children, level)
                    sub_item = {"id": sub_obj.pk, "row": sub_row_data, "children": sub_children}
                else:
                    sub_filter2 = {parent_field: getattr(sub_obj, foreign_key_field)}
                    if self.model_admin.model.objects.filter(**sub_filter2).exists():
                        sub_item = {"id": sub_obj.pk, "row": sub_row_data}
                    else:
                        sub_item = {"id": sub_obj.pk, "row": sub_row_data, "children": []}

                lst_item.append(sub_item)

        data = []
        if "parent_value" in change_list_config:
            dict_filter = {parent_field: change_list_config["parent_value"]}
        else:
            dict_filter = {"%s__isnull" % parent_field: True}

        queryset = queryset.filter(**dict_filter)
        total, page_total, begin, end = \
            admin_api.get_queryset_total(self.request, self.model_admin, queryset, self.page_index)

        if tree_level is None:
            tree_level = 9999999
            lazy_load_url = ""
        else:
            lazy_load_url = const.URL_LIST_TREE_LOAD % (self.app_label, self.model_name, parent_field)

        for obj in queryset[begin:end]:
            level = 1
            row_data = self.make_list_row(obj)
            children = []
            if tree_level > level:
                deep(obj, children, level)
                item = {"id": obj.pk, "row": row_data, "children": children, "expand": True}
            else:
                sub_filter = {parent_field: getattr(obj, foreign_key_field)}
                if self.model_admin.model.objects.filter(**sub_filter).exists():
                    item = {"id": obj.pk, "row": row_data}
                else:
                    item = {"id": obj.pk, "row": row_data, "children": []}

            data.append(item)

        table_config = self.config.table_config
        col_fixed = table_config.get("col_fixed", {})

        head_data, col_width, sort, col_horizontal = self.make_head()
        # 最后操作列要固定
        if self.config.row_opera:
            if "right" not in col_fixed:
                col_fixed["right"] = -1

            # key = list(col_width.keys())[-1]
            # col_width[key] = admin_api.get_opera_col_width(data)
        col = {"width": col_width, "fixed": col_fixed, "horizontal": col_horizontal}

        name = const.WN_TABLE % (self.app_label, self.model_name)
        o_table = widgets.Table(name=name, head={"fixed": True, "data": head_data},
                                width="100%", data=data, tree=True, col=col,
                                row={"height": 60, "border": {"color": "#EBEEF5"},
                                     "zebra": self.o_theme.table.get("zebra", None)},
                                focus={"color": self.o_theme.table.get("focus", {}).get("color", None)},
                                lazy_load_url=lazy_load_url,
                                )
        if change_list_config.get("order", False):
            o_table.order_url = const.URL_LIST_ORDER % (self.app_label, self.model_name)

        return o_table

    def make_list_pagination(self, queryset):
        """构造分页"""
        lst_widget = []
        page_size = int(self.request.GET.get(const.UPN_PAGE_SIZE, self.model_admin.get_list_per_page(self.request)))
        total, page_count, begin, end = \
            admin_api.get_queryset_total(self.request, self.model_admin, queryset, self.page_index, page_size=page_size)

        if self.display_mode:
            page_sizes = []
        else:
            page_sizes = None

        # if page_count > 1:
        p_name = const.WN_PAGINATION % self.model_name
        self.filter_name.append(p_name)
        if self.display_mode:
            url = const.URL_LIST_FILTER % (self.app_label, self.model_name)

            dict_para = {
                const.UPN_RELATED_APP: self.related_app_label,
                const.UPN_RELATED_MODEL: self.related_model_name,
                const.UPN_RELATED_FIELD: self.related_field_name,
                const.UPN_RELATED_ID: self.related_object_id,
                const.UPN_DISPLAY_MODE: self.display_mode
            }
            url = common.make_url(url, self.request, param=dict_para)
            o_step = step.Post(url=url, splice=self.filter_name)
            o_pagination = widgets.Pagination(name=p_name, step=o_step,
                                              page_count=page_count, value=self.page_index,
                                              page_sizes=page_sizes, page_size=page_size, padding_right=10,
                                              position="right")
        else:
            url = common.make_url(self.config.change_list_url, self.request)
            o_step = step.Post(url=url, jump=True, splice=self.filter_name)

            o_pagination = widgets.Pagination(name=p_name, step=o_step,
                                              page_count=page_count, value=self.page_index,
                                              page_sizes=page_sizes, page_size=page_size, position="right")
        lst_widget.append(o_pagination)

        if total > 0:
            text = "%s - %s / 总%s条" % (begin + 1, end, total)
            name = const.WN_COUNT_TEXT % self.model_name
            o_widget = widgets.Text(name=name, text=text, margin_right=10, position="right")
            lst_widget.append(o_widget)

        return lst_widget


class ChangeForm(Style):
    def __init__(self, request, model_admin, o_theme, obj=None, is_copy=False):
        Style.__init__(self)
        self.request = request
        self.model_admin = model_admin
        self.o_theme = o_theme
        if obj:
            self.obj = obj
            self.change = True
        else:
            self.obj = model_admin.get_default_object(request)
            self.obj.pk = None
            self.change = False

        self.show_mode = request.GET.get(const.UPN_SHOW_MODE, None)

        self.app_label = model_admin.opts.app_label
        self.model_name = model_admin.opts.model_name

        self.is_edit = True  # 表单是否可以编辑 （页面总开关）
        self.is_copy = is_copy  # 是否为拷贝
        self.is_inline = True  # 是否构造子表
        self.steps_idx = request.GET.get(const.UPN_STEPS_IDX, None)  # 步骤索引
        if self.steps_idx:
            self.steps_idx = int(self.steps_idx)
        self.steps_num = None

        # 字段显示文字
        self.readonly = model_admin.has_readonly_text(self.request, obj)
        self.fk_field_name = None  # 外键名称
        # 必填字段
        self.required_fields = model_admin.get_required_fields(self.request, obj) or []
        # 只读字段
        self.readonly_fields = list(model_admin.get_readonly_fields(self.request, obj) or [])

        self.display_mode = request.GET.get(const.UPN_DISPLAY_MODE,
                                            None)  # 弹出类型 "link":链接修改（关闭后要更新字段显示值） "child":子表弹出(关闭后要跟新列表）
        self.related_field_name = request.GET.get(const.UPN_RELATED_FIELD, None)  # 关联的字段名称（此表作为外键子表）
        self.related_object_id = request.GET.get(const.UPN_RELATED_ID, None)  # 关联的对象ID
        self.related_app_label = request.GET.get(const.UPN_RELATED_APP, None)
        self.related_model_name = request.GET.get(const.UPN_RELATED_MODEL, None)

    def make_form_view(self, is_save=True):
        """构造表单页面"""
        related_field = self.request.GET.get(const.UPN_RELATED_FIELD, None)
        related_id = self.request.GET.get(const.UPN_RELATED_ID, None)
        if related_field and self.display_mode:  # 子表关联的字段默认显示，且无法修改
            self.readonly_fields.append(related_field)
            try:
                db_field = admin_api.get_field(self.model_admin, related_field)
                setattr(self.obj, db_field.get_attname(), related_id)
            except (BaseException,):
                pass

        o_grid = widgets.Grid(name=const.WN_CONTENT_RIGHT,
                              col_num=2, padding=self.MARGIN,
                              scroll={"y": "auto"},
                              # width="100%%-%s" % (self.MARGIN_LEFT + self.MARGIN_RIGHT),
                              height="100vh-%s" % self.HEIGHT_TOP,
                              # height="100%",
                              vertical="top")

        if self.request.GET.get(const.UPN_DISPLAY_MODE, None) == const.DM_FORM_POPUP:
            o_grid.set("height", "90vh")

        if not self.model_admin.has_change_form_opera(self.request):
            is_save = False

        if is_save:
            o_grid.set_col_attr(col=1, width=200, horizontal="center")
        else:
            o_grid.set_col_attr(col=1, width=0)

        # 标题
        o_title = self.make_title()
        o_grid.add_widget(o_title, col=0)

        # 字段
        o_grid_field = self.make_form_field(self.model_admin, self.obj)
        o_grid.add_widget(o_grid_field, col=0)

        # 操作按钮
        if is_save:
            if self.is_copy:  # 在copy情况下，要读取obj数据，在保存和删除情况下不使用
                o_panel_save = self.make_opera_area()
            else:
                o_panel_save = self.make_opera_area(self.change and self.obj or None)

            o_grid.add_widget(o_panel_save)

        return o_grid

    def make_title(self, title=None):
        o_title = self.model_admin.make_form_title(self.request, self, self.obj)
        if o_title is None:
            o_title = widgets.Panel(width="100%", height=self.HEIGHT_TITLE,
                                    bg_image=settings.STATIC_URL + self.o_theme.title_image)

            # 等于菜单名称或verbose_name
            if title is None:
                menu_id = self.request.GET.get(const.UPN_MENU_ID, None)
                if menu_id:
                    title = menu.get_label(menu_id)

                if not title:
                    title = str(self.model_admin.opts.verbose_name)

            if self.display_mode or self.steps_idx is not None:
                o_text = widgets.Text(text=title,
                                      font={"color": "#FFFFFF", "size": self.o_theme.font["size"] + 4},
                                      padding_left=10)
                o_title.add_widget(o_text)
            else:
                # o_step = step.ViewOpera(back=1)
                url = common.make_url(self.model_admin.get_change_list_url(self.request, obj=self.obj),
                                      self.request, filter=["id", const.UPN_STEPS_IDX])
                o_step = step.Post(url=url, jump=True, submit_type="hide")
                prefix = widgets.Icon(icon="el-icon-back")
                o_button = widgets.Button(prefix=prefix,
                                          text=title,
                                          font={"color": "#FFFFFF", "size": self.o_theme.font["size"] + 4},
                                          border_color="transparent",
                                          bg_color="transparent",
                                          hover={"bg_color": "transparent", "font_color": "#FFFFFF"},
                                          step=o_step)
                o_title.add_widget(o_button)
        return o_title

    def make_form_field(self, model_admin, obj=None, is_inline=False):
        if model_admin.get_steps(self.request, obj):
            steps = model_admin.get_steps(self.request, obj)
            if self.steps_idx in [None, ""]:
                self.steps_idx = 0

            self.steps_num = len(steps)
            if self.steps_num > self.steps_idx:
                fieldsets = steps[self.steps_idx]["fieldsets"]
            else:
                fieldsets = steps[-1]["fieldsets"]
                self.steps_idx = self.steps_num - 1

            o_widget = self.make_fieldsets(model_admin, obj, fieldsets)

        elif model_admin.get_tabs(self.request, obj):
            tabs = model_admin.get_tabs(self.request, obj)
            tab_data = list()
            for i, dict_tab in enumerate(tabs):
                fieldsets = dict_tab["fieldsets"]
                lst_widget = self.make_fieldsets(model_admin, obj, fieldsets)
                o_grid_sub = widgets.Grid()
                o_grid_sub.add_widget(lst_widget)
                tab_data.append({"label": dict_tab["label"], "icon": dict_tab.get("icon", ""),
                                 "content": o_grid_sub, "id": i})

            # app_label = model_admin.opts.app_label
            model_name = model_admin.opts.model_name
            tabs_name = const.WN_FORM_TABS % model_name
            tabs_value = int(self.request.GET.get(tabs_name, 0))
            tabs_config = model_admin.get_tabs_config(self.request, obj)
            o_widget = widgets.Tabs(name=tabs_name, data=tab_data, value=tabs_value, width="100%",
                                    bg={"color": self.o_theme.right_bg_color},
                                    event={"change": step.Get(splice=tabs_name, submit_type="update_url")},
                                    **tabs_config)

        elif model_admin.get_collapses(self.request, obj):
            collapses = model_admin.get_collapses(self.request, obj)
            collapse_data = list()
            for i, dict_collapse in enumerate(collapses):
                fieldsets = dict_collapse["fieldsets"]
                lst_widget = self.make_fieldsets(model_admin, obj, fieldsets)
                if i == 0:
                    expand = True
                else:
                    expand = False

                if obj and obj.pk:
                    label = dict_collapse.get("label", str(obj))
                else:
                    label = "新建"
                collapse_data.append({"label": label,
                                      "content": lst_widget, "expand": expand})

            color = common.calc_focus_color(self.o_theme.right_bg_color)
            o_widget = widgets.Collapse(data=collapse_data, width="100%",
                                        border={"color": color, "width": "0,0,1,0"})

        else:
            if is_inline:
                fieldsets = self.model_admin.get_inline_fieldsets(self.request, model_admin, obj)
            else:
                fieldsets = model_admin.get_fieldsets(self.request, obj)  # 获取字段布局
            o_widget = self.make_fieldsets(model_admin, obj, fieldsets)

        return o_widget

    def make_fieldsets(self, model_admin, obj, fieldsets):
        lst_widget = []
        max_num = admin_api.calc_row_max_field_num(self.request, self.model_admin, obj, fieldsets)
        fieldset_num = len(fieldsets)
        for i, fieldset in enumerate(fieldsets):
            o_panel = self.make_fieldset(fieldset, model_admin, obj, max_num)
            app_label = model_admin.model._meta.app_label
            model_name = model_admin.model._meta.model_name
            o_panel.name = const.WN_FIELDSET % (app_label, model_name, i)
            lst_widget.append(o_panel)
            if i < (fieldset_num - 1):  # 最后一个不增加
                lst_widget.append(widgets.Row(height=10))

        return lst_widget

    def make_fieldset(self, fieldset, model_admin, obj, max_num=1):
        name, dict_field = fieldset
        exclude_fields = model_admin.get_exclude(self.request, obj) or []

        flag_title = False
        o_panel = widgets.Panel(background_color=self.o_theme.right_bg_color)
        merged_cells = []
        data = []
        row_idx = 0

        for key, lst_field in dict_field.items():
            if key == "classes":
                continue

            for field in lst_field:
                lst_row = [None] * (max_num * 2)
                if isinstance(field, (tuple, list)):  # 多个(不支持inline)
                    lst_sub_field = []
                    for (i, field_name) in enumerate(field):
                        if field_name in exclude_fields:
                            continue

                        if hasattr(field_name, "model"):
                            continue

                        if (field_name == self.fk_field_name) or \
                                ("%s_id" % field_name == self.fk_field_name):
                            continue

                        lst_sub_field.append(field_name)

                    field_num = len(lst_sub_field)
                    if field_num == 1:
                        field_name = lst_sub_field[0]
                        lst_row, merged_cell = self.make_row(model_admin, field_name, obj, row_idx, max_num)
                        merged_cells.extend(merged_cell)
                        flag_title = True

                    else:
                        for (i, field_name) in enumerate(lst_sub_field):
                            # 一行多列不支持inline
                            lst_widget1, lst_widget2 = \
                                field_translate.make_field_widget(self.request, obj,
                                                                  model_admin, field_name,
                                                                  self.required_fields, self.readonly_fields,
                                                                  readonly=self.readonly,
                                                                  is_popup=bool(self.display_mode))

                            if (not lst_widget1) and (not lst_widget2):
                                continue

                            if (not lst_widget1) or (not lst_widget2):
                                merged_cells.append("%s-%s:%s-%s" % (row_idx, i, row_idx, i))

                            flag_title = True
                            lst_row[i * 2] = lst_widget1
                            lst_row[i * 2 + 1] = lst_widget2

                            if i >= 2:  # 最大3
                                continue

                else:
                    if (field == self.fk_field_name) or ("%s_id" % str(field) == self.fk_field_name):
                        continue

                    lst_row, merged_cell = self.make_row(model_admin, field, obj, row_idx, max_num)
                    merged_cells.extend(merged_cell)
                    flag_title = True

                row_idx += 1
                data.append(lst_row)

        col_horizontal = {}
        col_width = {}
        for i in range(max_num):
            col_horizontal[i * 2] = "right"
            col_horizontal[i * 2 + 1] = "left"

        if max_num == 1:
            col_width[0] = "20%"
            col_width[1] = "80%"

        elif max_num == 2:
            col_width[0] = "16%"
            col_width[1] = "34%"
            col_width[2] = "16%"
            col_width[3] = "34%"

        elif max_num == 3:
            col_width[0] = "12%"
            col_width[1] = "22%"
            col_width[2] = "11%"
            col_width[3] = "22%"
            col_width[4] = "11%"
            col_width[5] = "22%"

        o_lite_table = widgets.LiteTable(data=data,
                                         col_horizontal=col_horizontal, col_width=col_width,
                                         merged_cells=merged_cells,
                                         space_top=10, space_bottom=10)
        o_panel.append(o_lite_table)

        if flag_title and (name is not None):  # 如果有子项，才显示标题
            o_text = widgets.Text(text=str(name),
                                  font={"weight": "bold", "size": self.o_theme.font["size"] + 1},
                                  margin=[5, 5, 5, 5])
            o_panel.insert_widget(0, o_text)

        return o_panel

    def make_row(self, model_admin, field_name, obj, row_idx, max_num):
        lst_row = [None] * (max_num * 2)
        merged_cells = []
        if not isinstance(field_name, str):
            o_widget = self.make_inline(field_name)
            lst_row[0] = o_widget
            # 子表，合并成一行
            merged_cells.append("%s-0:%s-%s" % (row_idx, row_idx, max_num * 2 - 1))
        else:
            lst_widget1, lst_widget2 = field_translate.make_field_widget(self.request, obj,
                                                                         model_admin, field_name,
                                                                         self.required_fields, self.readonly_fields,
                                                                         readonly=self.readonly,
                                                                         is_popup=bool(self.display_mode))
            lst_row[0] = lst_widget1
            lst_row[1] = lst_widget2
            # if max_num > 1:
            if not lst_widget1 or not lst_widget2:  # 都为空，合并成一行
                merged_cells.append("%s-0:%s-%s" % (row_idx, row_idx, max_num * 2 - 1))
            else:
                merged_cells.append("%s-1:%s-%s" % (row_idx, row_idx, max_num * 2 - 1))

        return lst_row, merged_cells

    def make_opera_area(self, obj=None):
        """构造保存区域按钮"""
        button_width = 170
        object_id = obj.pk if obj and obj.pk else None
        if self.show_mode:
            o_panel = widgets.Panel(width=190, horizontal="center", vertical="top")
        else:
            o_panel = widgets.Panel(width=190, horizontal="center", vertical="top")

        if self.display_mode == const.DM_FORM_POPUP:
            url = const.URL_FORM_SAVE_CLOSE % (self.app_label, self.model_name)
            url = common.make_url(url,
                                  param={const.UPN_DISPLAY_MODE: const.DM_FORM_POPUP,
                                         const.UPN_RELATED_APP: self.related_app_label,
                                         const.UPN_RELATED_MODEL: self.related_model_name,
                                         const.UPN_RELATED_FIELD: self.related_field_name,
                                         const.UPN_RELATED_ID: self.related_object_id,
                                         "id": object_id})

            o_button = self.model_admin.make_form_save_close(self.request, self, obj)
            if o_button == const.USE_TEMPLATE:  # 使用模板
                o_step = step.Post(url=url, submit_type="layer", check_required=True)
                o_button = widgets.Button(text="保存并关闭", step=o_step, width=button_width)

            if o_button:
                o_button.width = button_width
                o_panel.add_widget(o_button)
                o_panel.add_widget(widgets.Row(height=10))

            # 增加保存编辑按钮
            o_button = self.model_admin.make_form_save_edit(self.request, self, obj)
            if o_button == const.USE_TEMPLATE:  # 使用模板
                url = const.URL_FORM_SAVE_EDIT % (self.app_label, self.model_name)
                url = common.make_url(url, self.request, param={"id": object_id})
                o_step = step.Post(url=url, submit_type="layer", check_required=True)
                o_button = widgets.Button(text="保存并继续编辑", step=o_step, width=button_width)

            if o_button:
                o_button.width = button_width
                o_panel.add_widget(o_button)
                o_panel.add_widget(widgets.Row(height=10))

            o_button = widgets.Button(text="关闭", step=step.LayerClose(), width=button_width)
            o_panel.add_widget(o_button)

        elif self.display_mode == const.DM_FORM_LINK:
            if self.related_model_name:
                url = const.URL_FORM_SAVE_CLOSE % (self.app_label, self.model_name)
                url = common.make_url(url, self.request,
                                      param={const.UPN_RELATED_APP: self.related_app_label,
                                             const.UPN_RELATED_MODEL: self.related_model_name,
                                             const.UPN_RELATED_FIELD: self.related_field_name,
                                             const.UPN_RELATED_ID: self.related_object_id,
                                             "id": object_id,
                                             const.UPN_DISPLAY_MODE: const.DM_FORM_LINK,
                                             })

                o_button = self.model_admin.make_form_save_close(self.request, self, obj)
                if o_button == const.USE_TEMPLATE:  # 使用模板
                    o_step = step.Post(url=url, submit_type="layer", check_required=True)
                    o_button = widgets.Button(text="保存并关闭", step=o_step, width=button_width)

                if o_button:
                    o_button.width = button_width
                    o_panel.add_widget(o_button)
                    o_panel.add_widget(widgets.Row(height=10))

            o_button = widgets.Button(text="关闭", step=step.LayerClose(), width=button_width)
            o_panel.add_widget(o_button)

        else:
            o_panel.set_attr_value("float", {"right": 0, "top": self.HEIGHT_TOP + self.MARGIN_TOP})
            # 自定义
            lst_button_form = self.model_admin.get_change_form_custom(self.request, obj)
            if not isinstance(lst_button_form, (tuple, list)):
                lst_button_form = [lst_button_form, ]

            for o_button in lst_button_form or []:
                if o_button is None:
                    continue
                # o_step = step.Post(url=dict_button.get("url", ""), submit_type="hide", jump=dict_button.get("jump", False))
                # o_button = widgets.Button(text=_(dict_button.get("text", "")), step=o_step, width=button_width)
                # o_button.background_color = random.choice(const.COLOR_RANDOM)
                o_button.border_color = None
                # o_button.focus_color = theme.calc_gradient_color(o_button.background_color)
                o_button.width = button_width
                o_panel.add_widget(o_button)
                o_panel.add_widget(widgets.Row(height=10))

            if self.model_admin.has_change_permission(self.request, obj):
                if self.steps_idx is not None:
                    if self.steps_num >= (self.steps_idx + 1):
                        o_button = self.model_admin.make_form_next(self.request, self, obj)
                        if o_button == const.USE_TEMPLATE:  # 使用模板
                            o_button = self.make_form_next(obj)

                        if o_button:
                            o_button.width = button_width
                            o_button.border_color = None
                            o_panel.add_widget(o_button)
                            o_panel.add_widget(widgets.Row(height=10))

                            if self.steps_num == (self.steps_idx + 1):
                                o_button.text = "提交"

                    if self.steps_idx > 0:
                        o_button = self.model_admin.make_form_prev(self.request, self, obj)
                        if o_button == const.USE_TEMPLATE:  # 使用模板
                            o_button = self.make_form_prev(obj)

                        if o_button:
                            o_button.width = button_width
                            o_button.border_color = None
                            o_panel.add_widget(o_button)
                            o_panel.add_widget(widgets.Row(height=10))

                else:
                    # 先在admin
                    o_button = self.model_admin.make_form_save(self.request, self, obj)
                    if o_button == const.USE_TEMPLATE:  # 使用模板
                        o_button = self.make_form_save(obj)

                    if o_button:
                        o_button.width = button_width
                        o_button.border_color = None
                        o_panel.add_widget(o_button)
                        o_panel.add_widget(widgets.Row(height=10))

                    o_button = self.model_admin.make_form_save_edit(self.request, self, obj)
                    if o_button == const.USE_TEMPLATE:
                        o_button = self.make_form_save_edit(obj)

                    if o_button:
                        o_button.width = button_width
                        # o_button.border_color = None
                        o_panel.add_widget(o_button)
                        o_panel.add_widget(widgets.Row(height=10))

            if (not self.show_mode) and self.model_admin.has_add_permission(self.request):
                o_button = self.model_admin.make_form_save_add(self.request, self, obj)
                if o_button == const.USE_TEMPLATE:
                    o_button = self.make_form_save_add(obj)

                if o_button:
                    o_button.width = button_width
                    o_panel.add_widget(o_button)
                    o_panel.add_widget(widgets.Row(height=10))

                    # if not self.model_admin.inlines:
                    # 自定义的增加界面不能使用"保存并复制增加另一个"
                    # v_change_form_add = self.model_admin.get_v_change_form_add(self.request)
                    # if v_change_form_add.find(const.CHANGE_FORM_ADD % (self.app_label, self.model_name)) != -1:
                    #     o_button = self.model_admin.make_change_form_save_copy_add_button(self.request, obj)
                    #     if o_button:
                    #         o_button.width = button_width
                    #         o_panel.add_widget(o_button)
                    #         o_panel.add_widget(widgets.Row(height=10))

            if (obj is not None) and self.model_admin.has_delete_permission(self.request, obj):
                if (get_user_model() == self.model_admin.model) and (obj.pk == self.request.user.pk):  # 等于自已不能删除
                    pass
                else:
                    o_button = self.model_admin.make_form_delete(self.request, self, obj)
                    if o_button == const.USE_TEMPLATE:
                        o_button = self.make_form_delete(obj)

                    if o_button:
                        o_button.width = button_width
                        o_panel.add_widget(o_button)
                        o_panel.add_widget(widgets.Row(height=10))

            o_button = self.model_admin.make_form_close(self.request, self)
            if o_button == const.USE_TEMPLATE:
                o_button = self.make_form_close()

            if o_button:
                o_button.width = button_width
                o_panel.add_widget(o_button)
                o_panel.add_widget(widgets.Row(height=10))

        return o_panel

    def make_form_next(self, obj=None):
        """表单页面下一步按钮"""
        if obj and obj.pk:
            url = common.make_url(const.URL_FORM_SAVE % (self.app_label, self.model_name) +
                                  ("?id=%s" % obj.pk), self.request,
                                  param={const.UPN_STEPS_IDX: self.steps_idx + 1})
        else:
            url = common.make_url(const.URL_FORM_SAVE % (self.app_label, self.model_name), self.request,
                                  param={const.UPN_STEPS_IDX: self.steps_idx + 1})
        o_step = step.Post(url=url, check_required=True)
        o_button = widgets.Button(text="下一步", step=o_step)
        return o_button

    def make_form_prev(self, obj=None):
        """表单页面上一步按钮"""
        steps_idx = self.steps_idx - 1
        # if steps_idx == 0:
        #     steps_idx = None

        url = self.model_admin.get_change_form_url(self.request, obj)
        if steps_idx is not None:
            url = common.make_url(url, self.request,
                                  filter=[const.UPN_TOP_ID, const.UPN_SCREEN_WIDTH, const.UPN_SCREEN_HEIGHT],
                                  param={const.UPN_STEPS_IDX: steps_idx})
        else:
            url = common.make_url(url, self.request,
                                  filter=[const.UPN_TOP_ID, const.UPN_SCREEN_WIDTH, const.UPN_SCREEN_HEIGHT,
                                          const.UPN_STEPS_IDX])

        o_step = step.Post(url=url, jump=True)
        o_button = widgets.Button(text="上一步", step=o_step)
        return o_button

    def make_form_save(self, obj=None):
        """保存按钮"""
        if obj and obj.pk:
            url = common.make_url(const.URL_FORM_SAVE % (self.app_label, self.model_name), self.request,
                                  {"id": obj.pk, const.UPN_SCREEN_WIDTH: "{{window.innerWidth}}"})
        else:
            url = common.make_url(const.URL_FORM_SAVE % (self.app_label, self.model_name), self.request,
                                  {const.UPN_SCREEN_WIDTH: "{{window.innerWidth}}"})
        o_step = step.Post(url=url, check_required=True)
        o_button = widgets.Button(text="保存并关闭", step=o_step)
        return o_button

    def make_form_save_edit(self, obj=None):
        """保存编辑按钮"""
        app_label = self.app_label
        model_name = self.model_name
        if obj and obj.pk:
            url = common.make_url(const.URL_FORM_SAVE_EDIT % (app_label, model_name) + ("?id=%s" % obj.pk),
                                  self.request)
        else:
            url = common.make_url(const.URL_FORM_SAVE_EDIT % (app_label, model_name), self.request)

        tabs = self.model_admin.get_tabs(self.request, obj)
        if tabs:
            lst_widget_name = const.WN_FORM_TABS % model_name
        else:
            lst_widget_name = []

        o_step = step.Post(url=url, splice=lst_widget_name, check_required=True)
        o_button = widgets.Button(text=_("Save and continue editing"), step=o_step)
        return o_button

    def make_form_save_add(self, obj=None):
        """保存增加按钮"""
        app_label = self.app_label
        model_name = self.model_name
        if obj and obj.pk:
            object_id = obj.pk
        else:
            object_id = ""
        url = common.make_url(const.URL_FORM_SAVE_ADD % (app_label, model_name, object_id), self.request)
        o_step = step.Post(url=url, check_required=True)
        o_button = widgets.Button(text=_("Save and add another"), step=o_step)
        return o_button

    def make_form_save_close(self, obj=None):
        """保存并关闭按钮"""
        app_label = self.app_label
        model_name = self.model_name
        if obj and obj.pk:
            object_id = obj.pk
        else:
            object_id = ""

        url = common.make_url(const.URL_FORM_SAVE_CLOSE % (app_label, model_name),
                              self.request, param={"id": object_id})
        o_step = step.Post(url=url, check_required=True)
        o_button = widgets.Button(text=_("Save"), step=o_step)
        return o_button

    def make_form_delete(self, obj=None):
        """删除按钮"""
        app_label = self.app_label
        model_name = self.model_name
        if obj and obj.pk:
            object_id = obj.pk
        else:
            object_id = ""
        url = common.make_url(const.URL_FORM_DEL_VIEW % (app_label, model_name, object_id), self.request)
        url = common.make_url(url, self.request, filter=[const.UPN_STEPS_IDX])
        o_button = widgets.Button(text="删除", step=step.Post(url=url, jump=True, submit_type="hide"))
        return o_button

    def make_form_close(self):
        """关闭按钮"""
        if self.request.GET.get(const.UPN_REDIRECT_URL, None):
            url = self.request.GET[const.UPN_REDIRECT_URL]
        else:
            url = self.model_admin.get_change_list_url(self.request)
            url = common.make_url(url, self.request,
                                  param={const.UPN_SCREEN_WIDTH: "{{window.innerWidth}}"},
                                  filter=[const.UPN_SCREEN_HEIGHT,
                                          const.UPN_OBJECT_ID, "id",
                                          const.UPN_STEPS_IDX
                                          ],
                                  )

        o_step = step.Post(url=url, jump=True, submit_type="hide")
        o_button = widgets.Button(text="关闭", step=o_step)
        return o_button

    def get_inline_queryset(self, obj_inline, fk_field_name):
        queryset = []
        if self.obj and self.obj.pk:
            db_field = admin_api.get_field(obj_inline, fk_field_name)

            if db_field.to_fields and db_field.to_fields[0]:
                value = getattr(self.obj, db_field.to_fields[0])
            else:
                value = self.obj.pk

            queryset = obj_inline.model.objects.filter(**{admin_api.get_attname(db_field, db_field.name): value})
            queryset = self.model_admin.get_inline_results(self.request, obj_inline, queryset, self.obj)

        queryset_default = self.model_admin.get_inline_default(self.request, obj_inline,
                                                               self.change and self.obj or None)

        return queryset, queryset_default

    def make_inline(self, inline):
        obj_inline = admin_api.get_admin(inline)
        obj_inline.parent_param = [self.obj]  # 设置父类参数，在admin中使用
        # obj_inline = inline(model=inline.model, admin_site=admin.site)

        self.fk_field_name = fk_field_name = admin_api.get_foreign_key_field(obj_inline, self.model_admin.model)
        plane_name = "plane_%s" % fk_field_name
        o_panel = widgets.Panel(name=plane_name, horizontal="right", width="100%")
        try:
            add = obj_inline.has_add_permission(self.request)
        except (TypeError,):
            add = obj_inline.has_add_permission(self.request, self.change and self.obj or None)
        except (BaseException,):
            raise

        display_effect = self.model_admin.get_inline_display_effect(self.request, obj_inline,
                                                                    self.change and self.obj or None)
        if display_effect == const.INLINE_DISPLAY_LIST:
            o_module = importlib.import_module("vadmin.templates.%s" % self.o_theme.template)
            o_change_list = o_module.ChangeList(self.request, obj_inline.opts.app_label,
                                                obj_inline.opts.model_name, self.o_theme)
            o_change_list.readonly = self.readonly
            db_field = admin_api.get_field(obj_inline, fk_field_name)
            field_name = db_field.name

            if self.obj and self.obj.pk:
                queryset = obj_inline.model.objects.filter(**{field_name: self.obj.pk})
                queryset = self.model_admin.get_inline_results(self.request, obj_inline, queryset,
                                                               self.change and self.obj or None)
                o_change_list.related_object_id = self.obj.pk
            else:
                queryset = obj_inline.model.objects.none()

            o_change_list.related_app_label = self.app_label
            o_change_list.related_model_name = self.model_name
            o_change_list.related_field_name = field_name
            o_change_list.display_mode = const.DM_LIST_CHILD
            o_change_list.lst_display = self.model_admin.get_inline_list_display(self.request, obj_inline,
                                                                                 self.change and self.obj or None)
            o_grid = o_change_list.make_list_view_child(queryset)
            o_panel.add_widget(o_grid)

        elif display_effect == const.INLINE_DISPLAY_TABULAR:
            o_table = self.make_inline_tabular(obj_inline, fk_field_name)
            o_panel.add_widget(o_table)
            o_panel.add_widget(widgets.Row(height=10))

            change1 = self.model_admin.has_change_permission(self.request, self.change and self.obj or None)
            row_data = self.make_inline_tabular_row(obj_inline, obj_inline.get_default_object(self.request))
            if change1 and add and self.is_edit and (not self.readonly):
                o_button = self.model_admin.make_inline_add(self.request, obj_inline, row_data,
                                                            self.change and self.obj or None)
                if o_button == const.USE_TEMPLATE:
                    o_button = self.make_inline_add(obj_inline, row_data)

                if o_button:
                    o_panel.add_widget(o_button)

            lst_widget = self.model_admin.make_inline_custom(self.request, obj_inline, row_data,
                                                             self.change and self.obj or None)

            o_panel.add_widget(lst_widget)
            o_panel.add_widget(widgets.Row(height=10))

        else:  # 叠放
            o_table = self.make_inline_stacked(obj_inline, fk_field_name)
            o_panel.add_widget(o_table)
            row_data = self.make_inline_stacked_row(obj_inline, obj_inline.get_default_object(self.request))  # 构造增加的行数据
            if add and self.is_edit and (not self.readonly):
                o_button = self.model_admin.make_inline_add(self.request, obj_inline, row_data,
                                                            self.change and self.obj or None)
                if o_button == const.USE_TEMPLATE:
                    o_button = self.make_inline_add(obj_inline, row_data)

                if o_button:
                    o_panel.add_widget(widgets.Row(height=10))
                    o_panel.add_widget(o_button)

            lst_widget = self.model_admin.make_inline_custom(self.request, obj_inline, row_data,
                                                             self.change and self.obj or None)
            o_panel.add_widget(lst_widget)
            o_panel.add_widget(widgets.Row(height=10))

        return o_panel

    def make_inline_tabular(self, obj_inline, fk_field_name):
        app_label, model_name = obj_inline.opts.app_label, obj_inline.opts.model_name
        table_name = const.WN_TABLE % (app_label, model_name)
        head_data, col_width, order_url = self.make_inline_tabular_head(obj_inline)

        queryset, queryset_default = self.get_inline_queryset(obj_inline, fk_field_name)
        data = []
        row_id = []
        count = -1
        for obj_sub in queryset:
            row_data = self.make_inline_tabular_row(obj_inline, obj_sub)
            data.append(row_data)

            if self.is_copy:  # 拷贝默认等于负数，前台为认为是增加
                row_id.append(count)
                count -= 1

            else:
                row_id.append(obj_sub.pk)

        for obj_sub in queryset_default:
            row_data = self.make_inline_tabular_row(obj_inline, obj_sub)
            data.append(row_data)
            row_id.append(count)
            count -= 1

        border_color = "#EBEEF5"
        o_table = widgets.Table(name=table_name, select=False, order_url=order_url,
                                head={"show": True, "data": head_data, "color": self.o_theme.right_bg_color},
                                row={"id": row_id, "min_height": 40},
                                col={"width": col_width},
                                width="100%",
                                row_border={"color": border_color},
                                border={"color": border_color, "width": [0, 0, 1, 0]},
                                space_left=10, space_right=10,
                                data=data)

        return o_table

    def make_inline_tabular_head(self, obj_inline):
        lst_fields = self.model_admin.get_inline_list_display(self.request, obj_inline, self.obj)
        table_config = self.model_admin.get_inline_config(self.request, obj_inline, self.obj)

        sortable = table_config.get("order", False)
        col_width = table_config.get("col_width", obj_inline.get_change_list_config(self.request).get('col_width', {}))
        head = []
        order_url = ""
        if sortable:
            app_label, model_name = obj_inline.opts.app_label, obj_inline.opts.model_name
            order_url = const.URL_LIST_ORDER % (app_label, model_name)

        col = 0
        for sub_field in lst_fields:
            if sub_field == "__str__":
                continue

            if sub_field == self.fk_field_name:
                continue

            if sub_field in col_width:
                col_width[col] = col_width[sub_field]
                del col_width[sub_field]

            try:
                db_field = admin_api.get_field(obj_inline, sub_field)  # 先使用字段, 有可能自定义和字段相同
                if db_field.null or db_field.blank:
                    if db_field.help_text:
                        o_icon = widgets.Icon(icon="el-icon-info", tooltip=str(db_field.help_text),
                                              tooltip_interval_time=100, margin_left=2)
                        head.append([str(db_field.verbose_name), o_icon])
                    else:
                        head.append(str(db_field.verbose_name))
                else:
                    if db_field.help_text:
                        o_icon = widgets.Icon(icon="el-icon-info", tooltip=str(db_field.help_text),
                                              tooltip_interval_time=100, margin_left=2)
                        head.append([str(db_field.verbose_name),
                                     widgets.Text(text=u" *", font_size=12, font_color="#ff0000"), o_icon])
                    else:
                        head.append([str(db_field.verbose_name),
                                     widgets.Text(text=u" *", font_size=12, font_color="#ff0000")])

            except (BaseException,):
                # 自定义字段
                if getattr(obj_inline, sub_field, None) or getattr(obj_inline, "list_v_%s" % sub_field, None):
                    fun = getattr(obj_inline, sub_field, None) or getattr(obj_inline, "list_v_%s" % sub_field, None)
                    if getattr(fun, "multiple_col", False):  # 自定义多列
                        lst_name = getattr(self.model_admin, "%s_short_description" % fun.__name__)(self.request)
                        head.extend(lst_name)
                    elif hasattr(fun, 'short_description'):
                        head.append(getattr(fun, 'short_description'))
                    else:
                        head.append(sub_field)

            col += 1

        change1 = self.model_admin.has_change_permission(self.request, self.change and self.obj or None)
        delete = obj_inline.has_delete_permission(self.request)
        if change1 and delete and self.is_edit:
            head.append(u"操作")
            col_num = len(head)
            if col_num != 1:
                col_width[len(head) - 1] = 60

        return head, col_width, order_url

    def make_inline_tabular_row(self, obj_inline, obj_sub):
        row_data = []
        change1 = self.model_admin.has_change_permission(self.request, self.change and self.obj or None)
        lst_fields = self.model_admin.get_inline_list_display(self.request, obj_inline,
                                                              self.change and self.obj or None)
        for sub_field in lst_fields:
            if sub_field == "__str__":
                continue

            if sub_field == self.fk_field_name:
                continue

            # 回调自定义字段
            fun = getattr(obj_inline, sub_field, None) or getattr(obj_inline, "list_v_%s" % sub_field, None) or \
                  getattr(obj_inline, "form_v_%s" % sub_field, None)
            if callable(fun):
                o_widget = fun(self.request, obj_sub)
                if isinstance(o_widget, widgets.Widget):
                    row_data.append(o_widget)
                elif isinstance(o_widget, dict) and ("widget" in o_widget):
                    row_data.append(o_widget["widget"])
                elif isinstance(o_widget, (list, tuple)):
                    row_data.append(o_widget)
                elif not o_widget:
                    row_data.append(o_widget)
                elif isinstance(o_widget, dict) and "widget" in o_widget:
                    row_data.append(o_widget["widget"])
                else:
                    row_data.append(None)
            else:
                lst_expand = []
                o_widget = field_translate.field_2_widget(self.request, obj_inline, sub_field, obj_sub,
                                                          is_edit=True, lst_expand=lst_expand)
                if o_widget:
                    change2 = admin_api.has_change_permission(self.request, obj_inline, sub_field, obj_sub)
                    disabled = (not change1) or (not change2)
                    o_widget.disabled = disabled
                    if disabled:
                        row_data.append(o_widget)
                    else:
                        if lst_expand:
                            lst_expand.insert(0, o_widget)
                            row_data.append(lst_expand)
                        else:
                            row_data.append(o_widget)
                else:
                    row_data.append(None)

        delete = obj_inline.has_delete_permission(self.request, obj_sub)
        if change1 and delete and self.is_edit:
            o_icon = self.model_admin.make_inline_delete(self.request, obj_inline, obj_sub)
            if o_icon == const.USE_TEMPLATE:
                o_icon = self.make_inline_delete(obj_inline, obj_sub)
            row_data.append(o_icon)
        # else:
        #     row_data.append(None)

        return row_data

    def make_inline_stacked(self, obj_inline, fk_field_name):
        app_label, model_name = obj_inline.opts.app_label, obj_inline.opts.model_name
        table_name = const.WN_TABLE % (app_label, model_name)

        queryset, queryset_default = self.get_inline_queryset(obj_inline, fk_field_name)
        data = []
        row_id = []
        count = -1
        for obj_sub in queryset:
            row_data = self.make_inline_stacked_row(obj_inline, obj_sub)
            data.append(row_data)
            if self.is_copy:  # 拷贝默认等于负数，前台为认为是增加
                row_id.append(count)
                count -= 1
            else:
                row_id.append(obj_sub.pk)

        for obj_sub in queryset_default:
            row_data = self.make_inline_stacked_row(obj_inline, obj_sub)
            data.append(row_data)
            row_id.append(count)
            count -= 1

        o_table = widgets.Table(name=table_name, data=data, width="100%",
                                row={"id": row_id},
                                # col={"width": col_width, "horizontal": {1: "center"}},
                                space_left=0, space_right=0,
                                min_row_height=2)

        return o_table

    def make_inline_stacked_row(self, obj_inline, obj_sub=None):
        o_widget = self.make_form_field(obj_inline, obj_sub, is_inline=True)
        delete = obj_inline.has_delete_permission(self.request, obj_sub)
        o_icon = None
        if delete and self.is_edit:
            o_icon = self.model_admin.make_inline_delete(self.request, obj_inline, obj_sub=obj_sub)
            if o_icon == const.USE_TEMPLATE:
                o_icon = self.make_inline_delete(obj_inline, obj_sub)

        color = common.calc_focus_color(self.o_theme.right_bg_color)
        o_grid = widgets.Grid(width="100%", border={"color": color, "width": "1,0,0,0"})
        o_grid.append(o_widget)
        if o_icon:
            o_grid.set_col_attr(1, width="5%", horizontal="center")
            o_grid.append(o_icon)

        return [o_grid, ]

    def make_inline_delete(self, obj_inline, obj_sub=None, obj=None):
        """构造inline的删除按钮"""
        url = const.URL_INLINE_DEL % (self.app_label, self.model_name,
                                      obj_inline.opts.app_label, obj_inline.opts.model_name)
        table_name = const.WN_TABLE % (obj_inline.opts.app_label, obj_inline.opts.model_name)

        if obj_sub:
            o_step = step.WidgetOpera(name=table_name, opera=const.OPERA_TABLE_ROW_DEL,
                                      data={"row_id": obj_sub.pk, "url": url})
        else:
            o_step = step.WidgetOpera(name=table_name, opera=const.OPERA_TABLE_ROW_DEL,
                                      data={"row_id": -1, "url": url})

        o_icon = widgets.Icon(icon="el-icon-delete", step=o_step, font_size=16)
        return o_icon

    def make_inline_add(self, obj_inline, row_data):
        """构造inline的增加按钮"""
        app_label, model_name = obj_inline.opts.app_label, obj_inline.opts.model_name
        table_name = const.WN_TABLE % (app_label, model_name)
        o_step = step.WidgetOpera(name=table_name, opera=const.OPERA_TABLE_ROW_ADD,
                                  data={"row_data": row_data})
        o_button = widgets.Button(text=_("Add"), step=o_step, margin_right=5)
        return o_button


class ChangeDel(Style):
    def __init__(self, request, model_admin, o_theme, lst_object_id):
        Style.__init__(self)
        self.request = request
        self.model_admin = model_admin
        self.o_theme = o_theme
        self.app_label = model_admin.opts.app_label
        self.model_name = model_admin.opts.model_name
        self.lst_object_id = lst_object_id

    def make_del_view(self, queryset=None):
        """
        构造删除页面
        """
        model = self.model_admin.model
        if queryset:
            lst_obj = queryset
        else:
            lst_obj = model.objects.filter(pk__in=self.lst_object_id)

        deleted_objects, perms_needed, protected = \
            admin_api.get_deleted_objects(lst_obj, self.request, self.model_admin.admin_site)

        tree_name = const.WN_TREE % self.model_name
        tree_data = common.format_tree(deleted_objects)
        url = const.URL_FORM_POPUP % (self.app_label, self.model_name)
        url = common.make_url(url, param={"object_id": "{{js.getTreeNodeId('%s')}}" % tree_name})
        o_step = step.Get(url=url, jump=False)
        o_tree = widgets.Tree(name=tree_name, select=False, data=tree_data, search=False, width="100%",
                              min_height=200, max_height="100%-120", event={"click": o_step})

        o_panel = widgets.Panel(
            vertical="top",
            height="100vh-%s" % (self.HEIGHT_TOP + self.MARGIN_TOP + self.MARGIN_BOTTOM),
            width="100%%-%s" % (self.MARGIN_LEFT + self.MARGIN_RIGHT),
            round=self.o_theme.theme_round,
            margin=self.MARGIN,
            bg_color=self.o_theme.right_bg_color
        )
        o_panel.add_widget(widgets.Row(height=10))
        o_panel.add_widget(widgets.Text(text=_("Delete?") + str(self.model_admin.opts.verbose_name), color="#C1413F",
                                        font_size=self.o_theme.font["size"] + 2, margin_left=10))
        o_panel.add_widget(widgets.Row(height=5))
        text = "请确认要删除选中的 %(objects_name)s 吗？以下所有对象和它相关的条目都将删除：" % \
               {"objects_name": self.model_admin.opts.verbose_name}
        o_text = widgets.Text(text=text, color="#FF0000", margin_left=10)
        o_panel.add_widget(o_text)
        o_panel.add_widget(widgets.Row(height=10))
        o_panel.add_widget(o_tree)
        o_panel.add_widget(widgets.Row(height=10))

        table_name = const.WN_TABLE % (self.app_label, self.model_name)
        if self.lst_object_id:
            url = common.make_url(const.URL_LIST_DEL % (self.app_label, self.model_name), self.request,
                                  param={"id": str(self.lst_object_id).replace(" ", "")}, filter=[table_name])
        else:
            url = common.make_url(const.URL_LIST_DEL % (self.app_label, self.model_name), self.request,
                                  filter=[table_name])

        o_step = step.Get(url=url)
        o_panel.add_widget(widgets.Button(text="是的, 我确定", step=o_step, margin=[0, 10, 0, 10]))
        o_step = step.ViewOpera(back=1)
        o_panel.add_widget(widgets.Button(text="返回", step=o_step))
        o_panel.add_widget(widgets.Row(height=10))
        return o_panel


class HomeView(Style):
    def __init__(self, request, o_theme):
        Style.__init__(self)
        self.request = request
        self.o_theme = o_theme

    def make_view(self):
        o_panel = widgets.Panel(
            width="100%",
            # height="100vh-%s" % self.HEIGHT_TOP,
            padding=self.MARGIN,
            bg_color=self.o_theme.bg_color,
            vertical="top",
            # scroll={"overflow": "auto"}
        )

        o_grid_top = widgets.Grid(height="50vh-%s" % self.HEIGHT_TOP)
        o_grid_top.set_col_attr(col=0, width="40%")
        o_grid_top.set_col_attr(col=1, width=20)
        o_grid_top.set_col_attr(col=2)

        # 操作日志
        o_panel_log = self.make_opera_log()
        o_grid_top.add_widget(o_panel_log, col=0)

        # 常用功能入口
        o_panel_common = self.make_common_link()
        o_grid_top.add_widget(o_panel_common)
        o_panel.add_widget(o_grid_top)
        o_panel.add_widget(widgets.Row(20))

        o_grid_bottom = widgets.Grid(height="50vh-%s" % (self.MARGIN_TOP + self.MARGIN_BOTTOM + 20))
        o_grid_bottom.set_col_attr(col=0, width="40%")
        o_grid_bottom.set_col_attr(col=1, width=20)
        o_grid_bottom.set_col_attr(col=2)

        o_grid_bottom.append(self.make_notify(), col=0)
        o_grid_bottom.append(self.make_workflow())
        o_panel.add_widget(o_grid_bottom)

        return o_panel

    def make_opera_log(self):
        from vadmin_standard.models import OperationLog
        o_panel = widgets.Panel(width="100%", height="100%", vertical="top",
                                scroll={"overflow": "auto"},
                                bg={"color": self.o_theme.right_bg_color},
                                border={"radius": self.o_theme.theme_round})
        lst_log = OperationLog.objects.filter(user_id=self.request.user.id)  # vadmin操作表
        node_width = 46
        node_height = 46
        data = []
        dict_type = {1: "新增", 2: "删除", 3: "修改"}
        for o_log in lst_log[0:20]:
            if o_log.operation_type == 1:
                color = "#58BE6A"
            elif o_log.operation_type == 2:
                color = "#D93817"
            else:
                color = "#6496F3"
            # color = random.choice(["#58BE6A", "#D93817", "#6496F3"])
            content = "%s{{\n}}%s{{\n}}%s{{\n}}" % \
                      (o_log.ip, o_log.operation_desc, o_log.create_time.strftime('%Y-%m-%d %H:%M:%S'))
            o_node = widgets.Button(text=dict_type[o_log.operation_type],
                                    width=node_width, height=node_height, bg_color=color)
            data.append({"content": content, "node": o_node})

        o_timeline = widgets.Timeline(data=data, width="98%", margin_left=10)
        o_panel.append(widgets.Icon(icon="el-icon-link", margin=10, height=36))
        o_panel.append(widgets.Text(text="操作日志", height=36))
        o_panel.append(widgets.Row(1, bg_color="#E6EAEC"))
        o_panel.append(o_timeline)
        return o_panel

    def make_common_link(self):
        from vadmin_standard.models import CommonLink
        o_panel = widgets.Panel(width="100%", height="100%", vertical="top",
                                scroll={"overflow": "auto"},
                                bg={"color": self.o_theme.right_bg_color},
                                border={"radius": self.o_theme.theme_round})
        o_panel.append(widgets.Icon(icon="el-icon-link", margin=10, height=36))
        o_panel.append(widgets.Text(text="常用功能入口", height=36))

        url = const.URL_RUN_SCRIPT % "vadmin.widget_view.common_link_delete"
        o_step = step_ex.ConfirmBox(data=self.make_common_link_del_view(), step=step.Post(url=url),
                                    title="编辑常用功能入口", mask=True, top=80, width=600)
        o_text = widgets.Text(text="编辑", font={"decoration": "underline"}, step=o_step,
                              font_color="#0088CC", margin_left=20, height=36)
        o_panel.append(o_text)
        o_panel.append(widgets.Row(1, bg_color="#E6EAEC"))

        button_width = 120
        button_height = 120
        lst_link = CommonLink.objects.filter(Q(user_id=self.request.user.id) | Q(user_id__isnull=True)). \
            order_by("-create_time")

        for o_link in lst_link:
            if not o_link.link:
                continue

            link = o_link.link.strip()
            if link.find("http") == 0:
                o_step2 = step.Get(href=link, jump=True)
            else:
                o_step2 = step.Get(url=link, jump=True)

            focus_color = common.calc_focus_color(o_link.background_color)
            o_button = widgets.Button(text=o_link.name, font={"size": 20},
                                      width=button_width, height=button_height,
                                      step=o_step2, margin=10,
                                      background_color=o_link.background_color, focus_bg_color=focus_color)
            o_panel.append(o_button)

        url = const.URL_RUN_SCRIPT % "vadmin.widget_view.common_link_add"
        o_step = step_ex.ConfirmBox(data=self.make_common_link_add_view(), step=step.Post(url=url),
                                    title="增加常用功能入口", mask=True, top=80, width=600)
        o_button = widgets.Button(text="+", font_size=32, width=button_width, height=button_height,
                                  step=o_step, margin=10)
        o_panel.add_widget(o_button)
        return o_panel

    def make_common_link_del_view(self):
        from vadmin_standard.models import CommonLink
        o_panel = widgets.Panel(width=600, padding=20)
        data = list()
        row_id = list()
        queryset = CommonLink.objects.filter(Q(user_id=self.request.user.id) | Q(user_id__isnull=True), is_del=True)
        for obj in queryset:
            data.append([obj.name])
            row_id.append(obj.pk)

        border_color = common.calc_black_white_color(self.o_theme.right_bg_color)
        o_table = widgets.Table(name="common_edit_table",
                                head={"data": ["链接名称", ], "row_border": {"color": border_color}},
                                row={"id": row_id}, data=data, width="100%", min_row_height=60,
                                select="multiple", bg_color=self.o_theme.right_bg_color,
                                row_border={"color": border_color})

        o_panel.append(o_table)
        return o_panel

    def make_common_link_add_view(self):
        """
        增加常用功能页面
        """
        data = list()
        data.append([widgets.Text(text="名称 * : ", keyword="*"),
                     widgets.Input(name="home_add_common_name", width=400)])
        data.append([widgets.Text(text="链接 * : ", keyword="*"),
                     widgets.Input(name="home_add_common_link", input_type="textarea", width=400, height=80)])

        return widgets.LiteTable(data=data, width=600, min_row_height=60,
                                 col_width={0: 120},
                                 col_horizontal={0: "right", 1: "left"},
                                 bg_color=self.o_theme.right_bg_color)

    def make_notify(self):
        o_panel = widgets.Panel(width="100%", height="100%", vertical="top",
                                scroll={"overflow": "auto"},
                                bg={"color": self.o_theme.right_bg_color},
                                border={"radius": self.o_theme.theme_round})
        o_panel.append(widgets.Icon(icon="el-icon-link", margin=10, height=36))
        o_panel.append(widgets.Text(text="我的消息", height=36))
        o_panel.append(widgets.Row(1, bg_color="#E6EAEC"))
        from vadmin_standard.models import Todo
        font_size = 13
        row_id = []
        data = []
        for obj in Todo.objects.filter(user_id=self.request.user.id, complete=False).order_by("create_time")[0:10]:
            row_id.append(obj.pk)
            if obj.name:
                o_text = widgets.Text(text=str(obj.name), font={"size": font_size})
            elif obj.desc:
                o_text = widgets.Text(text=str(obj.desc), font={"size": font_size})
            else:
                o_text = None

            o_time = widgets.Text(text=obj.create_time.strftime("%Y-%m-%d %H:%M"), font={"size": font_size})
            o_step = step.RunScript("vadmin_standard.service.todo_complete?%s=%s" % (const.UPN_OBJECT_ID, obj.pk))
            o_step_confirm = step_ex.MsgBox(request=self.request, text="确定提醒事项已完成?",
                                            step=[o_step, step.LayerClose()])
            o_button1 = widgets.Button(text="已完成", font={"size": font_size}, width=60, height=26,
                                       margin_right=10, step=o_step_confirm)
            if obj.link:
                o_button2 = widgets.Button(text="去完成", font={"size": font_size}, width=60, height=26,
                                           step=step.Get(url=obj.link, jump=True, new_window=True, unique=True))
            else:
                o_button2 = None

            data.append([o_text, o_time, (o_button1, o_button2)])

        o_table = widgets.Table(name="todo-table",
                                head={"data": ["说明", "时间", "操作"], "row_border": {"color": "#E6EAEC"}},
                                data=data, row={"id": row_id, "min_height": 50},
                                col={"width": {1: 156, 2: 146}}, width="100%",
                                row_border={"color": "#E6EAEC"})
        o_panel.append(o_table)
        return o_panel

    def make_workflow(self):
        o_panel = widgets.Panel(width="100%", height="100%", vertical="top",
                                scroll={"overflow": "auto"},
                                bg={"color": self.o_theme.right_bg_color},
                                border={"radius": self.o_theme.theme_round})
        o_panel.append(widgets.Icon(icon="el-icon-link", margin=10, height=36))
        o_panel.append(widgets.Text(text="电子流", height=36))
        o_panel.append(widgets.Row(1, bg_color="#E6EAEC"))
        from workflow.views import workflow_me_view
        o_panel.add_widget(workflow_me_view(self.request, True))
        return o_panel
