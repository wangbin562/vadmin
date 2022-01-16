# !/usr/bin/python
# -*- coding=utf-8 -*-
"""
扩展组件
"""
from vadmin import step
from vadmin import widgets
from vadmin import const


class WidgetEx(object):
    pass

    def render(self):
        return {}

    def __str__(self):
        return self.render()

    def __repr__(self):
        import json
        from vadmin.json_encoder import Encoder
        dict_data = self.render()
        return json.dumps(dict_data, ensure_ascii=False, cls=Encoder)


class ImageManager(WidgetEx):

    def __init__(self, search_url, select_url):
        super().__init__()
        self.search_url = search_url
        self.select_url = select_url
        self.widget_type = "image_manager"
        # self.name = kwargs.get("name", None)

    def render(self):
        dict_data = dict()
        dict_data["widget_type"] = self.widget_type
        dict_data["search_url"] = self.search_url
        dict_data["select_url"] = self.select_url

        return dict_data


class TitleBar(WidgetEx):
    """标题栏"""

    def __init__(self, **kwargs):
        super().__init__()
        self.title = kwargs.get("title", None)
        self.height = kwargs.get("height", 50)
        self.float = kwargs.get("float", False)
        self.bg = kwargs.get("bg", None)
        # self.is_back = kwargs.get("is_back", True)
        if kwargs.get("back", None):
            self.back = kwargs["back"]
        else:
            o_button = widgets.Button(
                prefix=widgets.Icon(icon="el-icon-arrow-left", font={"size": 20, "color": "#222222"}),
                width="100%", height=self.height,
                hover={"bg_color": "transparent"}, bg={"color": "transparent"},
                step=step.ViewOpera(back=1),
                # step=[step.Get(url="v_app_home/", jump=True), step.ViewOpera(back=1)]
            )

            self.back = o_button

        self.setting = kwargs.get("setting", None)  # 标题栏后面的设置项

    def render(self):
        if self.float:
            o_grid = widgets.Grid(col_num=3, width="100%", height=self.height, vertical="center",
                                  float=self.float, bg=self.bg)
        else:
            o_grid = widgets.Grid(col_num=3, width="100%", height=self.height, vertical="center",
                                  bg=self.bg)

        o_grid.set_col_attr(col=0, horizontal="left", width=50)
        o_grid.set_col_attr(col=1, horizontal="center")
        o_grid.set_col_attr(col=2, horizontal="right", width=50)
        if self.back:
            o_grid.add_widget(self.back, col=0)

        if self.title:
            if isinstance(self.title, str):
                self.title = widgets.Text(text=self.title, font={"size": 16, "weight": "bold"})
            o_grid.add_widget(self.title, col=1)

        if self.setting:
            o_grid.add_widget(self.setting)

        return o_grid.render()


class SearchBar(WidgetEx):
    def __init__(self, **kwargs):
        super().__init__()
        self.height = kwargs.get("height", 50)
        self.float = kwargs.get("float", False)
        self.bg = kwargs.get("bg", None)
        self.placeholder = kwargs.get("placeholder", None)
        self.input_widget_name = kwargs.get("input_widget_name", "input-search-key")
        self.table_widget_name = kwargs.get("table_widget_name", "table-search-result")
        self.search_url = kwargs.get("search_url", None)

        if kwargs.get("back", None):
            self.back = kwargs["back"]
        else:
            o_button = widgets.Button(
                prefix=widgets.Icon(icon="el-icon-arrow-left", font={"size": 20, "color": "#222222"}),
                width=40, height="100%",
                hover={"bg_color": "transparent"}, bg={"color": "transparent"},
                step=step.ViewOpera(back=1),
                # step=[step.Get(url="v_app_home/", jump=True), step.ViewOpera(back=1)]
            )

            self.back = o_button

    def input_view(self):
        o_grid = widgets.Grid(col_num=3, width="100%", height=self.height, vertical="center",
                              float=self.float, bg=self.bg)

        o_grid.set_col_attr(col=0, width=50, horizontal="left")
        o_grid.set_col_attr(col=1, horizontal="center")
        o_grid.set_col_attr(col=2, width=50, horizontal="center")

        o_button = widgets.Button(
            prefix=widgets.Icon(icon="el-icon-arrow-left", font={"size": 20, "color": "#222222"}),
            width=40, height="100%",
            hover={"bg_color": "transparent"}, bg={"color": "transparent"},
            step=step.LayerClose(),
        )
        o_grid.append(o_button, col=0)

        o_step = step.RunScript(self.search_url, splice=[self.input_widget_name])
        o_input = widgets.Input(name=self.input_widget_name, active=True,
                                prefix=widgets.Icon(icon="el-icon-search"), width="100%",
                                placeholder=self.placeholder,
                                border={"radius": 50},
                                bg={"color": "#FFFFFF"},
                                event={"input": o_step}
                                )
        o_grid.append(o_input, col=1)

        o_text = widgets.Text(text="搜索",
                              step=step.Get(url=self.search_url, splice=[self.input_widget_name]))
        o_grid.append(o_text)

        o_panel = widgets.Panel(width="100vw", height="100vh", bg={"color": "#FFFFFF"}, vertical="top")
        o_panel.append(o_grid)
        o_table = widgets.LiteTable(name=self.table_widget_name)
        o_panel.append(o_table)
        return o_panel

    def render(self):
        o_grid = widgets.Grid(col_num=3, width="100%", height=self.height, vertical="center",
                              float=self.float, bg=self.bg)

        o_grid.set_col_attr(col=0, width=50, horizontal="left")
        o_grid.set_col_attr(col=1, horizontal="center")
        o_grid.set_col_attr(col=2, width=50, horizontal="right")
        if self.back:
            o_grid.add_widget(self.back, col=0)

        o_input = widgets.Input(prefix=widgets.Icon(icon="el-icon-search"), width="100%",
                                placeholder=self.placeholder,
                                border={"radius": 50},
                                bg={"color": "#FFFFFF"}, event={"click": step.LayerPopup(data=self.input_view())})
        o_grid.append(o_input, col=1)

        # if self.title:
        #     if isinstance(self.title, str):
        #         self.title = widgets.Text(text=self.title, text_size=18)
        #     o_grid.add_widget(self.title, col=1)
        #
        # if self.setting:
        #     o_grid.add_widget(self.setting)

        return o_grid.render()

        # if self.suspension:
        #     o_grid = widgets.Grid(col_num=2, width="100%", height=self.height, suspension_x=0, suspension_y=0,
        #                           background_color=self.background_color)
        # else:
        #     o_grid = widgets.Grid(col_num=2, width="100%", height=self.height,
        #                           background_color=self.background_color)
        #
        # o_grid.set_col_attr(col=0, horizontal="left")
        # o_grid.set_col_attr(col=1, horizontal="right", width="20%")
        # o_grid.add_widget(widgets.Input(prefix_icon=widgets.Icon(class_name="el-icon-search"), width="90%",
        #                                 value=self.search_key,
        #                                 placeholder=self.placeholder, margin_left=10), col=0)
        #
        # if self.close_popup:
        #     o_grid.add_widget(widgets.Button(text="搜索",
        #                                      step=[step.GridClose(), step.Get(url=self.search_url, jump=True)],
        #                                      margin_right=10))
        #
        # else:
        #     o_grid.add_widget(widgets.Button(text="搜索", url=self.search_url, jump=True, margin_right=10))
        #
        # # if self.setting:
        # #     o_grid.add_widget(self.setting, col=1)
        #
        # if self.suspension:
        #     return [o_grid.render(), widgets.Row(self.height)]
        #
        # return o_grid.render()


class InputBar(WidgetEx):
    """输入栏"""

    def __init__(self, **kwargs):
        super().__init__()
        self.input = kwargs.get("input", None)
        self.height = kwargs.get("height", 50)
        self.float = kwargs.get("float", False)
        self.bg = kwargs.get("bg", None)
        self.border = kwargs.get("border", None)
        self.submit = kwargs.get("submit", None)

    def render(self):
        o_grid = widgets.Grid(col_num=2, width="100%", height=self.height, vertical="center",
                              float=self.float, bg=self.bg, border=self.border)

        o_grid.set_col_attr(col=0, horizontal="left")
        o_grid.set_col_attr(col=1, horizontal="center", width=80)
        o_grid.append(self.input, col=0)
        o_grid.append(self.submit)

        return o_grid.render()


class Breadcrumb(WidgetEx):
    def __init__(self, data=None, head_icon=None, separator_icon=None, focus=None):
        self.data = data
        self.head_icon = head_icon
        self.separator_icon = separator_icon
        self.focus = focus

    def render(self):
        o_panel = widgets.Panel()
        if self.head_icon:
            if isinstance(self.head_icon, str):
                o_panel.append(widgets.Icon(icon=self.head_icon, margin_right=6))
            else:
                o_panel.append(self.head_icon)

        count = len(self.data)
        for i, item in enumerate(self.data):
            o_text = widgets.Text(text=item["label"])
            if "step" in item:
                o_text.step = item["step"]
            elif "url" in item:
                o_text.step = step.Get(url=item["url"])

            o_text.focus = self.focus
            o_panel.append(o_text)

            if i < (count - 1):
                if self.separator_icon:
                    if isinstance(self.separator_icon, str):
                        o_panel.append(widgets.Icon(icon=self.separator_icon))
                    else:
                        o_panel.append(self.separator_icon)
                else:
                    o_panel.append(" / ")

        return o_panel


class RadioColor(WidgetEx):
    def __init__(self, name=None, data=None, value=None,
                 width=None, height=None, item_width=None, item_height=None,
                 activate=None, deactivate=None):
        self.name = name
        self.data = data
        self.value = value
        self.width = width
        self.height = height
        self.item_width = item_width or 80
        self.activate = item_height or 80
        self.item_height = item_height or 80
        self.activate = activate
        self.deactivate = deactivate

    def render(self):
        o_panel = widgets.Panel(width=self.width, height=self.height)
        data = []
        for color in self.data:
            o_sub = widgets.Panel(bg={"color": color}, horizontal="right", vertical="top",
                                  width=self.item_width, height=self.item_height, margin_right=20)
            o_sub.append(widgets.Icon(icon="el-icon-circle-check", font={"size": 26, "color": "#FFFFFF"},
                                      margin=[6, 6, 0, 0]))
            data.append([color, o_sub])

        o_widget = widgets.Group(name=self.name, data=data, value=self.value,
                                 activate=self.activate, deactivate=self.deactivate)
        o_panel.append(o_widget)
        return o_panel
