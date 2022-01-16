# !/usr/bin/python
# -*- coding=utf-8 -*-
"""
模仿
https://www.creative-tim.com/?_ga=2.101759617.1097910116.1609579572-1507775082.1609382066
"""

from django.conf import settings

from vadmin import admin_api
from vadmin import common
from vadmin import const
from vadmin import menu
from vadmin import step
from vadmin import widget_view
from vadmin import widgets
from vadmin import field_translate
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
        self.HEIGHT_TOP = 70  # 头部高度
        self.WIDTH_LEFT = 260  # 左边宽度
        self.HEIGHT_TITLE = 50  # 标题高度
        self.HEIGHT_BOTTOM = 50  # 底部高度
        self.MARGIN_TOP = 20  # 内容区域顶部填充
        self.MARGIN_BOTTOM = 20  # 内容区域底部填充
        self.MARGIN_LEFT = 20  # 内容区域左边填充
        self.MARGIN_RIGHT = 20  # 内容区域右边填充
        self.MARGIN = "20,20,20,20"


class Page(default.Page, Style):
    def __init__(self, request, o_theme):
        super().__init__(request, o_theme)
        Style.__init__(self)

    def create(self, o_content=None):
        o_page = widgets.Page(bg_color=self.o_theme.bg_color)
        o_grid = widgets.Grid(name=const.WN_CONTENT, col_num=2, height="100vh", vertical="top",
                              bg={"color": self.o_theme.bg_color})
        o_grid.set_col_attr(col=0, width=0)

        if self.menu_id is not None:
            url = common.make_url(const.URL_LEFT, param={const.UPN_MENU_ID: self.menu_id})
            o_grid.set_col_attr(col=0, width=self.WIDTH_LEFT, url=url, scroll={"y": "auto"})
            o_grid.set_col_attr(col=1, width="100%%-%s" % self.WIDTH_LEFT, scroll={"y": "hidden"})
        else:
            o_grid.set_col_attr(col=0, width=0, scroll={"y": "auto"})
            o_grid.add_widget(col=0, widget=self.create_left())  # 位置打桩

        url = common.make_url(const.URL_TOP, self.request)
        o_top = widgets.Panel(height=self.HEIGHT_TOP, width="100%", bg_color=self.o_theme.top_bg_color, url=url)
        o_grid.append(col=1, widget=o_top)

        if o_content:
            o_grid.append(col=1, widget=o_content)
        else:
            url, href = menu.get_url_by_menu_id(self.menu_id)
            if href:
                o_panel = widgets.Panel(name=const.WN_CONTENT_RIGHT, vertical="top", width="100%", height="100%",
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
        height = 36
        o_panel = widgets.Panel(width="100%", height=self.HEIGHT_TITLE, horizontal="left")
        o_panel.append(widgets.ButtonMutex(prefix="v-align-center", step=menu_hide(self.request),
                                           active_prefix="v-align-center", active_step=menu_show(self.request),
                                           margin_left=self.MARGIN_LEFT,
                                           width=40, height=height))

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
                                          step=step.Post(url="v_theme_view/", jump=True, submit_type="hide"))
                lst_widget.append(o_widget)

            o_widget = widgets.Button(prefix="el-icon-user", tooltip=u"欢迎您，%s" % self.request.user)
            lst_widget.append(o_widget)

            if settings.V_TOP_UPDATE_PWD:
                o_step = widget_view.make_update_pwd(self.request, self.o_theme)
                o_widget = widgets.Button(prefix="el-icon-unlock", tooltip=u"修改密码", step=o_step)
                lst_widget.append(o_widget)

            o_widget = widgets.Button(prefix="el-icon-switch-button", tooltip=u"退出",
                                      step=step.Get(url="v_logout/", submit_type="hide"))
            lst_widget.append(o_widget)

        width = 40
        for o_widget in lst_widget:
            o_widget.bg = {"color": self.o_theme.top_bg_color}
            if o_widget.get("width", None) is None:
                o_widget.width = width
            o_widget.height = height
            o_widget.font_color = "#555555"
            bg_color = common.calc_hover_color(self.o_theme.top_bg_color)
            o_widget.hover = {"bg_color": bg_color}
            o_widget.position = "right"

        o_panel.append(lst_widget)
        return o_panel

    def create_left(self):
        o_panel = widgets.Panel(width="100%", height="100vh",
                                horizontal="center", vertical="top", scroll={"y": "auto"},
                                border={"style": ["none", "box_shadow", "none", "none"]},
                                bg={"image": settings.STATIC_URL + "vadmin/img/material/sidebar-4.jpg",
                                    "opacity": 0.93}
                                )
        logo = settings.V_LOGO
        title = settings.V_TITLE
        o_panel.append(widgets.Row(20))
        if logo:
            o_panel.append(widgets.Image(name=const.WN_LOGO, href=settings.STATIC_URL + logo, width=80))
            o_panel.append(widgets.Row(10))

        o_text = widgets.Text(name=const.WN_TITLE, text=title, font={"size": 20, "color": "#3C4858"})
        o_panel.add_widget(o_text)
        o_panel.append(widgets.Row(20))

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

        if o_menu_left:
            focus = {"bg_color": self.o_theme.theme_color, "font_color": "#FFFFFF"}
            o_menu_left.name = const.WN_CONTENT_LEFT
            o_menu_left.width = "100%-40"
            o_menu_left.focus = focus
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
                                height="100vh",
                                width="100%",
                                bg={"color": self.o_theme.bg_color},
                                padding=self.MARGIN)
        # o_panel.add_widget(widgets.Row(10))

        o_panel_sub = self.make_list_view_child(queryset)
        o_panel.add_widget(o_panel_sub)
        if self.display_mode == const.DM_LIST_SELECT:
            o_panel.height = "90vh"

        return o_panel

    def make_list_view_child(self, queryset):
        self.queryset = queryset
        o_panel = widgets.Panel(name=const.WN_CHANGE_LIST % (self.app_label, self.model_name),
                                vertical="top", width="100%")
        if self.is_top:
            top_area = self.make_top_area()
            top_area.name = const.WN_CONTENT_FILTER
            o_panel.add_widget(top_area)

        o_table = self.model_admin.make_list_table(self.request, self, queryset)
        if o_table is None:
            self.config.lst_display_links = []
            o_table = self.make_list_table(queryset)
            o_table.bg = {"color": "#FFFFFF"}

        o_table.value = self.row_id
        o_table.row_border = {"color": "#DDDDDD"}
        if self.display_mode == const.DM_LIST_SELECT:
            o_table.select = "single"
            o_table.submit_format = "select"
            o_table.height = "90vh-123-%s" % const.WN_CONTENT_FILTER  # 标题头部固定50px
        elif self.display_mode == const.DM_LIST_CHILD:
            # o_table.height = "100vh-%s-%s" % (
            #     (self.HEIGHT_TOP + 16 + self.HEIGHT_TOP + self.MARGIN_BOTTOM + self.HEIGHT_BOTTOM),
            #     const.WN_CONTENT_FILTER)
            pass
        else:
            o_table.height = "100vh-%s-%s" % (
                (self.HEIGHT_TOP + self.MARGIN_TOP + self.MARGIN_BOTTOM + self.HEIGHT_BOTTOM + 2),
                const.WN_CONTENT_FILTER)

        o_panel.add_widget(widgets.Row(height=1, bg_color=self.o_theme.bg_color))
        o_panel.add_widget(o_table)
        o_panel.add_widget(widgets.Row(height=1, bg_color=self.o_theme.bg_color))

        if self.is_bottom:
            bottom_area = self.make_bottom_area(queryset)
            bottom_area.round = [0, 0, self.o_theme.theme_round, self.o_theme.theme_round]
            o_panel.add_widget(bottom_area)

        return o_panel

    def make_top_area(self):
        """构造头部区域"""
        o_grid = self.model_admin.make_list_top_area(self.request, self)
        if o_grid:
            return o_grid

        # 过滤器
        filter_widget = self.make_filter()

        o_grid = widgets.Grid(col_num=4, bg={"color": self.o_theme.right_bg_color},
                              border={"radius": [self.o_theme.theme_round, self.o_theme.theme_round, 0, 0]},
                              padding=[6, 0, 6, 0])
        o_grid.set_col_attr(col=0, width=14)
        o_grid.set_col_attr(col=1, width=80)

        o_grid.append(col=2, widget=filter_widget)

        title = ""
        menu_id = self.request.GET.get(const.UPN_MENU_ID, None)
        if menu_id:
            title = menu.get_label(menu_id)

        if not title:
            title = str(self.model_admin.opts.verbose_name)

        if self.display_mode != const.DM_LIST_CHILD:
            o_grid.append(widgets.Button(text=title[:6], width=60, height=60, margin_top=-20, focus={}), col=1)

        # 确定按钮
        if self.display_mode == const.DM_LIST_SELECT:
            o_grid.set_col_attr(col=3, horizontal="right", width=200)
            o_button = self.make_ok_button()
            o_grid.add_widget(o_button)
            o_grid.add_widget(widgets.Col(width=10))
            o_button = self.make_close_button()
            o_grid.add_widget(o_button)
            o_grid.width = "100%"
        elif not self.readonly:
            lst_widget = self.make_add_button()
            if not isinstance(lst_widget, list):
                lst_widget = [lst_widget, ]

            width = 10
            for o_widget in lst_widget:
                if isinstance(o_widget, (dict, widgets.Widget)):
                    width += o_widget.get("width", 80)

            o_grid.set_col_attr(col=3, horizontal="right", width=width)
            o_grid.append(lst_widget)
        return o_grid


class ChangeForm(default.ChangeForm, Style):
    def __init__(self, request, model_admin, o_theme, obj=None, is_copy=False):
        super().__init__(request, model_admin, o_theme, obj, is_copy)
        Style.__init__(self)
        self.fieldset_idx = 0
        self.is_tabs = False

    def make_form_view(self, is_save=True):
        """构造表单页面"""
        o_grid = widgets.Grid(name=const.WN_CONTENT_RIGHT,
                              col_num=2, padding=[0, self.MARGIN_RIGHT, self.MARGIN_BOTTOM, self.MARGIN_LEFT],
                              scroll={"y": "auto"},
                              width="100%",
                              height="100vh-%s" % self.HEIGHT_TOP,
                              vertical="top")

        if self.display_mode == const.DM_FORM_POPUP:
            o_grid.scroll = None
            o_grid.height = None
            o_grid.padding_top = self.MARGIN_BOTTOM
            o_grid.padding_right = self.MARGIN_RIGHT
            o_grid.padding_bottom = self.MARGIN_BOTTOM
            o_grid.padding_left = self.MARGIN_LEFT
            o_grid.padding = None

        # o_grid.set_col_attr(col=0, bg={"color": self.o_theme.right_bg_color})
        if is_save:
            o_grid.set_col_attr(col=1, width=200, horizontal="center")
        else:
            o_grid.set_col_attr(col=1, width=0)

        # 字段
        o_grid_field = self.make_form_field(self.model_admin, self.obj)
        o_grid.add_widget(o_grid_field, col=0)

        # 操作按钮
        if is_save:
            if self.is_copy:  # 在copy情况下，要读取obj数据，在保存和删除情况下不使用
                o_panel_save = self.make_opera_area()
            else:
                o_panel_save = self.make_opera_area(self.obj)

            o_grid.add_widget(o_panel_save)

        return o_grid

    def make_form_field(self, model_admin, obj=None, is_inline=False):
        if model_admin.get_tabs(self.request, obj):
            self.is_tabs = True
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
            o_widget = widgets.Tabs(name=tabs_name, data=tab_data, value=tabs_value, width="100%",
                                    bg={"color": self.o_theme.right_bg_color},
                                    border={"radius": self.o_theme.theme_round},
                                    event={"change": step.Get(splice=tabs_name, submit_type="update_url")})

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
        # fieldset_num = len(fieldsets)
        for i, fieldset in enumerate(fieldsets):
            self.fieldset_idx = i
            o_panel, add_title = self.make_fieldset(fieldset, model_admin, obj, max_num)
            if add_title:
                if self.is_tabs and i == 0:
                    pass
                elif i == 0:
                    lst_widget.append(widgets.Row(height=20, bg={"color": self.o_theme.bg_color}))
                else:
                    lst_widget.append(widgets.Row(height=32, bg={"color": self.o_theme.bg_color}))

            app_label = model_admin.model._meta.app_label
            model_name = model_admin.model._meta.model_name
            o_panel.name = const.WN_FIELDSET % (app_label, model_name, i)
            lst_widget.append(o_panel)

        return lst_widget

    def make_fieldset(self, fieldset, model_admin, obj, max_num=1):
        name, dict_field = fieldset
        exclude_fields = model_admin.get_exclude(self.request, obj) or []

        flag_title = False
        o_panel = widgets.Panel(background_color=self.o_theme.right_bg_color, round=self.o_theme.theme_round)
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

        add_title = False
        if flag_title and (name is not None):
            if (not self.is_tabs) or (self.is_tabs and self.fieldset_idx != 0):
                o_button = widgets.Button(text=str(name), width=60, height=60, margin_top=-14, margin_left=14, focus={})
                o_panel.insert(0, o_button)
                add_title = True
                # if self.is_tabs and self.fieldset_idx == 0:
                #     o_panel.insert(0, widgets.Row(40))

        return o_panel, add_title

    def make_opera_area(self, obj=None):
        o_panel = super().make_opera_area(obj)
        if not self.display_mode:
            o_panel.set_attr_value("float", {"right": 10, "top": self.HEIGHT_TOP})

        return o_panel


class ChangeDel(default.ChangeDel, Page):
    def __init__(self, request, model_admin, o_theme, lst_object_id):
        super().__init__(request, model_admin, o_theme, lst_object_id)
        Style.__init__(self)


class HomeView(default.HomeView, Style):
    def __init__(self, request, o_theme):
        super().__init__(request, o_theme)
        Style.__init__(self)
