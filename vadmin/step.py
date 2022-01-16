#!/usr/bin/python
# -*- coding=utf-8 -*-
import collections
import re


class Step(object):
    def __init__(self, **kwargs):
        if not hasattr(self, "type"):
            try:
                this = self.__class__
                while True:
                    step_type = this.__name__
                    this = this.__base__
                    if this.__name__ == "Step":
                        break

                lst_type = re.findall('[A-Z][^A-Z]*', step_type)
                self.type = "_".join(lst_type).lower()
            except (BaseException,):
                pass

        for k, v in kwargs.items():
            if v is None:
                continue

            setattr(self, k, v)

    def __str__(self):
        return self.render()

    def __repr__(self):
        import json
        from vadmin.json_encoder import Encoder
        dict_data = self.render()
        return json.dumps(dict_data, ensure_ascii=False, cls=Encoder)

    def check_param(self):
        pass

    def format_background(self):
        background = {}
        if "bg_color" in self.__dict__:
            background["color"] = self.__dict__["bg_color"]
            del self.__dict__["bg_color"]
        elif "background_color" in self.__dict__:
            background["color"] = self.__dict__["background_color"]
            del self.__dict__["background_color"]

        if "bg_image" in self.__dict__:
            background["image"] = self.__dict__["bg_image"]
            del self.__dict__["bg_image"]
        elif "background_image" in self.__dict__:
            background["image"] = self.__dict__["background_image"]
            del self.__dict__["background_image"]

        if background:
            self.__dict__.setdefault("bg", {}).update(background)

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
        self.format_background()
        self.check_param()
        dict_data = collections.OrderedDict()
        for k, v in self.__dict__.items():
            if v is None:
                continue

            if k in ["request"]:
                continue

            if isinstance(v, bool):
                v = int(v)

            dict_data[k] = v

        return dict_data


class Request(Step):
    def __init__(self, url=None, href=None, jump=None, submit_type=None, section=None, mothod=None,
                 splice=None, parent=None,
                 new_window=None, cache=None, check_required=None, loading=None, unique=None, **kwargs):
        super().__init__(**kwargs)
        if url is not None:
            self.url = url
        if href is not None:
            self.href = href
        if jump is not None:
            self.jump = jump
        if submit_type is not None:
            self.submit_type = submit_type
        if section is not None:
            self.section = section
        if splice is not None:
            self.splice = splice
        if parent is not None:
            self.parent = parent
        if new_window is not None:
            self.new_window = new_window
        if unique is not None:
            self.unique = unique
        if cache is not None:
            self.cache = cache
        if check_required is not None:
            self.check_required = check_required
        if loading is not None:
            self.loading = loading
        if mothod is not None:
            self.mothod = mothod
        else:
            self.mothod = "post"


class Get(Request):
    def __init__(self, url=None, href=None, jump=None, submit_type=None, section=None,
                 splice=None, new_window=None, cache=None, check_required=None,
                 loading=None, unique=None, change_submit=None, **kwargs):
        super().__init__(**kwargs)
        if url is not None:
            self.url = url
        if href is not None:
            self.href = href
        if jump is not None:
            self.jump = jump

        self.submit_type = submit_type or "hide"
        if section is not None:
            self.section = section
        if splice is not None:
            self.splice = splice
        if new_window is not None:
            self.new_window = new_window
        if unique is not None:
            self.unique = unique
        if cache is not None:
            self.cache = cache
        if check_required is not None:
            self.check_required = check_required
        if loading is not None:
            self.loading = loading
        if change_submit is not None:
            self.change_submit = change_submit

        self.mothod = "get"


class Post(Request):
    pass


class RequestAsync(Step):
    def __init__(self, url=None, cycle=2, max=1800, **kwargs):
        super().__init__(**kwargs)
        self.type = "request_async"
        self.url = url
        self.cycle = cycle
        self.max = max


class RunJs(Step):
    """
    执行js脚本
    """

    def __init__(self, script=None, **kwargs):
        super().__init__(**kwargs)
        self.type = "run_js"
        self.script = script


class RunAnimation(Step):
    """执行动画"""

    def __init__(self, animation=None, **kwargs):
        super().__init__(**kwargs)
        self.type = "run_animation"
        self.animation = animation


class WidgetLoad(Step):
    def __init__(self, data=None, **kwargs):
        super().__init__(**kwargs)
        self.type = "widget_load"
        self.data = data


class WidgetAdd(Step):
    def __init__(self, mode="after", related=None, data=None, **kwargs):
        super().__init__(**kwargs)
        self.type = "widget_add"
        self.mode = mode
        self.related = related
        self.data = data


class WidgetDel(Step):
    def __init__(self, data=None, **kwargs):
        super().__init__(**kwargs)
        self.type = "widget_del"
        self.data = data


class WidgetUpdate(Step):
    def __init__(self, mode="section", data=None, related_id=None, parent_name=None, **kwargs):
        super().__init__(**kwargs)
        self.type = "widget_update"
        self.mode = mode
        self.data = data
        self.related_id = related_id
        self.parent_name = parent_name

    # def check_param(self):
    #     if not self.data:
    #         raise ValueError("widget_update步骤必须有data数据！")


class WidgetOpera(Step):
    def __init__(self, name=None, opera=None, data=None, **kwargs):
        super().__init__(**kwargs)
        self.type = "widget_opera"
        self.name = name
        self.opera = opera
        self.data = data


class WidgetHide(Step):
    def __init__(self, name=None, animation=None, placeholder=True, **kwargs):
        super().__init__(**kwargs)
        self.type = "widget_hide"
        self.name = name
        self.animation = animation
        self.placeholder = placeholder


class WidgetShow(Step):
    def __init__(self, name=None, animation=None, **kwargs):
        super().__init__(**kwargs)
        self.type = "widget_show"
        self.name = name
        self.animation = animation


class LayerPopup(Step):
    def __init__(self, name=None, data=None, top=None, right=None, bottom=None, left=None, related=None,
                 animation=None, timeout=None, modal=None, esc_close=None, click_close=None, mask=None, move=None,
                 title=None, width=None, height=None, bg=None, **kwargs):
        super().__init__(**kwargs)
        self.type = "layer_popup"
        if name is not None:
            self.name = name
        if data is not None:
            self.data = data
        if top is not None:
            self.top = top
        if right is not None:
            self.right = right
        if bottom is not None:
            self.bottom = bottom
        if left is not None:
            self.left = left
        if related is not None:
            self.related = related
        if animation is not None:
            self.animation = animation
        if timeout is not None:
            self.timeout = timeout
        if modal is not None:
            self.modal = modal
        if esc_close is not None:
            self.esc_close = esc_close
        if click_close is not None:
            self.click_close = click_close
        if mask is not None:
            self.mask = mask
        if move is not None:
            self.move = move
        self.title = title
        if width is not None:
            self.width = width
        if height is not None:
            self.height = height
        if bg is not None:
            self.bg = bg

    def render(self):
        from vadmin import widgets
        if (self.title is not None) and isinstance(self.title, str):
            o_panel = widgets.Panel(width="100%", height=50)
            o_panel.append(widgets.Text(text=self.title, margin_left=10))
            o_panel.append(widgets.Icon(height=50, width=50, icon="el-icon-close",
                                        step=LayerClose(),
                                        position="right", margin_right=10))
            self.title = o_panel
        dict_data = super().render()
        return dict_data


class LayerClose(Step):
    def __init__(self, name=None, **kwargs):
        super().__init__(**kwargs)
        self.type = "layer_close"
        self.name = name


class OperaSuccess(Step):
    def __init__(self, data=None, **kwargs):
        super().__init__(**kwargs)
        self.data = data


class OperaFailed(Step):
    def __init__(self, data=None, msg=None, **kwargs):
        super().__init__(**kwargs)
        self.data = data
        self.msg = msg
        if not msg:
            error = list(data.values())[0]
            if isinstance(error, str):
                self.msg = error
            else:
                self.msg = error[0]["error"]


class DownloadFile(Step):
    def __init__(self, href=None, **kwargs):
        super().__init__(**kwargs)
        self.href = href


class AddHide(Step):
    def __init__(self, data=None, **kwargs):
        super().__init__(**kwargs)
        self.data = data


class ViewOpera(Step):
    """
    web操作
    """

    def __init__(self, back=None, forward=None, reload=None, cache=None, **kwargs):
        super().__init__(**kwargs)
        self.back = back
        self.forward = forward
        self.reload = reload
        self.cache = cache


class ChangeTheme(Step):
    """
    修改主题
    """

    def __init__(self, data=None, **kwargs):
        super().__init__(**kwargs)
        self.data = data


# class LocateAnchor(Step):
#     """
#     定位锚点
#     """
#
#     def __init__(self, name=None):
#         super().__init__("locate_anchor")
#         self.step_type = "locate_anchor"
#         self.name = name  # 锚点名称
#
#     def render(self):
#         data = super().render()
#         step_data = {}
#         if self.name:
#             step_data["name"] = self.name
#
#         data["step_data"] = step_data
#         return data


class Call(Step):
    """拨打电话 """

    def __init__(self, phone=None, **kwargs):
        super().__init__(**kwargs)
        self.phone = phone


class Print(Step):
    """打印"""

    pass


class FullScreen(Step):
    """全屏"""

    pass


class ScanCode(Step):
    """扫描二维码"""

    pass


class ExitStep(Step):
    """退出执行步骤"""

    pass


class AnchorPoint(Step):
    """定位锚点"""

    def __init__(self, name=None, **kwargs):
        super().__init__(**kwargs)
        self.name = name


class LoadFile(Step):
    """加载文件"""

    def __init__(self, url=None, **kwargs):
        super().__init__(**kwargs)
        self.url = url


############################################## 前端不用支持部分 #########################################################
class RunScript(Request):
    """
    执行python代码
    """

    def __init__(self, script=None, loading=None, **kwargs):
        super().__init__(**kwargs)
        self.script = script
        self.loading = loading

    def render(self):
        data = super().render()
        script = self.script
        if callable(script):
            url = "v_run/%s.%s/" % (script.__module__, script.__name__)
        else:
            if "?" in script:
                url = "v_run/%s" % script
            else:
                url = "v_run/%s/" % script

        data["url"] = url
        return data


class Msg(Step):
    def __init__(self, text=None, msg_type=None, position=None, **kwargs):
        super().__init__(**kwargs)
        self.text = text
        self.msg_type = msg_type
        self.position = position
        # self.modal = 0
        # self.overlay = 1
        # self.timeout = 5

    # def render(self):
    #     from vadmin import widgets
    #
    #     dict_color = {
    #         "success": "#67C23A",
    #         "warning": "#E6A23C",
    #         "info": "#909399",
    #         "error": "#F56C6C",
    #     }
    #     msg_type = "info"  # success/warning/info/error
    #
    #     bg_color = dict_color[msg_type]
    #     grid = widgets.Grid(col_num=2, bg_color=bg_color, scroll={"style": "none"}, min_height=100, max_height=300)
    #     grid.set_col_attr(col=0, min_width=50, max_width=200)
    #     grid.set_col_attr(col=1, width=200)
    #     grid.add_widget(widgets.Text(text=self.text, font_color="#FFFFFF"), col=0)
    #     grid.add_widget(widgets.Icon(icon="el-icon-close", font_text="#FFFFFF", step=LayerClose()))
    #
    #     # self.type = None
    #     # self.text = None
    #     dict_data = super().render()
    #     dict_data["data"] = grid
    #     position = self.kwargs.get("position", "top")
    #     # o_animation = animation.Animation(type="popup", duration=5, cycles=1)
    #     # if self.position == "top":
    #     #     o_animation.position = [{"top": "0px"}, {"top": "100px"}]
    #     # elif self.position == "top_left":
    #     #     o_animation.position = [{"top": 0, "left": 10}, {"top": 100, "left": 10}]
    #     # # elif self.position == "top_right":
    #     # #     o_animation.position = [{"top": 0, "left": 10}, {"top": 100, "left": 10}]
    #     #
    #     # dict_data["animation"] = o_animation
    #
    #     return dict_data
