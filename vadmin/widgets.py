# !/usr/bin/python
# -*- coding=utf-8 -*-
"""
组件
"""
import collections
import os
import re

from vadmin import common
from vadmin import const
from vadmin import event
from vadmin import step


class Widget(object):
    """
    组件基类，不能实例化
    """

    def __init__(self,
                 href=None,
                 url=None,

                 name=None, type=None, hide=None,
                 data=None, value=None,
                 position=None, opacity=None,
                 vertical=None, horizontal=None,
                 required=None, readonly=None,

                 space_left=None, space_right=None,
                 space_top=None, space_bottom=None,
                 width=None, height=None,
                 min_width=None, min_height=None,
                 max_width=None, max_height=None,
                 font=None, bg=None, active=None,
                 border=None, focus=None,
                 scroll=None, hover=None,
                 event=None, step=None,
                 disabled=None, disabled_style=None,
                 tooltip=None, tooltip_style=None,
                 placeholder=None, placeholder_style=None,
                 padding=None, padding_top=None, padding_right=None, padding_bottom=None, padding_left=None,
                 margin=None, margin_top=None, margin_right=None, margin_bottom=None, margin_left=None,
                 **kwargs):

        # object.__setattr__(self, 'kwargs', kwargs)
        if type is None:
            # widget_type = "widget"

            try:
                this = self.__class__
                while True:
                    widget_type = this.__name__
                    this = this.__base__
                    if this.__name__ == "Widget":
                        break
                lst_type = re.findall('[A-Z][^A-Z]*', widget_type)
                self.type = "_".join(lst_type).lower()
            except (BaseException,):
                pass
        else:
            self.type = type

        if url is not None:
            self.url = url
        if href is not None:
            self.href = href

        if space_left is not None:
            self.space_left = space_left
        if space_right is not None:
            self.space_right = space_right
        if space_top is not None:
            self.space_top = space_top
        if space_bottom is not None:
            self.space_bottom = space_bottom

        # 公用
        if name is not None:
            self.name = name
        if hide is not None:
            self.hide = hide
        if data is not None:
            self.data = data
        if value is not None:
            self.value = value
        if position is not None:
            self.position = position
        if opacity is not None:
            self.opacity = opacity
        if vertical is not None:
            self.vertical = vertical
        if horizontal is not None:
            self.horizontal = horizontal
        if required is not None:
            self.required = required
        if readonly is not None:
            self.readonly = readonly
        if width is not None:
            self.width = width
        if height is not None:
            self.height = height
        if min_width is not None:
            self.min_width = min_width
        if min_height is not None:
            self.min_height = min_height
        if max_width is not None:
            self.max_width = max_width
        if max_height is not None:
            self.max_height = max_height
        if font is not None:
            self.font = font
        if bg is not None:
            self.bg = bg
        if active is not None:
            self.active = active
        if border is not None:
            self.border = border
        if focus is not None:
            self.focus = focus
        if scroll is not None:
            self.scroll = scroll
        if hover is not None:
            self.hover = hover
        # self.event = event or {}
        if event is not None:
            self.event = event
        if step is not None:
            self.step = step
        if disabled is not None:
            self.disabled = disabled
        if disabled_style is not None:
            self.disabled_style = disabled_style
        if tooltip is not None:
            self.tooltip = tooltip
        if tooltip_style is not None:
            self.tooltip_style = tooltip_style
        if placeholder is not None:
            self.placeholder = placeholder
        if placeholder_style is not None:
            self.placeholder_style = placeholder_style
        if padding is not None:
            self.padding = padding
        if padding_top is not None:
            self.padding_top = padding_top
        if padding_right is not None:
            self.padding_right = padding_right
        if padding_bottom is not None:
            self.padding_bottom = padding_bottom
        if padding_left is not None:
            self.padding_left = padding_left
        if margin is not None:
            self.margin = margin
        if margin_top is not None:
            self.margin_top = margin_top
        if margin_right is not None:
            self.margin_right = margin_right
        if margin_bottom is not None:
            self.margin_bottom = margin_bottom
        if margin_left is not None:
            self.margin_left = margin_left

        for k, v in kwargs.items():
            if v is None:
                continue

            setattr(self, k, v)

    # def __str__(self):
    #     return self.render()

    def __repr__(self):
        import json
        from vadmin.json_encoder import Encoder
        dict_data = self.render()
        return json.dumps(dict_data, ensure_ascii=False, cls=Encoder)

    def format_background(self, kwargs):
        background = {}
        if "bg_color" in kwargs:
            background["color"] = kwargs["bg_color"]
            del kwargs["bg_color"]
        elif "background_color" in kwargs:
            background["color"] = kwargs["background_color"]
            del kwargs["background_color"]

        if "bg_image" in kwargs:
            background["image"] = kwargs["bg_image"]
            del kwargs["bg_image"]
        elif "background_image" in kwargs:
            background["image"] = kwargs["background_image"]
            del kwargs["background_image"]

        return background

    def format_border(self):
        border = {}
        if "border_color" in self.__dict__:
            border["color"] = self.__dict__["border_color"]
            del self.__dict__["border_color"]

        if "border_style" in self.__dict__:
            border["style"] = self.__dict__["border_style"]
            del self.__dict__["border_style"]

        if "border_width" in self.__dict__:
            border["width"] = self.__dict__["border_width"]
            del self.__dict__["border_width"]

        if "border_radius" in self.__dict__:
            border["radius"] = self.__dict__["border_radius"]
            del self.__dict__["border_radius"]

        if "round" in self.__dict__:
            border["radius"] = self.__dict__["round"]
            del self.__dict__["round"]

        # if "border" in self.__dict__ and self.__dict__["border"]:
        #     for k, v in self.__dict__["border"].items():
        #         if isinstance(v, (list, tuple)):
        #             v = str(v).strip("[]").replace(",", " ").replace("'", "").replace('"', '')
        #             border[k] = v
        #         else:
        #             border[k] = v

        if border and border.get("color", None):
            if "style" not in border:
                border["style"] = "solid"

            if "width" not in border:
                border["width"] = "1px 1px 1px 1px"
        #

        # if "color" in border:
        #     if "style" not in border:
        #         border["style"] = "solid"
        #
        #     if "width" not in border:
        #         border["width"] = "1px"

        # if border:
        #     if "border" in self.self.__dict__:
        #         self.__dict__["border"].update(border)
        #     else:
        #         self.__dict__["border"] = border

        return border

    def format_float(self):
        float = {}
        if "float_x" in self.__dict__:
            float["x"] = self.__dict__["float_x"]
            del self.__dict__["float_x"]

        if "float_y" in self.__dict__:
            float["y"] = self.__dict__["float_y"]
            del self.__dict__["float_y"]

        # if hover:
        #     if "hover" in self.__dict__:
        #         self.__dict__["hover"].update(hover)
        #     else:
        #         self.__dict__["hover"] = hover

        return float

    def format_focus(self):
        focus = {}
        if "focus_bg_color" in self.__dict__:
            focus["bg_color"] = self.__dict__["focus_bg_color"]
            del self.__dict__["focus_bg_color"]

        if "focus_color" in self.__dict__:
            focus["bg_color"] = self.__dict__["focus_color"]
            del self.__dict__["focus_color"]

        if "focus_font_color" in self.__dict__:
            focus["font_color"] = self.__dict__["focus_font_color"]
            del self.__dict__["focus_font_color"]

        if "focus_border_color" in self.__dict__:
            focus["border_color"] = self.__dict__["focus_border_color"]
            del self.__dict__["focus_border_color"]

        if "focus_line_color" in self.__dict__:
            focus["line_color"] = self.__dict__["focus_line_color"]
            del self.__dict__["focus_line_color"]

        if "focus_line_width" in self.__dict__:
            focus["line_width"] = self.__dict__["focus_line_width"]
            del self.__dict__["focus_line_width"]

        return focus

    def format_font(self):
        font = {}
        if "font_color" in self.__dict__:
            font["color"] = self.__dict__["font_color"]
            del self.__dict__["font_color"]

        if "font_size" in self.__dict__:
            font["size"] = self.__dict__["font_size"]
            del self.__dict__["font_size"]

        if "font_family" in self.__dict__:
            font["family"] = self.__dict__["border_family"]
            del self.__dict__["border_family"]

        if "font_weight" in self.__dict__:
            font["weight"] = self.__dict__["font_weight"]
            del self.__dict__["font_weight"]

        if "font_decoration" in self.__dict__:
            font["decoration"] = self.__dict__["font_decoration"]
            del self.__dict__["font_decoration"]

        if "font_style" in self.__dict__:
            font["style"] = self.__dict__["font_style"]
            del self.__dict__["font_style"]

        if "font_spacing" in self.__dict__:
            font["spacing"] = self.__dict__["font_spacing"]
            del self.__dict__["font_spacing"]

        return font

    def set_attr_value(self, attr, value):
        self.__dict__[attr] = value
        return self

    def get_attr_value(self, attr, default=None):
        return self.__dict__.get(attr, default)

    def set(self, key, value):
        self.__dict__[key] = value
        return self

    def get(self, key, default=None):
        return self.__dict__.get(key, default)

    def __setitem__(self, key, value):
        self.__dict__[key] = value
        return self

    def __getitem__(self, key):
        return self.__dict__.get(key, None)

    def render(self):
        self.check_param()
        dict_data = collections.OrderedDict()
        # dict_data["type"] = self.kwargs.get("type", None)
        # if "name" in self.kwargs:
        #     dict_data["name"] = self.kwargs["name"]

        padding = self.__dict__.get("padding", None)
        if padding not in [[0, 0, 0, 0], None, "0,0,0,0", ""]:
            dict_data["padding"] = padding
        else:
            padding = [0, 0, 0, 0]
            padding[0] = self.__dict__.get("padding_top", 0) or 0
            padding[1] = self.__dict__.get("padding_right", 0) or 0
            padding[2] = self.__dict__.get("padding_bottom", 0) or 0
            padding[3] = self.__dict__.get("padding_left", 0) or 0
            if padding != [0, 0, 0, 0]:
                dict_data["padding"] = "%s,%s,%s,%s" % tuple(padding)

        margin = self.__dict__.get("margin", None)
        if margin not in [[0, 0, 0, 0], None, "0,0,0,0", ""]:
            dict_data["margin"] = margin
        else:
            margin = [0, 0, 0, 0]
            margin[0] = self.__dict__.get("margin_top", 0) or 0
            margin[1] = self.__dict__.get("margin_right", 0) or 0
            margin[2] = self.__dict__.get("margin_bottom", 0) or 0
            margin[3] = self.__dict__.get("margin_left", 0) or 0
            if margin != [0, 0, 0, 0]:
                dict_data["margin"] = margin

        if "step" in self.__dict__ and self.__dict__["step"]:
            self.event = {"click": self.step}
            # del self.__dict__["step"]
        # elif "url" in self.__dict__:
        #     self.event = {"click": step.Get(url=self.__dict__["url"])}
        #     del self.__dict__["url"]

        if "event" in self.__dict__:
            dict_event = {}
            if isinstance(self.event, (list, tuple)):
                for o_event in self.event:
                    dict_event[o_event.type] = o_event
            elif isinstance(self.event, dict):
                pass
            elif self.event:
                dict_event[self.event.type] = self.event

            if dict_event:
                self.event = dict_event

        bg = self.format_background(self.__dict__)
        if bg:
            self.__dict__.setdefault("bg", {}).update(bg)

        border = self.format_border()
        if border:
            self.__dict__.setdefault("border", {}).update(border)

        font = self.format_font()
        if font:
            self.__dict__.setdefault("font", {}).update(font)

        focus = self.format_focus()
        if focus:
            self.__dict__.setdefault("focus", {}).update(focus)

        dict_float = self.format_float()
        if dict_float:
            self.__dict__.setdefault("float", {}).update(dict_float)

        if "scroll" in self.__dict__:
            if "xy" in self.__dict__["scroll"]:
                self.__dict__["scroll"]["overflow"] = self.__dict__["scroll"]["xy"]
                del self.__dict__["scroll"]["xy"]

            if "overflow_x" in self.__dict__["scroll"]:
                self.__dict__["scroll"]["x"] = self.__dict__["scroll"]["overflow_x"]
                del self.__dict__["scroll"]["overflow_x"]

            if "overflow_y" in self.__dict__["scroll"]:
                self.__dict__["scroll"]["y"] = self.__dict__["scroll"]["overflow_y"]
                del self.__dict__["scroll"]["overflow_y"]

        if ("children" in self.__dict__) and (self.__dict__["children"] is not None):
            if not isinstance(self.__dict__["children"], (tuple, list)):
                self.__dict__["children"] = [self.__dict__["children"]]

        for k, v in self.__dict__.items():
            if k in ["padding_top", "padding_right", "padding_bottom", "padding_left",
                     "margin_top", "margin_right", "margin_bottom", "margin_left", "parameter_name",
                     "padding", "margin"]:
                continue

            if v is None:
                continue

            if isinstance(v, bool):
                v = int(v)

            # k = admin_api.get_short_name(k)
            dict_data[k] = v

        # if "children" in dict_data:
        #     children = []
        #     for item in dict_data["children"]:
        #         children.append(item.render())
        #     dict_data["children"] = children

        return dict_data

    def get_children(self):
        return self.__dict__.get("children", []) or []

    def add_widget(self, widget):
        data = self.__dict__.get("children", []) or []
        if isinstance(widget, (tuple, list)):
            data.extend(widget)
        elif widget not in [None, "{}"]:
            data.append(widget)
        else:
            try:
                sub = widget.render()
                if isinstance(sub, (tuple, list)):
                    data.extend(sub)
                elif widget not in [None, "{}"]:
                    data.append(sub)
            except (BaseException,):
                data.append(widget)

        self.__dict__["children"] = data

        return self

    def append(self, widget):
        return self.add_widget(widget)

    def add_event(self, event):
        data = self.__dict__.get("event", {}) or {}

        if hasattr(event, "param") and event.param:
            data[event.type] = event
        elif isinstance(event, dict):
            data.update(event)
        else:
            data[event.type] = event.step

        self.event = data

        return self

    def check_param(self):
        horizontal = self.__dict__.get("horizontal", None)
        vertical = self.__dict__.get("vertical", None)
        if horizontal not in [None, 'left', 'center', 'right']:
            raise ValueError("horizontal参数值错误:%s, 可填值:['left', 'center', 'right']" % horizontal)

        if vertical not in [None, 'top', 'middle', 'bottom']:
            if vertical == "center":
                self.vertical = "middle"
            else:
                raise ValueError("vertical参数值错误:%s, 可填值:['top', 'middle', 'bottom']" % vertical)

        for key in ["bg", "border", "font", "focus", "hover", "float", "scroll"]:
            val = self.__dict__.get(key, None)
            if val is None:
                continue

            if not isinstance(val, dict):
                raise ValueError("%s参数值错误:%s" % (key, val))


class Row(Widget):
    """
    行间距
    """

    def __init__(self, height=None, bg=None, **kwargs):
        kwargs["height"] = height
        kwargs["bg"] = bg
        super(Row, self).__init__(**kwargs)


class Col(Widget):
    """
    列间距
    """

    def __init__(self, width=None, bg=None, **kwargs):
        kwargs["width"] = width
        kwargs["bg"] = bg
        super().__init__(**kwargs)


class Button(Widget):
    """
    按钮
    """

    def __init__(self, text=None, font=None, bg=None,
                 width=None, height=None, prefix=None, suffix=None,
                 horizontal=None, vertical=None, border=None, active=None,
                 remote_method=None, focus=None,
                 timed_start=None, timed_second=None, timed_step=None,
                 **kwargs):
        if text is not None:
            self.text = str(text)

        # if prefix is not None:
        #     if isinstance(prefix, str):
        #         self.prefix = Icon(icon=prefix)
        #     else:
        #         self.prefix = prefix
        #
        # if suffix is not None:
        #     if isinstance(suffix, str):
        #         self.suffix = Icon(icon=suffix)
        #     else:
        #         self.suffix = suffix

        if timed_start is not None:
            self.timed_start = timed_start
        if timed_second is not None:
            self.timed_second = timed_second
        if timed_step is not None:
            self.timed_step = timed_step
        if remote_method is not None:
            self.remote_method = remote_method
        kwargs["prefix"] = prefix
        kwargs["suffix"] = suffix
        kwargs["width"] = width
        kwargs["height"] = height
        kwargs["font"] = font
        kwargs["bg"] = bg
        kwargs["horizontal"] = horizontal
        kwargs["vertical"] = vertical
        kwargs["border"] = border
        kwargs["active"] = active
        kwargs["focus"] = focus
        super().__init__(**kwargs)

    def render(self):
        if "step" in self.__dict__:
            self.event = {"click": self.step}
            del self.__dict__["step"]  # 要删除，要不有两个事件

        elif "url" in self.__dict__:
            self.event = {"click": step.Get(url=self.__dict__["url"])}
            # del self.__dict__["url"]

        dict_data = super().render()
        if ("icon" in dict_data) and ("prefix" not in dict_data):
            prefix = Icon(icon=dict_data["icon"])
            dict_data["prefix"] = prefix
            del dict_data["icon"]
        elif "prefix_icon" in dict_data:
            prefix = Icon(icon=dict_data["prefix_icon"])
            dict_data["prefix"] = prefix
            del dict_data["prefix_icon"]
        return dict_data


class ButtonMutex(Widget):
    """
    互斥按钮
    """

    def __init__(self, **kwargs):
        kwargs["type"] = "button_mutex"
        super().__init__(**kwargs)

    def render(self):
        dict_data = super().render()
        # if "prefix" in dict_data:
        #     prefix = Icon(icon=dict_data["prefix"])
        #     dict_data["prefix"] = prefix
        #     if "active_prefix" not in dict_data:
        #         dict_data["active_prefix"] = prefix

        # elif "prefix_icon" in dict_data:
        #     prefix = Icon(icon=dict_data["prefix_icon"])
        #     dict_data["prefix"] = prefix
        #     del dict_data["prefix_icon"]
        #     if "active_prefix" not in dict_data:
        #         dict_data["active_prefix"] = prefix

        # if "active_prefix" in dict_data:
        #     active_prefix = Icon(icon=dict_data["active_prefix"])
        #     dict_data["active_prefix"] = active_prefix

        if "active_step" in dict_data:
            dict_data["active_event"] = {"click": dict_data["active_step"]}

        return dict_data


class Text(Widget):
    """
    文字
    """

    def __init__(self, text=None, font=None, bg=None,
                 direction=None, inline=None, keyword=None, keyword_color=None,
                 horizontal=None, vertical=None, border=None, active=None,
                 **kwargs):
        if text is not None:
            self.text = str(text)
        if direction is not None:
            self.direction = direction
        if inline is not None:
            self.inline = inline
        if keyword is not None:
            self.keyword = keyword
        if keyword_color is not None:
            self.keyword_color = keyword_color

        kwargs["bg"] = bg
        kwargs["horizontal"] = horizontal
        kwargs["vertical"] = vertical
        kwargs["border"] = border
        kwargs["active"] = active
        kwargs["font"] = font
        super().__init__(**kwargs)


class Json(Widget):
    """
    json
    """

    def __init__(self, text=None, width=None, height=None,
                 max_height=None, **kwargs):
        if text is not None:
            self.text = text
        if width is not None:
            self.width = width
        if height is not None:
            self.height = height
        if max_height is not None:
            self.max_height = max_height

        super().__init__(**kwargs)


class Icon(Widget):
    """
    图标
    """

    def __init__(self, icon=None, font=None, **kwargs):
        if icon is not None:
            self.icon = icon

        kwargs["font"] = font
        super().__init__(**kwargs)


class Image(Widget):
    """
    图片
    """

    def __init__(self, href=None, active_href=None,
                 width=None, height=None, enlarge=None, **kwargs):
        if active_href is not None:
            self.active_href = active_href
        kwargs["href"] = href
        kwargs["width"] = width
        kwargs["height"] = height
        kwargs["enlarge"] = enlarge
        super().__init__(**kwargs)


class Checkbox(Widget):
    """
    复选框
    """

    def __init__(self, data=None, value=None, theme=None, direction=None,
                 width=None, height=None, bg=None, border=None,
                 active=None, focus=None, **kwargs):
        if theme is not None:
            self.theme = theme
        if direction is not None:
            self.direction = direction
        kwargs["data"] = data
        kwargs["value"] = value
        kwargs["width"] = width
        kwargs["height"] = height
        kwargs["bg"] = bg
        kwargs["border"] = border
        kwargs["active"] = active
        kwargs["focus"] = focus
        super().__init__(**kwargs)

    def render(self):
        dict_data = super().render()
        if "value" in dict_data:
            if isinstance(dict_data["value"], int):
                dict_data["value"] = [dict_data["value"], ]
            # elif isinstance(dict_data["value"], (tuple, list)):
            #     dict_data["value"] = "%s" % dict_data["value"]

        return dict_data


class CheckboxBool(Widget):
    """布尔值单选框"""

    pass


class Input(Widget):
    """
    输入框
    """

    def __init__(self, input_type=None, data=None, value=None,
                 max_length=None, auto_size=None, step_num=None,
                 prefix=None, suffix=None, encrypt=None,
                 width=None, height=None, max_height=None,
                 border=None, hover=None, focus=None,
                 disabled=None, disabled_style=None,
                 **kwargs):
        if input_type is not None:
            self.input_type = input_type
        if max_length is not None:
            self.max_length = max_length
        if auto_size is not None:
            self.auto_size = auto_size
        if step_num is not None:
            self.step_num = step_num
        if encrypt is not None:
            self.encrypt = encrypt

        if prefix is not None:
            if isinstance(prefix, str):
                self.prefix = Icon(icon=prefix)
            else:
                self.prefix = prefix

        if suffix is not None:
            if isinstance(suffix, str):
                self.suffix = Icon(icon=suffix)
            else:
                self.suffix = suffix

        kwargs["data"] = data
        kwargs["value"] = value
        kwargs["width"] = width
        kwargs["height"] = height
        kwargs["max_height"] = max_height
        kwargs["border"] = border
        kwargs["hover"] = hover
        kwargs["focus"] = focus
        kwargs["disabled"] = disabled
        kwargs["disabled_style"] = disabled_style
        super().__init__(**kwargs)

    def set_remote_method(self, app_label=None, model_name=None, search_field=None, **kwargs):
        """
        设置远程搜索
        :param app_label:
        :param model_name:
        :param search_field:单个字段或多个字段
        :return:
        """
        if isinstance(search_field, str):
            search_field = [search_field, ]

        url = "v_input_search/%s/%s/%s/" % (app_label, model_name, search_field)

        if kwargs:
            url = url + "?" + "&".join(["%s=%s" % (k, v[0]) for k, v in kwargs.items()])

        self.remote_method = url


class Slider(Widget):
    """
    滑杆
    """

    def __init__(self, min=None, max=None, value=None,
                 bg=None, **kwargs):
        if min is not None:
            self.min = min
        if max is not None:
            self.max = max
        kwargs["value"] = value
        kwargs["bg"] = bg
        super().__init__(**kwargs)


class Switch(Widget):
    """
    开关
    """

    def __init__(self, value=None, width=None, height=None,
                 **kwargs):
        kwargs["value"] = value
        kwargs["width"] = width
        kwargs["height"] = height
        super().__init__(**kwargs)


class Select(Widget):
    """
    选择器
    """

    def __init__(self, data=None, value=None, multiple=None, clearable=None,
                 filterable=None, width=None, **kwargs):
        kwargs["data"] = data
        kwargs["value"] = value
        kwargs["multiple"] = multiple
        kwargs["clearable"] = clearable
        kwargs["filterable"] = filterable
        kwargs["width"] = width
        super().__init__(**kwargs)

    def set_remote_method(self, parent_app_name=None, parent_model_name=None,
                          app_label=None, model_name=None, field_name=None,
                          foreign_key_app_label=None, foreign_key_model_name=None,
                          search_field=None, object_id=0, **kwargs):
        """
        设置远程搜索
        :param parent_app_name:
        :param parent_model_name:
        :param app_label:
        :param model_name:
        :param field_name:
        :param foreign_key_app_label: 外键的app_name
        :param foreign_key_model_name: 外键的model_name，搜索的model
        :param search_field:单个字段或多个字段
        :param object_id: 父对象id
        :return:
        """
        # self.remote = True
        # self.filter = False
        if isinstance(search_field, str):
            search_field = [search_field, ]

        param = {"app_label": app_label, "model_name": model_name, "field_name": field_name,
                 "foreign_key_app_label": foreign_key_app_label,
                 "foreign_key_model_name": foreign_key_model_name,
                 "search_field": search_field,
                 "object_id": object_id,
                 "search_term": "{{js.getCurrentAttrValue('label')}}",  # label是input输入框中的值
                 "widget_name": "{{js.getCurrentAttrValue('name')}}",
                 "widget_id": "{{js.getCurrentAttrValue('id')}}",
                 }

        url = common.make_url(const.URL_SELECT_SEARCH, param=param)
        self.add_event(event=event.Event(type="input", step=step.Get(url=url, loading=False)))
        return self


class Radio(Widget):
    """
    单选框
    """

    def __init__(self, data=None, value=None, theme=None, direction=None,
                 width=None, height=None, bg=None, border=None,
                 active=None, focus=None, **kwargs):
        if theme is not None:
            self.theme = theme
        if direction is not None:
            self.direction = direction
        kwargs["data"] = data
        kwargs["value"] = value
        kwargs["width"] = width
        kwargs["height"] = height
        kwargs["bg"] = bg
        kwargs["border"] = border
        kwargs["active"] = active
        kwargs["focus"] = focus
        super().__init__(**kwargs)


class Picker(Widget):
    """选择器"""

    def __init__(self, col=None, col_num=None, value=None, border=None,
                 width=None, height=None, **kwargs):
        if col is not None:
            self.col = col
        if col_num is not None:
            self.col_num = col_num
        kwargs["type"] = "picker"
        kwargs["value"] = value
        kwargs["width"] = width
        kwargs["height"] = height
        kwargs["border"] = border
        super().__init__(**kwargs)


class ColorPicker(Widget):
    """
    颜色选择器
    """

    def __init__(self, value=None, **kwargs):
        kwargs["type"] = "color_picker"
        kwargs["value"] = value
        super().__init__(**kwargs)


class TimePicker(Widget):
    """
    时间选择器
    """

    def __init__(self, value=None, format=None, border=None, active=None, focus=None, **kwargs):
        kwargs["type"] = "time_picker"
        kwargs["value"] = value
        kwargs["format"] = format
        kwargs["border"] = border
        kwargs["active"] = active
        kwargs["focus"] = focus
        super().__init__(**kwargs)


class DatePicker(Widget):
    """
    日期选择器
    """

    def __init__(self, value=None, format=None, border=None, active=None, focus=None, **kwargs):
        kwargs["type"] = "date_picker"
        kwargs["value"] = value
        kwargs["format"] = format
        kwargs["border"] = border
        kwargs["active"] = active
        kwargs["focus"] = focus
        super().__init__(**kwargs)


class DateTimePicker(Widget):
    """
    日期时间选择器
    """

    def __init__(self, value=None, format=None, border=None, active=None, focus=None, **kwargs):
        kwargs["type"] = "datetime_picker"
        kwargs["value"] = value
        kwargs["format"] = format
        kwargs["border"] = border
        kwargs["active"] = active
        kwargs["focus"] = focus
        super().__init__(**kwargs)


class Table(Widget):
    """
    表格
    """

    def __init__(self, head=None, row=None, col=None, tree=None, value=None, select_all_value=None,
                 data=None, space_left=None, space_right=None, space_top=None, space_bottom=None,
                 horizontal=None, vertical=None, order_url=None, select=None,
                 height=None, min_height=None, width=None, bg=None, focus=None,
                 active=None, row_border=None, col_border=None, stable=None,
                 **kwargs):
        if head is not None:
            self.head = head
        if row is not None:
            self.row = row
        if col is not None:
            self.col = col
        if tree is not None:
            self.tree = tree
        if select_all_value is not None:
            self.select_all_value = select_all_value
        if order_url is not None:
            self.order_url = order_url
        if select is not None:
            self.select = select
        if row_border is not None:
            if isinstance(row_border, str):
                self.row_border = {"color": row_border}
            else:
                self.row_border = row_border
        if col_border is not None:
            if isinstance(col_border, str):
                self.col_border = {"color": col_border}
            else:
                self.col_border = col_border
        if stable is not None:
            self.stable = stable
        kwargs["data"] = data
        kwargs["value"] = value
        kwargs["space_left"] = space_left
        kwargs["space_right"] = space_right
        kwargs["space_top"] = space_top
        kwargs["space_bottom"] = space_bottom
        kwargs["horizontal"] = horizontal
        kwargs["vertical"] = vertical
        kwargs["height"] = height
        kwargs["min_height"] = min_height
        kwargs["width"] = width
        kwargs["active"] = active
        kwargs["focus"] = focus
        kwargs["bg"] = bg
        super().__init__(**kwargs)

    def render(self):
        dict_data = super().render()
        dict_head = dict_data.get("head", {})
        for k, v in dict_head.items():
            if isinstance(v, bool):
                dict_head[k] = int(v)

        if "select" in dict_data:
            if isinstance(dict_data["select"], (int, bool)):
                if dict_data["select"]:
                    dict_data["select"] = "multiple"
                else:
                    dict_data["select"] = "none"

        return dict_data


class LiteTable(Widget):
    """简化表格"""

    def __init__(self, data=None, row_border=None, col_border=None,
                 width=None, height=None, row_height=None, min_row_height=None,
                 col_width=None, space_left=None, space_right=None, space_top=None, space_bottom=None,
                 horizontal=None, vertical=None, col_horizontal=None, row_vertical=None,
                 merged_cells=None, bg=None, **kwargs):
        if row_border is not None:
            self.row_border = row_border
        if col_border is not None:
            self.col_border = col_border
        if row_height is not None:
            self.row_height = row_height
        if min_row_height is not None:
            self.min_row_height = min_row_height
        if col_width is not None:
            self.col_width = col_width
        if col_horizontal is not None:
            self.col_horizontal = col_horizontal
        if row_vertical is not None:
            self.row_vertical = row_vertical
        if merged_cells is not None:
            self.merged_cells = merged_cells
        kwargs["space_left"] = space_left
        kwargs["space_right"] = space_right
        kwargs["space_top"] = space_top
        kwargs["space_bottom"] = space_bottom
        kwargs["horizontal"] = horizontal
        kwargs["vertical"] = vertical
        kwargs["data"] = data
        kwargs["bg"] = bg
        kwargs["width"] = width
        kwargs["height"] = height
        super().__init__(**kwargs)

    def render(self):
        dict_data = super().render()
        if "width" not in dict_data:
            dict_data["width"] = "100%"

        return dict_data


# class LayoutTable(Widget):
#     """布局表格"""
#
#     def __init__(self, **kwargs):
#         kwargs["type"] = "layout_table"
#         super().__init__(**kwargs)


class Pagination(Widget):
    """
    分页
    """

    def __init__(self, page_count=None, value=None, font=None, border=None, active=None, focus=None, **kwargs):
        if page_count is not None:
            self.page_count = page_count
        kwargs["value"] = value
        kwargs["font"] = font
        kwargs["border"] = border
        kwargs["active"] = active
        kwargs["focus"] = focus
        super().__init__(**kwargs)


class Transfer(Widget):
    """
    穿梭框
    """

    def __init__(self, data=None, value=None, font=None, border=None, active=None, focus=None, **kwargs):
        kwargs["data"] = data
        kwargs["value"] = value
        kwargs["font"] = font
        kwargs["border"] = border
        kwargs["active"] = active
        kwargs["focus"] = focus
        super().__init__(**kwargs)


class Upload(Widget):
    """
    上传
    """

    def __init__(self, multiple=None, accept=None, upload_url=None,
                 title=None, limit=None, size=None, data=None, value=None,
                 section_size=None, resume_url=None, delete_url=None, theme=None,
                 width=None, height=None, readonly=None, disabled=None,
                 **kwargs):
        if multiple is not None:
            self.multiple = multiple
        if accept is not None:
            self.accept = accept
        if upload_url is not None:
            self.upload_url = upload_url
        if title is not None:
            self.title = title
        if limit is not None:
            self.limit = limit
        if size is not None:
            self.size = size
        if section_size is not None:
            self.section_size = section_size
        if resume_url is not None:
            self.resume_url = resume_url
        if delete_url is not None:
            self.delete_url = delete_url
        if theme is not None:
            self.theme = theme
        kwargs["data"] = data
        kwargs["value"] = value
        kwargs["width"] = width or 120
        kwargs["height"] = height or 120
        kwargs["readonly"] = readonly
        kwargs["disabled"] = disabled
        super().__init__(**kwargs)

    def render(self):
        dict_data = super().render()
        if "section_size" in self.__dict__:
            dict_data["resume_url"] = "v_update_file_resume/"
        elif (self.__dict__.get("upload_url", None) is None) and (not self.__dict__.get("resume_url", None)):
            dict_data["upload_url"] = "v_upload_file/"

        # if (self.__dict__.get("limit", 1) > 1) and ("multiple" not in self.__dict__):
        #     dict_data["multiple"] = 1
        # if not self.kwargs.get("delete_url", None):
        # dict_data["delete_url"] = "v_delete_file/"

        if "upload_url" in dict_data:
            dict_data["upload_url"] = dict_data["upload_url"].lstrip("/").lstrip("\\")

        return dict_data


class Cascader(Widget):
    """
    级联选择
    """

    def __init__(self, data=None, value=None, clearable=None, width=None, height=None,
                 filterable=None, border=None, active=None, focus=None, any_level=None,
                 multiple=None, lazy_load_url=None, readonly=None, disabled=None,
                 **kwargs):
        if clearable is not None:
            self.clearable = clearable
        if filterable is not None:
            self.filterable = filterable
        if any_level is not None:
            self.any_level = any_level
        if multiple is not None:
            self.multiple = multiple
        if lazy_load_url is not None:
            self.lazy_load_url = lazy_load_url
        kwargs["data"] = data
        kwargs["value"] = value
        kwargs["width"] = width
        kwargs["height"] = height
        kwargs["readonly"] = readonly
        kwargs["disabled"] = disabled
        kwargs["border"] = border
        kwargs["active"] = active
        kwargs["focus"] = focus
        super().__init__(**kwargs)


# class Steps(Widget):
#     """
#     步骤
#     """
#
#     def __init__(self, **kwargs):
#         kwargs["type"] = "steps"
#         super().__init__(**kwargs)


class Swipe(Widget):
    """滑动块"""

    def __init__(self, **kwargs):
        kwargs["type"] = "swipe"
        super().__init__(**kwargs)


class Carousel(Widget):
    """轮播"""

    def __init__(self, **kwargs):
        kwargs["type"] = "carousel"
        super().__init__(**kwargs)


class Html(Widget):
    """
    动态html
    """

    def __init__(self, data=None, width=None, height=None, **kwargs):
        kwargs["type"] = "html"
        kwargs["data"] = data
        kwargs["width"] = width
        kwargs["height"] = height
        super().__init__(**kwargs)


class Tree(Widget):
    """树"""

    def __init__(self, data=None, value=None, width=None, height=None, min_height=None,
                 max_height=None, bg=None, font=None, sort=None, select=None,
                 edit=None, filterable=None, lazy=None, lazy_load_url=None,
                 opera_url=None, border=None, focus=None, **kwargs):
        if sort is not None:
            self.sort = sort
        if select is not None:
            self.select = select
        if edit is not None:
            self.edit = edit
        if filterable is not None:
            self.filterable = filterable
        if lazy is not None:
            self.lazy = lazy
        if lazy_load_url is not None:
            self.lazy_load_url = lazy_load_url
        if opera_url is not None:
            self.opera_url = opera_url
        kwargs["type"] = "tree"
        kwargs["data"] = data
        kwargs["value"] = value
        kwargs["width"] = width
        kwargs["height"] = height
        kwargs["min_height"] = min_height
        kwargs["max_height"] = max_height
        kwargs["bg"] = bg
        kwargs["font"] = font
        kwargs["border"] = border
        kwargs["focus"] = focus
        super().__init__(**kwargs)

    def render(self):
        dict_data = super().render()
        if "select" in dict_data:
            if isinstance(dict_data["select"], bool) and dict_data["select"]:
                dict_data["select"] = "multiple"

        return dict_data


class Rich(Widget):
    """
    富文本编辑器
    """

    def __init__(self, **kwargs):
        kwargs["type"] = "rich"
        super().__init__(**kwargs)


class Word(Widget):
    """
    word编辑器
    """

    def __init__(self, export_url=None, import_url=None, **kwargs):
        kwargs["type"] = "word"
        kwargs["export_url"] = export_url or const.URL_EXPORT_WORD
        kwargs["import_url"] = import_url or const.URL_IMPORT_WORD
        super().__init__(**kwargs)


class Pdf(Widget):
    """
    pdf展示
    """

    def __init__(self, href=None, **kwargs):
        kwargs["type"] = "pdf"
        kwargs["href"] = href
        super().__init__(**kwargs)


# class Timed(Button):
#     """
#     定时刷新
#     """
#
#     def __init__(self, **kwargs):
#         super().__init__(**kwargs)
#         self.kwargs["type"] = "timed"


class Countdown(Button):
    """倒计时"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.kwargs["type"] = "countdown"


class BackTop(Widget):
    """返回顶部"""

    def __init__(self, **kwargs):
        kwargs["type"] = "back_top"
        super().__init__(**kwargs)


# class Anchor(Widget):
#     def __init__(self, **kwargs):
#         kwargs["type"] = "anchor"
#         super().__init__(**kwargs)


class Video(Widget):
    """
    视频播放
    """

    def __init__(self, **kwargs):
        kwargs["type"] = "video"
        super().__init__(**kwargs)


class Audio(Widget):
    """语音播放"""

    def __init__(self, **kwargs):
        kwargs["type"] = "audio"
        super().__init__(**kwargs)


class Rate(Widget):
    """
    评分（显示五颗星）
    """

    def __init__(self, value=None, number=None, image=None, **kwargs):
        if number is not None:
            self.number = number
        if image is not None:
            self.image = image
        kwargs["value"] = value
        super().__init__(**kwargs)


class Page(Widget):
    """页面"""

    def __init__(self, horizontal=None, children=None, disabled=None, readonly=None,
                 bg=None, scroll=None, min_width=None, min_height=None,
                 zoom=None, **kwargs):
        if horizontal is not None:
            self.horizontal = horizontal

        if children is not None:
            self.children = children

        if zoom is not None:
            self.zoom = zoom

        kwargs["disabled"] = disabled
        kwargs["readonly"] = readonly
        kwargs["bg"] = bg
        kwargs["scroll"] = scroll
        kwargs["min_width"] = min_width
        kwargs["min_height"] = min_height
        super().__init__(**kwargs)

    def render(self):
        dict_data = super().render()
        if "vertical" not in dict_data:
            dict_data["vertical"] = "top"
        return dict_data


class Grid(Widget):
    """布局"""

    def __init__(self, col_num=None, **kwargs):
        kwargs["type"] = "grid"
        if "vertical" not in kwargs:
            kwargs["vertical"] = "top"
        self.col_num = col_num or 1
        super().__init__(**kwargs)
        col = []
        for i in range(0, self.col_num):
            col.append({})

        self.col = col

    def set_col_attr(self, col, horizontal=None, **kwargs):
        """
        设置列属性
        """
        for i in range(len(self.col), col + 1):
            self.col.append({})

        dict_col = self.col[col]
        kwargs["horizontal"] = horizontal
        dict_col.update(kwargs)

    def insert_widget(self, index, widget, col=-1):
        """
        插入组件
        :param index:列表索引
        :param widget:组件或组件列表
        :param col: 列索引，默认等于最后一列
        :return:
        """
        dict_col = self.col[col]
        if isinstance(widget, (tuple, list)):
            for i in range(len(widget) - 1, -1, -1):
                dict_col.setdefault("children", []).insert(index, widget[i])
        elif widget not in [None, "{}"]:
            dict_col.setdefault("children", []).insert(index, widget)

    def append(self, widget, col=-1):
        self.add_widget(widget, col)

    def add_widget(self, widget, col=-1):
        lst_col = self.col
        if not isinstance(lst_col, list):
            lst_col = [{"children": []}]
            col_num = 1
        else:
            col_num = len(lst_col)

        if col > -1:
            for i in range(col_num, col + 1):
                lst_col.append({"children": []})

        dict_col = lst_col[col]
        if isinstance(widget, (tuple, list)):
            dict_col.setdefault("children", []).extend(widget)
        elif widget not in [None, "{}"]:
            dict_col.setdefault("children", []).append(widget)

    def render(self):
        # if "vertical" not in self.__dict__:
        #     self.__dict__["vertical"] = "middle"

        dict_data = super().render()
        if "col_num" in dict_data:
            del dict_data["col_num"]

        percentage = 0
        total = 0
        width_count = 0
        # lst_col = self.kwargs["col"]
        for dict_col in self.col:
            if "width" in dict_col:
                width = dict_col["width"]
                # 只有%
                if isinstance(width, (int, float)):
                    total += width
                elif width.isdigit():
                    total += int(width)
                elif width.find("%") > -1 and width.find("+") < 0 and width.find("-") < 0:
                    percentage += float(width.replace("%", ""))
                else:
                    pass  # 解析公式

                width_count += 1

        default_width = 0
        col_num = len(self.col)
        if col_num > width_count:
            count = col_num - width_count
            if total == 0:
                default_width = "%s%%" % int((100 - percentage) / count)
            elif total > 0:
                default_width = "%s%% - %s" % (int((100 - percentage) / count),
                                               int(total / count))
            else:
                default_width = "%s%%+%s" % (int((100 - percentage) / count),
                                             int(total / count))

        lst_col = []
        for col in self.col:
            dict_col = {}
            bg = self.format_background(col)
            if bg:
                dict_col.setdefault("bg", {}).update(bg)

            for k, v in col.items():
                # k = admin_api.get_short_name(k)
                dict_col[k] = v

            if "width" not in dict_col:
                dict_col["width"] = default_width

            if "vertical" not in dict_col and self.__dict__.get("vertical", None):
                dict_col["vertical"] = self.vertical
                # del dict_data["vertical"]

            if "horizontal" not in dict_col and self.__dict__.get("horizontal", None):
                dict_col["horizontal"] = self.horizontal
                # del dict_data["horizontal"]

            # if "scroll" not in dict_col and self.scroll:
            #     dict_col["scroll"] = self.scroll

            lst_col.append(dict_col)

        dict_data["col"] = lst_col

        if "width" not in dict_data:
            dict_data["width"] = "100%"

        return dict_data


class Panel(Widget):
    """面板"""

    def __init__(self, width=None, height=None, min_height=None, max_height=None,
                 bg=None, children=None, href=None, url=None, horizontal=None,
                 vertical=None, float=None, scroll=None, border=None, loading=None,
                 **kwargs):
        if loading is not None:
            self.loading = loading
        kwargs["width"] = width
        kwargs["height"] = height
        kwargs["min_height"] = min_height
        kwargs["max_height"] = max_height
        kwargs["bg"] = bg
        kwargs["children"] = children
        kwargs["href"] = href
        kwargs["url"] = url
        kwargs["horizontal"] = horizontal
        kwargs["vertical"] = vertical
        kwargs["float"] = float
        kwargs["scroll"] = scroll
        kwargs["border"] = border
        super().__init__(**kwargs)

    def insert_widget(self, index, widget):
        """
        插入组件
        """
        self.__dict__.setdefault("children", [])

        if isinstance(widget, (tuple, list)):
            for i in range(len(widget) - 1, -1, -1):
                self.__dict__["children"].insert(index, widget[i])

        elif widget not in [None, "{}"]:
            self.__dict__["children"].insert(index, widget)

    def insert(self, index, widget):
        self.insert_widget(index, widget)

    def render(self):
        dict_data = super().render()
        if ("url" in dict_data) or ("href" in dict_data):
            if "loading" not in dict_data:
                dict_data["loading"] = 1

        return dict_data


class Menu(Widget):
    """菜单"""

    def __init__(self, data=None, value=None, popup=None, bg=None, font=None,
                 collapse=None, width=None, height=None, direction=None,
                 active=None, focus=None, **kwargs):
        kwargs["type"] = "menu"
        if popup is not None:
            self.popup = popup
        if collapse is not None:
            self.collapse = collapse
        if direction is not None:
            self.direction = direction

        kwargs["data"] = data
        kwargs["value"] = value
        kwargs["bg"] = bg
        kwargs["font"] = font
        kwargs["width"] = width
        kwargs["height"] = height
        kwargs["height"] = height
        kwargs["active"] = active
        kwargs["focus"] = focus
        super().__init__(**kwargs)

    def add_item(self, item):
        data = self.__dict__.get("data", []) or []
        data.append(item)
        self.__dict__["data"] = data


class Group(Widget):
    """分组"""

    def __init__(self, **kwargs):
        kwargs["type"] = "group"
        super().__init__(**kwargs)


class Tabs(Widget):
    def __init__(self, data=None, value=None, tab_width=None, tab_position=None, bg=None,
                 border=None, active=None, focus=None, width=None, height=None, **kwargs):
        if tab_width is not None:
            self.tab_width = tab_width
        if tab_position is not None:
            self.tab_position = tab_position
        kwargs["type"] = "tabs"
        kwargs["data"] = data
        kwargs["value"] = value
        kwargs["bg"] = bg
        kwargs["border"] = border
        kwargs["active"] = active
        kwargs["focus"] = focus
        kwargs["width"] = width
        kwargs["height"] = height
        super().__init__(**kwargs)


class Timeline(Widget):
    def __init__(self, data=None, align=None, width=None, height=None, **kwargs):
        if align is not None:
            self.align = align

        kwargs["type"] = "timeline"
        kwargs["data"] = data
        kwargs["width"] = width
        kwargs["height"] = height
        super().__init__(**kwargs)


class Collapse(Widget):
    def __init__(self, data=None, width=None, height=None, align=None,
                 bg=None, border=None, accordion=None, **kwargs):
        kwargs["type"] = "collapse"
        kwargs["data"] = data
        kwargs["width"] = width
        kwargs["height"] = height
        kwargs["border"] = border
        kwargs["bg"] = bg
        if align is not None:
            self.align = align
        if accordion is not None:
            self.accordion = accordion
        super().__init__(**kwargs)


class Paragraph(Widget):
    """段落,对应word段落"""

    def __init__(self, first_line_indent=None, left_indent=None, right_indent=None, space_before=None,
                 space_after=None, line_spacing=None, line_spacing_rule=None, horizontal=None,
                 **kwargs):
        kwargs["type"] = "paragraph"
        kwargs["children"] = []
        kwargs["first_line_indent"] = first_line_indent
        kwargs["left_indent"] = left_indent
        kwargs["right_indent"] = right_indent
        kwargs["space_before"] = space_before
        kwargs["space_after"] = space_after
        kwargs["line_spacing"] = line_spacing
        kwargs["line_spacing_rule"] = line_spacing_rule
        kwargs["horizontal"] = horizontal
        super().__init__(**kwargs)


class Dropdown(Widget):
    """
    下拉菜单
    """

    def __init__(self, **kwargs):
        kwargs["widget_type"] = "dropdown"
        super().__init__(**kwargs)
        # self.icon = kwargs.get("icon", None)  # 图标
        self.prefix_icon = kwargs.get("prefix_icon", None)  # 图标
        self.title = kwargs["title"]  # 标题
        self.color = kwargs.get("color", None)  # 标题图标颜色
        self.height = kwargs.get("height", None)

    def render(self):
        dict_data = super().render()
        dict_data.update({"title": self.title})

        if self.color is not None:
            dict_data["color"] = self.color

        # if self.icon is not None:
        #     dict_data["icon"] = self.icon

        if self.prefix_icon is not None:
            dict_data["prefix_icon"] = self.prefix_icon

        return dict_data


class Round(Widget):
    """圆,画板上组件"""

    def __init__(self, x=None, y=None, width=None, height=None, icon=None, border=None, **kwargs):
        kwargs["type"] = "round"
        if x is not None:
            kwargs["x"] = x
        if y is not None:
            kwargs["y"] = y
        if width is not None:
            kwargs["width"] = width
        if height is not None:
            kwargs["height"] = height
        if icon is not None:
            if isinstance(icon, str):
                kwargs["icon"] = Icon(icon=icon)
            else:
                kwargs["icon"] = icon
        if border is not None:
            kwargs["border"] = border
        super().__init__(**kwargs)


class Rectangle(Widget):
    """矩形, 画板上组件"""

    def __init__(self, x=None, y=None, width=None, height=None, icon=None, border=None, **kwargs):
        kwargs["type"] = "rectangle"
        if x is not None:
            kwargs["x"] = x
        if y is not None:
            kwargs["y"] = y
        if width is not None:
            kwargs["width"] = width
        if height is not None:
            kwargs["height"] = height
        if icon is not None:
            if isinstance(icon, str):
                kwargs["icon"] = Icon(icon=icon)
            else:
                kwargs["icon"] = icon
        if border is not None:
            kwargs["border"] = border
        super().__init__(**kwargs)


class ConnectLine(Widget):
    """连接线, 画板上组件"""

    def __init__(self, pos=None, icon=None, **kwargs):
        kwargs["type"] = "connect_line"
        if pos is not None:
            kwargs["pos"] = pos
        if icon is not None:
            if isinstance(icon, str):
                kwargs["icon"] = Icon(icon=icon)
            else:
                kwargs["icon"] = icon
        super().__init__(**kwargs)


class Draw(Widget):
    """画板"""

    def __init__(self, width=None, height=None, widget=None, data=None, **kwargs):
        kwargs["type"] = "draw"
        if width is not None:
            kwargs["width"] = width
        if height is not None:
            kwargs["height"] = height
        if widget is not None:
            kwargs["widget"] = widget
        if data is not None:
            kwargs["data"] = data
        super().__init__(**kwargs)


#################################### 自定义组件 #######################################################
# class CustomWidget(object):
#     def __init__(self, **kwargs):
#         self.kwargs = kwargs
#
#     def __setattr__(self, n, v):
#         if n == "kwargs":
#             self.__dict__["kwargs"] = v
#         else:
#             self.kwargs[n] = v
#
#     def __getattr__(self, n):
#         if n == "kwargs":
#             return self.kwargs
#         else:
#             return self.kwargs.get(n, None)
#
#
# class FileUpload(CustomWidget):
#     """文件上传"""
#
#     def __init__(self, **kwargs):
#         super().__init__(**kwargs)
#
#     def render(self):
#         name = self.kwargs["name"]
#         file_type = self.kwargs.get("file_type", "file")
#         multiple = self.kwargs.get("multiple", None)
#         accept = self.kwargs.get("accept", None)
#         limit = self.kwargs.get("limit", None)
#         size = self.kwargs.get("limit", None)
#         width = self.kwargs.get("width", "100%")
#
#         # 上传后要增加表格数据
#         upload = Upload(name=name, multiple=multiple, accept=accept, limit=limit, size=size, progress=True)
#         panel = Panel(width=width)
#         panel.add_widget(upload)
#         panel.add_widget(Row())
#         lst_file = self.kwargs.get("file", [])
#         data = []
#         icon = Icon(icon="el-icon-document", font_size=16)
#         icon_del = Icon(icon="el-icon-delete", font_size=16)
#
#         if file_type == "file":
#             for dict_file in lst_file:
#                 path = dict_file["path"]
#                 name = dict_file.get("name", os.path.split(path))
#                 size = dict_file.get("size", None)
#                 update_time = dict_file.get("update_time", None)
#                 text_name = Text(text=name, step=step.DownloadFile(href=path))
#                 if update_time:
#                     text_time = Text(text="修改日期:%s" % update_time)
#                 else:
#                     text_time = None
#
#                 if size:
#                     text_size = Text(text="大小:%s" % size)
#                 else:
#                     text_size = None
#
#                 data.append(((icon, text_name), (text_time, Row(), text_size), Icon(icon=icon_del)))
#
#             o_table = LiteTable(name="%s-t" % name,
#                                 data=data, width="100%", col_width={0: "40%", 1: "40%", 2: "20%"}, height=60)
#             panel.add_widget(o_table)
#         return panel


# class RadioColor(CustomWidget):
#     """颜色卡片单选"""
#
#     def __init__(self, **kwargs):
#         super().__init__(**kwargs)
#
#     def render(self):
#         name = self.kwargs["name"]
#         data = self.kwargs["data"]
#         width = self.kwargs.get("width", "auto")
#         height = self.kwargs.get("height", "auto")
#         single_width = self.kwargs.get("single_width", 80)
#         value = self.kwargs.get("value", None)
#         # border = self.kwargs.get("border", None)
#         lst_name = []
#         group = Group(name=name, data=[], width=width, height=height, value=value)
#
#         for i, (id_value, color) in enumerate(data):
#             icon_name = "%s_%s_icon" % (name, i)
#             lst_name.append(icon_name)
#
#         for i, (id_value, color) in enumerate(data):
#             button_name = "%s_%s" % (name, i)
#             icon_name = "%s_%s_icon" % (name, i)
#
#             button = Button(bg_color=color, margin_right=10, bind_value=id_value,
#                             width=single_width, height=single_width,
#                             focus={"bg_color": color},
#                             # active_event={"type": "click", "step": o_step_show},
#                             event={"click": [step.WidgetHide(name=lst_name),
#                                              step.WidgetShow(name=icon_name),
#                                              step.WidgetUpdate(data={"name": name, "value": id_value})]},
#                             name=button_name
#                             )
#
#             if value == id_value:
#                 hide = 0
#             else:
#                 hide = 1
#             icon = Icon(name=icon_name, icon="el-icon-success", hide=hide,
#                         float={"top": 10, "right": 10, "related": button_name})
#
#             group.data.append(button)
#             group.data.append(icon)
#
#         return group
#
#         #
#         # # group.data.append()
#         # panel = Panel(width=width, height=height)
#         #
#         # input_type = None
#         # group_name = []
#         # o_step = step.WidgetHide(name=group_name)
#         # script = 'set_attr_value("%s", "value", get_current_attr_value("bind_value"))' % name
#         # o_step_show = [step.WidgetShow(name=group_name), step.RunJs(script=script)]
#         # for (id_value, color) in data:
#         #     button = Button(bg_color=color, margin_right=10, bind_value=id_value,
#         #                     width=single_width, height=single_width,
#         #                     event={"type": "click", "step": o_step},
#         #                     focus={},
#         #                     # active_event={"type": "click", "step": o_step_show},
#         #                     )
#         #
#         #     icon_name = common.allocate_id()
#         #     icon = Icon(name=icon_name, icon="el-icon-success", mergin_top=-30, margin_left=-30)
#         #     group_name.append(icon_name)
#         #     panel.add_widget(button)
#         #     panel.add_widget(icon)
#         #
#         #     if input_type is None:
#         #         if isinstance(id_value, (int, float)):
#         #             input_type = "number"
#         #         else:
#         #             input_type = "text"
#         #
#         # panel.add_widget(Input(name=name, width=0, height=0, input_type=input_type))
#         #
#         # return panel


#
# class Collapse(CustomWidget):
#     """折叠面板"""
#
#     def __init__(self, **kwargs):
#         super().__init__(**kwargs)
#
#     def render(self):
#         data = self.kwargs["data"]
#         width = self.kwargs["width"]
#         height = self.kwargs.get("height", None)
#         position = self.kwargs.get("position", "right")
#
#         title_border = self.kwargs.get("title_border", None)
#         title_bg = self.kwargs.get("title_bg", None)
#         title_height = self.kwargs.get("title_height", 60)
#
#         mutex = ButtonMutex(bg_color="transparent", prefix=Icon(icon="el-icon-arrow-up"),
#                             active_prefix="el-icon-arrow-down")
#         dict_animation = animation.Animation(type="fold").render()
#
#         panel = Panel(width=width, height=height)
#         for dict_item in data:
#             title = dict_item.get("title", None)
#             content = dict_item.get("content", None)
#             expand = dict_item.get("expand", False)
#
#             title_panel = Panel(width=width, height=title_height, bg=title_bg, border=title_border)
#
#             name = common.allocate_id()
#             mutex.event = {"click", step.WidgetHide(name=name, hide=1, animation=dict_animation)}
#             mutex.active_event = {"click": step.WidgetHide(name=name, hide=0, animation=dict_animation)}
#             mutex.value = expand
#             if position == "left":
#                 title_panel.add_widget(mutex.render())
#
#             if isinstance(title, str):
#                 title_panel.add_widget(Text(text=title))
#
#             elif isinstance(title, (Panel, Grid)):
#                 title.width = "90%"
#                 title.bg = {"color": "transparent"}
#                 title.height = title_height
#                 title.scroll = {"scroll": "none"}
#                 title_panel.add_widget(title)
#
#             if position == "right":
#                 title_panel.add_widget(mutex.render())
#
#             sub_panel = Panel(name=name, width=width, hide=not expand)
#             sub_panel.add_widget(content)
#             panel.add_widget(sub_panel)
#             panel.add_widget(Row())
#         return panel

#
# class Tabs(CustomWidget):
#     def __init__(self, **kwargs):
#         super().__init__(**kwargs)
#
#     def render(self):
#         pass
#
#
# class Timeline(CustomWidget):
#     def __init__(self, **kwargs):
#         super().__init__(**kwargs)
#
#     def render(self):
#         if "direction" in self.kwargs:
#             direction = self.kwargs["direction"]
#             del self.kwargs["direction"]
#         else:
#             direction = "right_right"
#
#         item_height = 100
#         data = []
#         col_horizontal = {}
#         def_node = {"type": "button", "border": {"radius": 100}, "width": 15, "height": 15}
#         if direction == "right_right":
#             col_width = {0: 40}
#             col_horizontal = {0: "center"}
#             for item in self.data:
#                 bg_color = random.choice(const.COLOR_RANDOM)
#                 if "node" in item:
#                     node = item["node"]
#                 else:
#                     node = copy.copy(def_node)
#                     node["bg_color"] = bg_color
#
#                 data.append([
#                     [node, Row(), Panel(width=4, height=item_height, bg_color=bg_color)],
#                     [item.get("label", " "), Row(), item.get("content", "")]
#                 ])
#
#         elif direction == "left_left":
#             col_width = {0: "80%", 1: "20%"}
#             for item in self.data:
#                 data.append([
#                     [item.get("label", ""), Row(height=5), item.get("content", "")],
#                     [item.get("node", ""), Row(height=5), Panel(width=5, height="100")]
#                 ])
#         elif direction == "left_right":
#             col_width = {0: "40%", 1: "20%", 2: "40%"}
#             for item in self.data:
#                 data.append([
#                     item.get("label", ""),
#                     [item.get("node", ""), Row(height=5), Panel(width=5, height="100")],
#                     item.get("content", ""),
#                 ])
#         elif direction == "right_left":
#             col_width = {0: "40%", 1: "20%", 2: "40%"}
#             for item in self.data:
#                 data.append([
#                     item.get("content", ""),
#                     [item.get("node", ""), Row(height=5), Panel(width=5, height="100")],
#                     item.get("label", ""),
#                 ])
#         elif direction == "interval":
#             col_width = {0: "40%", 1: "20%", 2: "40%"}
#             for i, item in enumerate(self.data):
#                 if i % 2 == 0:
#                     data.append([
#                         [item.get("label", ""), Row(height=5), item.get("content", "")],
#                         [item.get("node", ""), Row(height=5), Panel(width=5, height="100")],
#                         None,
#                     ])
#                 else:
#                     data.append([
#                         None,
#                         [item.get("node", ""), Row(height=5), Panel(width=5, height="100")],
#                         [item.get("label", ""), Row(height=5), item.get("content", "")],
#                     ])
#         else:
#             raise ValueError("direction参数值错误:%s, 可填值:['top', 'middle', 'bottom']" % direction)
#
#         # self.kwargs["border"] = {"color": "red"}
#         self.kwargs["scroll"] = {"overflow": "auto"}
#         table = LiteTable(**self.kwargs)
#         table.data = data
#         table.col_width = col_width
#         table.col_horizontal = col_horizontal
#         # table.row_height = 100
#
#         return table.render()


class Dropdown(Widget):
    """
    下拉菜单
    """

    def __init__(self, **kwargs):
        kwargs["widget_type"] = "dropdown"
        super().__init__(**kwargs)
        # self.icon = kwargs.get("icon", None)  # 图标
        self.prefix_icon = kwargs.get("prefix_icon", None)  # 图标
        self.title = kwargs["title"]  # 标题
        self.color = kwargs.get("color", None)  # 标题图标颜色
        self.height = kwargs.get("height", None)

    def render(self):
        dict_data = super().render()
        dict_data.update({"title": self.title})

        if self.color is not None:
            dict_data["color"] = self.color

        # if self.icon is not None:
        #     dict_data["icon"] = self.icon

        if self.prefix_icon is not None:
            dict_data["prefix_icon"] = self.prefix_icon

        return dict_data
