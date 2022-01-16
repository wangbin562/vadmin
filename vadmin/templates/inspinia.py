# !/usr/bin/python
# -*- coding=utf-8 -*-
"""
模板样式 http://www.inspinia.net/
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
from vadmin.templates import default


def menu_hide(request):
    hide_animation = animation.Animation(type="fold", change_style={"width": 60}, duration="0.3s")
    result = list()
    result.append(step.WidgetUpdate(data={"name": const.WN_CONTENT_LEFT, "collapse": True, "margin": 0, "width": 60}))
    # result.append(step.WidgetUpdate(data={"name": const.WN_CONTENT + "|0", "width": 60}))
    result.append(step.RunAnimation(name=const.WN_CONTENT + "|0", animation=hide_animation))
    result.append(step.WidgetUpdate(data={"name": const.WN_CONTENT + "|1", "width": "100%-60"}))
    result.append(step.WidgetUpdate(data={"name": const.WN_LOGO, "width": "30"}))
    result.append(step.WidgetUpdate(data={"name": const.WN_TITLE, "text": settings.V_TITLE[0]}))
    result.append(step.AddHide(data={const.WN_CONTENT_HIDE: 2}))
    return result


def menu_show(request):
    o_style = Style()
    show_animation = animation.Animation(type="fold", change_style={"width": o_style.WIDTH_LEFT}, duration="0.3s")
    result = list()
    result.append(step.WidgetUpdate(data={"name": const.WN_CONTENT_LEFT, "collapse": False, "margin": [0, 20, 0, 20],
                                          "width": "100%-40"}))
    # result.append(step.WidgetUpdate(data={"name": const.WN_CONTENT + "|0", "width": 220}))
    result.append(step.RunAnimation(name=const.WN_CONTENT + "|0", animation=show_animation))
    result.append(step.WidgetUpdate(data={"name": const.WN_CONTENT + "|1", "width": "100%%-%s" % o_style.WIDTH_LEFT}))
    result.append(step.WidgetUpdate(data={"name": const.WN_LOGO, "width": "80"}))
    result.append(step.WidgetUpdate(data={"name": const.WN_TITLE, "text": settings.V_TITLE}))
    result.append(step.AddHide(data={const.WN_CONTENT_HIDE: 1}))
    return result


class Style(object):
    """
    布局的位置配置
    """

    def __init__(self):
        self.HEIGHT_TOP = 50  # 头部高度
        self.WIDTH_LEFT = 260  # 左边宽度
        self.HEIGHT_TITLE = 50  # 标题高度
        self.HEIGHT_BOTTOM = 60  # 底部高度
        self.MARGIN_TOP = 10  # 内容区域顶部填充
        self.MARGIN_BOTTOM = 20  # 内容区域底部填充
        self.MARGIN_LEFT = 20  # 内容区域左边填充
        self.MARGIN_RIGHT = 20  # 内容区域右边填充
        self.MARGIN = [self.MARGIN_TOP, self.MARGIN_RIGHT, self.MARGIN_BOTTOM, self.MARGIN_LEFT]


class Page(default.Page, Style):
    def __init__(self, request, o_theme):
        super().__init__(request, o_theme)
        Style.__init__(self)

    def create(self, o_content=None):
        o_page = widgets.Page(bg_color=self.o_theme.bg_color)
        o_grid = widgets.Grid(name=const.WN_CONTENT, col_num=2, height="100vh", vertical="top",
                              bg={"color": self.o_theme.bg_color})

        if self.menu_id is not None:
            url = common.make_url(const.URL_LEFT, param={const.UPN_MENU_ID: self.menu_id})
            o_grid.set_col_attr(col=0, width=self.WIDTH_LEFT, url=url, scroll={"y": "auto"})
            o_grid.set_col_attr(col=1, width="100%%-%s" % self.WIDTH_LEFT)
        else:
            o_grid.set_col_attr(col=0, width=self.WIDTH_LEFT, scroll={"y": "auto"})
            o_grid.add_widget(col=0, widget=self.create_left())
            o_grid.set_col_attr(col=1, width="100%%-%s" % self.WIDTH_LEFT)

        url = common.make_url(const.URL_TOP, self.request)
        o_top = widgets.Panel(height=self.HEIGHT_TOP, width="100%", bg_color=self.o_theme.top_bg_color, url=url)
        o_grid.append(col=1, widget=o_top)

        if o_content:
            o_grid.append(col=1, widget=o_content)
        else:
            url, href = menu.get_url_by_menu_id(self.menu_id)
            if href:
                o_panel = widgets.Panel(name=const.WN_CONTENT_RIGHT, vertical="top", width="100%",
                                        height="100vh-%s" % self.HEIGHT_TOP,
                                        href=href)
                o_grid.append(col=1, widget=o_panel)
            else:
                url = common.make_url(url, self.request)
                o_panel = widgets.Panel(name=const.WN_CONTENT_RIGHT, vertical="top", width="100%", height="100%",
                                        url=url)
                o_grid.append(col=1, widget=o_panel)

        o_page.add_widget(o_grid)

        return o_page

    def create_top(self):
        menu_position = self.o_theme.menu_position
        o_top = widgets.Grid(name=const.WN_TOP, col_num=2, vertical="middle",
                             height=self.HEIGHT_TOP, bg_color=self.o_theme.top_bg_color, width="100%")

        # o_title = self.make_title()
        # o_top.add_widget(o_title, col=0)
        font_color = common.calc_black_white_color(self.o_theme.top_bg_color)
        hover_bg_color = common.calc_hover_color(self.o_theme.top_bg_color)
        font_size = self.o_theme.font["size"] + 2
        font = {"color": font_color, "size": font_size}

        if menu_position == "top":
            active = self.o_theme.menu.get("active", {})
            active["bg_color"] = common.calc_focus_color(self.o_theme.top_bg_color)
            active["font_color"] = common.calc_black_white_color(self.o_theme.top_bg_color)
            focus = self.o_theme.menu.get("focus", {})
            focus["bg_color"] = active["bg_color"]

            top_menu = widgets.Menu(name=const.WN_MENU_TOP,
                                    height=self.HEIGHT_TOP,
                                    direction="horizontal", bg={"color": self.o_theme.top_bg_color},
                                    font=font, focus=focus, active=active)

            for dict_item in self.lst_menu:
                top_id, left_id = menu.get_first_top_left_id(dict_item)
                dict_menu = copy.deepcopy(dict_item)
                if "children" in dict_menu:
                    del dict_menu["children"]

                dict_menu["id"] = top_id
                url = common.make_url(const.URL_HOME, param={const.UPN_TOP_ID: top_id, const.UPN_MENU_ID: left_id})
                dict_menu["step"] = step.Post(url=url, jump=True, submit_type="hide")

                top_menu.add_item(dict_menu)

            top_menu.value = self.top_id
            o_top.add_widget(top_menu, col=0)
        else:
            o_top.append(widgets.ButtonMutex(prefix="v-align-center", step=menu_hide(self.request),
                                             active_prefix="v-align-center", active_step=menu_show(self.request),
                                             margin_left=self.MARGIN_LEFT,
                                             width=40, height=36), col=0)

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
                o_widget = widgets.Button(prefix="el-icon-brush", tooltip=u"设置主题和布局",
                                          tooltip_interval_time=100,
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

            o_widget = widgets.Button(prefix="el-icon-user", tooltip=u"欢迎您，%s" % self.request.user)
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
            o_widget.hover = {"bg_color": hover_bg_color}

        o_top.add_widget(lst_widget, col=1)
        o_top.set_col_attr(col=0, width="100%%-%s" % all_width)
        o_top.set_col_attr(col=1, width=all_width, horizontal="right")
        return o_top

    def create_left(self):
        o_panel = widgets.Panel(width="100%", height="100vh",
                                horizontal="center", vertical="top", scroll={"y": "auto"},
                                border={"style": ["none", "box_shadow", "none", "none"]},
                                bg_color=self.o_theme.left_bg_color)
        logo = settings.V_LOGO
        title = settings.V_TITLE
        o_panel.append(widgets.Row(20))
        if logo:
            o_panel.append(widgets.Image(name=const.WN_LOGO, href=settings.STATIC_URL + logo, width=80))
            o_panel.append(widgets.Row(10))

        o_text = widgets.Text(name=const.WN_TITLE, text=title,
                              font={"size": 20,
                                    "color": common.calc_black_white_color(self.o_theme.left_bg_color)})
        o_panel.add_widget(o_text)
        o_panel.append(widgets.Row(20))

        font_color = common.calc_black_white_color(self.o_theme.left_bg_color)
        font_size = self.o_theme.font["size"] + 1
        font = {"color": font_color, "size": font_size}

        o_menu_left = None
        if self.o_theme.menu_position == "left":
            menu_data = list()
            menu.make_left_menu_list(self.request, self.lst_menu, menu_data)
            o_menu_left = widgets.Menu(value=self.left_id, data=menu_data)
        else:
            for i, dict_item in enumerate(self.lst_menu):
                menu_id = menu.get_menu_id(dict_item)
                if menu_id == self.top_id:
                    if "children" in dict_item:
                        menu_data = list()
                        menu.make_left_menu_list(self.request, dict_item["children"], menu_data)
                        o_menu_left = widgets.Menu(value=self.left_id, data=menu_data)
                    break

        if o_menu_left is None:
            o_menu_left = widgets.Menu()

        hover = self.o_theme.menu.get("hover", {})
        hover["bg_color"] = common.calc_focus_color(self.o_theme.left_bg_color)
        hover["font_color"] = common.calc_black_white_color(self.o_theme.left_bg_color)  # "#FFFFFF"
        hover["border_radius"] = self.o_theme.theme_round

        focus = self.o_theme.menu.get("focus", {})
        focus["bg_color"] = self.o_theme.theme_color
        focus["border_radius"] = self.o_theme.theme_round

        o_menu_left.name = const.WN_CONTENT_LEFT
        o_menu_left.width = "100%-40"
        # o_menu_left.height = "100vh"
        o_menu_left.font = font
        o_menu_left.hover = hover
        o_menu_left.focus = focus
        o_menu_left.bg = {"color": self.o_theme.left_bg_color}
        o_menu_left.margin = [0, 20, 0, 20]
        o_menu_left.space_top = 6
        o_menu_left.space_bottom = 6
        o_panel.append(o_menu_left)
        return o_panel


class ChangeList(default.ChangeList, Style):
    def __init__(self, request, app_label, model_name, o_theme):
        super().__init__(request, app_label, model_name, o_theme)
        Style.__init__(self)

    def make_list_view(self, queryset=None, row_id=None, row_id_field=None):
        """
        构造列表页
        """
        self.row_id = row_id
        self.row_id_field = row_id_field or "pk"
        if queryset is None:
            queryset = admin_api.get_filter_queryset(self.request, self.model_admin)

        o_panel = widgets.Panel(name=const.WN_CONTENT_RIGHT,
                                vertical="top",
                                height="100vh-%s" % (self.HEIGHT_TITLE + self.MARGIN_BOTTOM),
                                width="100%",
                                bg={"color": self.o_theme.bg_color})

        if self.is_title:
            title_area = self.make_title()
            o_panel.add_widget(title_area)

        o_panel_sub = self.make_list_view_child(queryset)
        o_panel.add_widget(o_panel_sub)
        return o_panel

    def make_list_view_child(self, queryset):
        self.queryset = queryset
        o_panel = widgets.Panel(name=const.WN_CHANGE_LIST % (self.app_label, self.model_name),
                                vertical="top", width="100%%-%s" % (self.MARGIN_LEFT + self.MARGIN_RIGHT),
                                margin=self.MARGIN)
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
        o_table.row_border = {"color": "#DDDDDD"}
        if self.display_mode == const.DM_LIST_SELECT:
            o_table.select = "single"
            o_table.submit_format = "select"
            o_table.height = "90vh-%s-%s" % (self.HEIGHT_TITLE + 2 + self.HEIGHT_BOTTOM +
                                             self.MARGIN_TOP + self.MARGIN_BOTTOM,
                                             const.WN_CONTENT_FILTER)
        elif self.display_mode == const.DM_LIST_CHILD:
            # o_table.height = "100vh-%s-%s" % (
            #     (self.HEIGHT_TOP + 16 + self.HEIGHT_TOP + self.MARGIN_BOTTOM + self.HEIGHT_BOTTOM),
            #     const.WN_CONTENT_FILTER)
            pass
        else:
            o_table.height = "100vh-%s-%s" % (
                (self.HEIGHT_TOP + self.HEIGHT_TITLE + self.MARGIN_TOP + self.MARGIN_BOTTOM + self.HEIGHT_BOTTOM + 2),
                const.WN_CONTENT_FILTER)

        o_panel.add_widget(widgets.Row(height=1))
        o_panel.add_widget(o_table)
        o_panel.add_widget(widgets.Row(height=1, bg_color=self.o_theme.bg_color))

        if self.is_bottom:
            bottom_area = self.make_bottom_area(queryset)
            o_panel.add_widget(bottom_area)

        return o_panel

    def make_title(self, title=None):
        o_grid = widgets.Grid(col_num=3, width="100%", height=self.HEIGHT_TITLE,
                              bg_color=self.o_theme.right_bg_color, padding=[5, 0, 5, 0], vertical="middle")
        o_grid.set_col_attr(col=0, width=14)
        # o_grid.set_col_attr(col=2, horizontal="right", width="auto")
        color = common.calc_black_white_color(self.o_theme.right_bg_color)
        font = {"size": self.o_theme.font["size"] + 2, "color": color}

        if title is None:
            menu_id = self.request.GET.get(const.UPN_MENU_ID, None)
            if menu_id:
                title = menu.get_label(menu_id)

            if not title:
                title = str(self.model_admin.opts.verbose_name)

        o_text = widgets.Text(text=title, padding_left=10, font=font)
        o_grid.add_widget(col=1, widget=o_text)

        # # 确定按钮
        # if self.display_mode == const.DM_LIST_SELECT:
        #     o_grid.set_col_attr(col=2, horizontal="right", width=200)
        #     o_button = self.make_ok_button()
        #     if o_button:
        #         o_button.margin = 4
        #     o_grid.add_widget(o_button)
        #     o_grid.add_widget(widgets.Col(width=10))
        #     o_button = self.make_close_button()
        #     if o_button:
        #         o_button.margin = 4
        #     o_grid.add_widget(o_button)
        #     o_grid.width = "100%"
        # else:
        #     lst_widget = self.make_add_button()
        #     if not isinstance(lst_widget, list):
        #         lst_widget = [lst_widget, ]
        #
        #     for o_button in lst_widget:
        #         if o_button:
        #             o_button.margin = 4
        #
        #     o_grid.set_col_attr(col=2, horizontal="right", width=len(lst_widget) * 90)
        #     o_grid.add_widget(lst_widget)

        return o_grid

    # def make_top_area(self):
    #     """构造头部区域"""
    #     o_panel = self.model_admin.make_list_top_area(self.request, self)
    #     if o_panel:
    #         return o_panel
    #
    #     # 过滤器
    #     filter_widget = self.make_filter()
    #     o_panel = widgets.Panel(bg_color=self.o_theme.right_bg_color, width="100%", padding_left=10)
    #     o_panel.append(widget=filter_widget)
    #
    #     return o_panel


class ChangeForm(default.ChangeForm, Style):
    def __init__(self, request, model_admin, o_theme, obj=None, is_copy=False):
        super().__init__(request, model_admin, o_theme, obj, is_copy)
        Style.__init__(self)
        self.fieldset_idx = 0
        self.is_tabs = False

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

        o_panel = widgets.Panel(name=const.WN_CONTENT_RIGHT,
                                scroll={"y": "auto"},
                                width="100%",
                                height="100vh-%s" % (self.HEIGHT_TOP + self.MARGIN_BOTTOM),
                                vertical="top")

        # 标题
        o_title = self.make_title()
        o_panel.add_widget(o_title)

        # 字段
        o_field = self.make_form_field(self.model_admin, self.obj)
        o_panel_field = widgets.Panel(width="100%%-%s" % (self.MARGIN_LEFT + self.MARGIN_RIGHT),
                                      margin_top=self.MARGIN_TOP, margin_left=self.MARGIN_LEFT,
                                      margin_right=self.MARGIN_RIGHT)
        o_panel_field.append(o_field)
        o_panel.add_widget(o_panel_field)

        if self.request.GET.get(const.UPN_DISPLAY_MODE, None) or self.display_mode:
            o_panel.set("height", "90vh")
            o_panel.append(widgets.Row(self.MARGIN_BOTTOM))

        # 操作按钮
        if is_save:
            if self.is_copy:  # 在copy情况下，要读取obj数据，在保存和删除情况下不使用
                o_panel_save = self.make_opera_area()
            else:
                o_panel_save = self.make_opera_area(self.change and self.obj or None)

            # o_panel.append(widgets.Row(self.HEIGHT_BOTTOM))
            o_panel.append(o_panel_save)

        return o_panel

    def make_title(self, title=None):
        o_title = self.model_admin.make_form_title(self.request, self, self.obj)
        if o_title is None:
            o_title = widgets.Panel(width="100%", height=self.HEIGHT_TITLE, bg_color=self.o_theme.right_bg_color)

            # 等于菜单名称或verbose_name
            if title is None:
                menu_id = self.request.GET.get(const.UPN_MENU_ID, None)
                if menu_id:
                    title = menu.get_label(menu_id)

                if not title:
                    title = str(self.model_admin.opts.verbose_name)

            text_color = common.calc_black_white_color(self.o_theme.right_bg_color)
            if self.display_mode or self.steps_idx is not None:
                o_text = widgets.Text(text=title,
                                      font={"color": text_color, "size": self.o_theme.font["size"] + 4},
                                      padding_left=10)
                o_title.add_widget(o_text)

            else:
                url = common.make_url(self.model_admin.get_change_list_url(self.request, obj=self.obj),
                                      self.request, filter=["id", const.UPN_STEPS_IDX])
                o_step = step.Post(url=url, jump=True, submit_type="hide")
                prefix = widgets.Icon(icon="el-icon-back")
                o_button = widgets.Button(prefix=prefix,
                                          text=title,
                                          font={"color": text_color, "size": self.o_theme.font["size"] + 4},
                                          border_color="transparent",
                                          bg_color="transparent",
                                          hover={"bg_color": "transparent",
                                                 "font_color": common.calc_focus_color(text_color)},
                                          step=o_step, margin_left=self.MARGIN_LEFT)
                o_title.add_widget(o_button)

        return o_title

    def make_fieldset(self, fieldset, model_admin, obj, max_num=1):
        name, dict_field = fieldset
        exclude_fields = model_admin.get_exclude(self.request, obj) or []

        flag_title = False
        o_panel = widgets.Panel(background_color=self.o_theme.right_bg_color, border={"color": "#E6EAEC"})
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
            o_panel.insert_widget(0, widgets.Row(1, bg_color="#E6EAEC"))
            o_text = widgets.Text(text=str(name),
                                  font={"weight": "bold", "size": self.o_theme.font["size"] + 1},
                                  margin=[10, 0, 10, 5])
            o_panel.insert_widget(0, o_text)

        return o_panel

    def make_opera_area(self, obj=None):
        """构造保存区域按钮"""
        # button_width = 170
        object_id = obj.pk if obj and obj.pk else None
        o_panel = widgets.Panel(width="100%%-%s" % (self.MARGIN_LEFT + self.MARGIN_RIGHT),
                                margin_left=self.MARGIN_LEFT, margin_right=self.MARGIN_RIGHT,
                                horizontal="center", vertical="middle",
                                height=self.HEIGHT_BOTTOM,
                                bg={'color': self.o_theme.right_bg_color}, border={"color": "#E6EAEC"})

        if self.display_mode == const.DM_FORM_POPUP:
            url = const.URL_FORM_SAVE_CLOSE % (self.app_label, self.model_name)
            url = common.make_url(url, self.request,
                                  param={const.UPN_DISPLAY_MODE: const.DM_FORM_POPUP,
                                         const.UPN_RELATED_APP: self.related_app_label,
                                         const.UPN_RELATED_MODEL: self.related_model_name,
                                         const.UPN_RELATED_FIELD: self.related_field_name,
                                         const.UPN_RELATED_ID: self.related_object_id,
                                         "id": object_id})

            o_step = step.Post(url=url, submit_type="layer", check_required=True)
            o_button = widgets.Button(text="保存并关闭", step=o_step)
            o_panel.add_widget(o_button)
            o_panel.add_widget(widgets.Col(10))

            # 增加保存编辑按钮
            url = const.URL_FORM_SAVE_EDIT % (self.app_label, self.model_name)
            url = common.make_url(url, self.request, param={"id": object_id})
            o_step = step.Post(url=url, submit_type="layer", check_required=True)
            o_button = widgets.Button(text="保存并继续编辑", step=o_step)
            o_panel.add_widget(o_button)
            o_panel.add_widget(widgets.Col(10))

            o_button = widgets.Button(text="关闭", step=step.LayerClose())
            o_panel.add_widget(o_button)
            o_panel.set_attr_value("float", {"left": self.MARGIN_LEFT, "bottom": self.MARGIN_BOTTOM, "mode": "window"})

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

                o_step = step.Post(url=url, submit_type="layer", check_required=True)
                o_button = widgets.Button(text="保存并关闭", step=o_step)
                o_panel.add_widget(o_button)
                o_panel.add_widget(widgets.Col(10))

            o_button = widgets.Button(text="关闭", step=step.LayerClose())
            o_panel.add_widget(o_button)
            o_panel.set_attr_value("float", {"left": self.MARGIN_LEFT, "bottom": self.MARGIN_BOTTOM, "mode": "window"})

        else:
            o_panel.set_attr_value("float", {"left": self.MARGIN_LEFT, "bottom": 0, "mode": "window"})
            # 自定义
            lst_button_form = self.model_admin.get_change_form_custom(self.request, obj)
            if not isinstance(lst_button_form, (tuple, list)):
                lst_button_form = [lst_button_form, ]

            for o_button in lst_button_form or []:
                if o_button is None:
                    continue

                o_button.border_color = None
                o_panel.add_widget(o_button)
                o_panel.add_widget(widgets.Col(10))

            # if self.model_admin.get_v_save_button(self.request, obj):
            if self.model_admin.has_change_permission(self.request, obj):
                # 先在admin
                o_button = self.model_admin.make_form_save(self.request, self, obj)
                if o_button == const.USE_TEMPLATE:  # 使用模板
                    o_button = self.make_form_save(obj)

                if o_button:
                    o_button.border_color = None
                    o_panel.add_widget(o_button)
                    o_panel.add_widget(widgets.Col(10))

                o_button = self.model_admin.make_form_save_edit(self.request, self, obj)
                if o_button == const.USE_TEMPLATE:
                    o_button = self.make_form_save_edit(obj)

                if o_button:
                    # o_button.border_color = None
                    o_panel.add_widget(o_button)
                    o_panel.add_widget(widgets.Col(10))

            if not self.show_mode and self.model_admin.has_add_permission(self.request) and \
                    self.model_admin.has_change_permission(self.request, obj):
                o_button = self.model_admin.make_form_save_add(self.request, self, obj)
                if o_button == const.USE_TEMPLATE:
                    o_button = self.make_form_save_add(obj)

                if o_button:
                    o_panel.add_widget(o_button)
                    o_panel.add_widget(widgets.Col(10))

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
                        o_panel.add_widget(o_button)
                        o_panel.add_widget(widgets.Col(10))

            o_button = self.model_admin.make_form_close(self.request, self)
            if o_button == const.USE_TEMPLATE:
                o_button = self.make_form_close()

            if o_button:
                o_panel.add_widget(o_button)
                o_panel.add_widget(widgets.Col(10))

        return o_panel


class ChangeDel(default.ChangeDel, Style):
    def __init__(self, request, model_admin, o_theme, lst_object_id):
        super().__init__(request, model_admin, o_theme, lst_object_id)
        Style.__init__(self)


class HomeView(default.HomeView, Style):
    def __init__(self, request, o_theme):
        super().__init__(request, o_theme)
        Style.__init__(self)
