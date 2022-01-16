#!/usr/bin/python
# -*- coding=utf-8 -*-

from vadmin import common
from vadmin import const
from vadmin import theme
from vadmin import widgets
from vadmin.step import *


class DialogBox(LayerPopup):
    """基础弹框"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def getConfirmArea(self, o_theme, is_cancel=True):
        o_panel = widgets.Panel(width="100%", height=60, horizontal="right")
        if is_cancel:
            bg_color = common.calc_black_white_color(o_theme.theme_color)
            font_color = common.calc_black_white_color(bg_color)
            focus_color = common.calc_focus_color(o_theme.theme_color)
            o_panel.append(widgets.Button(text="取消", margin_right=10, step=LayerClose(),
                                          bg={"color": "transparent"},
                                          font={"color": o_theme.theme_color},
                                          focus={"bg_color": focus_color, "font_color": font_color}))
        if getattr(self, "step", None):
            o_panel.append(widgets.Button(text="确定", margin_right=10, step=self.step))
        elif "button" in self.__dict__:
            o_panel.append(self.__dict__["button"])
        else:
            o_panel.append(widgets.Button(text="确定", margin_right=10, step=LayerClose()))
        return o_panel


class ConfirmBox(DialogBox):
    """确认框"""

    def __init__(self, request=None, title=None, text=None,
                 data=None, step=None, button=None, **kwargs):
        """
        title:弹出框标题(str或对象)
        content:弹出框内容
        step:弹出框确定步骤
        """
        self.request = request
        self.text = text
        self.data = data
        self.step = step
        self.button = button
        super().__init__(**kwargs)

        title = title or "确定"
        if isinstance(title, str):
            self.title = widgets.Text(text=title, width="100%-20", height=50, margin_left=20, vertical="middle",
                                      font={"size": 18, "weight": "bold"})
        else:
            self.title = self.title

    def render(self):
        o_panel = widgets.Panel(scroll={"overflow": "hidden"}, width="100%")
        o_theme = theme.get_theme(self.request)

        if self.text:
            o_panel1 = widgets.Panel(width="100%", height=50)
            o_panel1.append(widgets.Text(text=self.text, font={"size": 16}, margin_left=20))
            o_panel.append(o_panel1)

        if self.data:
            o_panel.append(self.data)

        o_panel.append(self.getConfirmArea(o_theme))

        dict_data = super().render()

        dict_data["data"] = o_panel
        dict_data["top"] = self.__dict__.get("top", 120)
        dict_data["width"] = self.__dict__.get("width", 400)
        if not self.data:
            dict_data["height"] = self.__dict__.get("height", 160)

        try:
            dict_style = eval(o_theme.style)
            radius = dict_style["button"]["border"]["radius"]
        except (BaseException,):
            radius = 4

        dict_data["border"] = self.__dict__.get("border", {"radius": radius})
        dict_data["esc_close"] = True

        return dict_data


class MsgBox(DialogBox):
    """提示确认框"""

    def __init__(self, title=None, text=None, msg_type=None, step=None, request=None, **kwargs):
        self.text = text
        self.msg_type = msg_type
        self.step = step
        self.request = request
        super().__init__(**kwargs)
        title = title or "提醒"
        if isinstance(title, str):
            self.title = widgets.Text(text=title, width="100%-20", height=50, margin_left=20, vertical="middle",
                                      font={"size": 18, "weight": "bold"})
        else:
            self.title = self.title

    def render(self):
        o_panel = widgets.Panel(scroll={"overflow": "hidden"}, width="100%")
        o_theme = theme.get_theme(self.request)

        size = 30
        if self.msg_type == "warning":
            o_icon = widgets.Icon(icon="el-icon-warning", font={"color": "#E9AB24", "size": size})
        elif self.msg_type == "success":
            o_icon = widgets.Icon(icon="el-icon-success", font={"color": "#0AA653", "size": size})
        elif self.msg_type == "error":
            o_icon = widgets.Icon(icon="el-icon-error", font={"color": "#C10116", "size": size})
        else:
            o_icon = widgets.Icon(icon="el-icon-info", font={"color": "#474B52", "size": size})

        o_icon.set_attr_value("margin_left", 20)
        o_icon.set_attr_value("margin_right", 10)

        max_height = self.__dict__.get("height", 660)
        o_grid = widgets.Grid(width="100%", col_num=3, vertical="middle", max_height=max_height - 50 - 60)
        o_grid.set_col_attr(width=60, col=0)
        o_grid.set_col_attr(width=20, col=2)
        o_grid.append(o_icon, col=0)
        o_grid.append(widgets.Text(text=self.text, font={"size": 16}), col=1)
        o_panel.append(o_grid)

        o_panel.append(self.getConfirmArea(o_theme, False))

        dict_data = super().render()

        dict_data["data"] = o_panel
        dict_data["top"] = self.__dict__.get("top", 120)
        dict_data["width"] = self.__dict__.get("width", 400)
        # dict_data["height"] = height
        try:
            dict_style = eval(o_theme.style)
            radius = dict_style["button"]["border"]["radius"]
        except (BaseException,):
            radius = 4

        dict_data["border"] = self.__dict__.get("border", {"radius": radius})
        dict_data["esc_close"] = True
        dict_data["click_close"] = True

        return dict_data


class InputBox(ConfirmBox):
    """输入确认框"""

    def __init__(self, title=None, value=None, step=None, request=None, **kwargs):
        o_panel = widgets.Panel(width="100%")
        o_panel.add_widget(widgets.Input(name=const.WN_BOX_INPUT, required=True, width="100%-40",
                                         margin_left=20, value=value))
        o_panel.add_widget(widgets.Row(height=20))

        kwargs["width"] = 460
        super().__init__(text=title, data=o_panel, step=step, request=request, **kwargs)


class SelectBox(ConfirmBox):
    """选择确认框"""

    def __init__(self, title=None, desc=None, data=None, value=None, step=None, request=None, **kwargs):
        bg_color = self.__dict__.get("bg_color", "#FFFFFF")
        o_panel = widgets.Panel(width="100%", bg_color=bg_color, horizontal="left")
        o_panel.add_widget(widgets.Row(height=10))
        if desc:
            o_panel.append(widgets.Text(text=desc.replace("\n", "{{\n}}"), margin=10))

        o_panel.add_widget(
            widgets.Select(name=const.WN_BOX_SELECT,
                           required=True, width="100%-20", margin=10,
                           data=data, value=value))
        o_panel.add_widget(widgets.Row(height=20))
        super().__init__(title=title, data=o_panel, step=step, request=request, **kwargs)
