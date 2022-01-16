# !/usr/bin/python
# -*- coding=utf-8 -*-
"""
theme
"""
import json


def make_theme_view(request):
    from django.conf import settings
    from vadmin import widgets
    from vadmin import widgets_ex
    from vadmin import step
    from vadmin import animation
    from vadmin import common
    from vadmin import const
    o_theme = get_theme(request.user.id)

    min_height = 60
    left_width = "30%"
    right_width = "70%"
    o_panel = widgets.Panel(width="100%", scroll={"y": "auto"}, horizontal="center")
    table_data = []
    template_value = o_theme.template
    data = []
    for object_id, label in settings.V_STYLE_TEMPLATE:
        data.append((object_id, label))

    table_data.append([widgets.Text(text="主题模板 : "),
                       widgets.Radio(name="template", data=data, value=template_value)])

    dict_style = json.loads(o_theme.style)
    theme_color = o_theme.theme_color
    # skin_color = o_theme.skin_color

    # data = []
    # dict_item = settings.V_STYLE_COLOR.get(template_value, {"color": []})
    # for lst_color in dict_item["color"]:
    #     color = lst_color[0]
    #     if color not in settings.V_STYLE_CONFIG[template_value]:
    #         continue
    #
    #     data.append((color, color))

    # table_data.append([widgets.Text(text="皮肤颜色 : "),
    #                    widgets.RadioColor(name="skin_color", data=data, value=skin_color, single_width=120)])

    dict_base = dict_style.get("base", {})
    if dict_base.get("color_list", []):
        script1 = "showNode(getFirstChildNode(getChildNodeByName(vm, vm.value)))"
        script2 = "for (var vnode of getChildNodes(vm)){hideNode(getFirstChildNode(vnode))}"
        table_data.append([widgets.Text(text="主题颜色 : "),
                           widgets_ex.RadioColor(name="theme_color", data=dict_base["color_list"],
                                                 activate=step.RunJs(script1),
                                                 deactivate=step.RunJs(script2),
                                                 value=dict_base.get("theme_color", theme_color))])
    else:
        table_data.append([widgets.Text(text="主题颜色 : "),
                           widgets.ColorPicker(name="theme_color", value=dict_base.get("theme_color", theme_color))])

    # table_data.append([widgets.Text(text="菜单位置 : "),
    #                    widgets.Radio(name="menu_position", theme="button",
    #                                  data=[("left", u"左侧"), ("top", u"顶部")], value=o_theme.menu_position)])

    table_data.append([widgets.Text(text="顶部背景颜色 : "),
                       widgets.ColorPicker(name="top_bg_color", value=dict_base.get("top_bg_color", "#588DD6"))])

    table_data.append([widgets.Text(text="左侧背景颜色 : "),
                       widgets.ColorPicker(name="left_bg_color", value=dict_base.get("left_bg_color", "#252D33"))])

    dict_button = dict_style.get("button", {"border": {"radius": 2}, "bg": {"color": o_theme.theme_color}})
    o_step_1 = step.Post(url="v_theme_submit/", check_required=True)
    o_step_2 = step.Get(url="v_theme_submit/", submit_type="hide")

    bg_color = dict_button["bg"]["color"]
    font_color = common.calc_black_white_color(bg_color)
    focus_color = common.calc_focus_color(bg_color)
    table_data.append([None, [
        widgets.Row(height=20),
        widgets.Button(text="应用", step=o_step_1, bg_color=bg_color,
                       font_color=font_color, focus_bg_color=focus_color),
        widgets.Col(width=20),
        widgets.Button(text="恢复默认", step=o_step_2, bg_color=bg_color,
                       font_color=font_color, focus_bg_color=focus_color)
    ]])

    merged_cells = ["3-0:3-1"]
    # merged_cells = None
    o_table = widgets.LiteTable(data=table_data, width="100%",
                                col_width={0: "30%"}, min_row_height=60,
                                col_horizontal={0: "right", 1: "left"}, space_left=10, space_right=10,
                                # border={"style": "solid none solid none", "color": "#FF0000", "width": 3}
                                )
    o_panel.add_widget(o_table)

    return o_panel


def make_theme_view_2(request):
    """
    构造主题数据
    """
    from django.conf import settings
    from vadmin import widgets
    from vadmin import step
    from vadmin import animation
    from vadmin import common
    from vadmin import const

    o_theme = get_theme(request.user.id)

    min_height = 60
    left_width = "30%"
    right_width = "70%"
    o_panel = widgets.Panel(width="100%", scroll={"y": "auto"}, horizontal="center")
    o_grid = widgets.Grid(min_height=min_height)
    o_grid.set_col_attr(col=0, width=left_width, horizontal="right")
    o_grid.set_col_attr(col=1, width=right_width)
    o_grid.add_widget(col=0, widget=widgets.Text(text="皮肤模板 : "))
    data = []
    template_value = o_theme.template
    for object_id, label in settings.V_STYLE_TEMPLATE:
        data.append((object_id, label))
    o_grid.add_widget(widget=widgets.Radio(name="template", data=data, value=template_value))
    o_panel.add_widget(o_grid.render())
    o_panel.add_widget(widgets.Row())

    o_grid = widgets.Grid(min_height=min_height)
    o_grid.set_col_attr(col=0, width=left_width, horizontal="right")
    o_grid.set_col_attr(col=1, width=right_width)
    o_grid.add_widget(col=0, widget=widgets.Text(text="皮肤颜色 : "))

    dict_style = json.loads(o_theme.style)
    theme_color = o_theme.theme_color
    skin_color = o_theme.skin_color
    data = []
    dict_item = settings.V_STYLE_COLOR.get(template_value, settings.V_DEFAULT_TEMPLATE)
    # label = dict_item["label"]
    for lst_color in dict_item["color"]:
        color = lst_color[0]
        if color not in settings.V_STYLE_CONFIG[template_value]:
            continue

        data.append((color, color))
    o_grid.add_widget(widget=widgets.RadioColor(name="skin_color", data=data, value=skin_color, single_width=120))
    o_panel.add_widget(o_grid.render())
    o_panel.add_widget(widgets.Row())

    dict_base = dict_style.get("base", {})
    o_grid = widgets.Grid(min_height=min_height)
    o_grid.set_col_attr(col=0, width=left_width, horizontal="right")
    o_grid.set_col_attr(col=1, width=right_width)
    o_grid.add_widget(col=0, widget=widgets.Text(text="主题颜色 : "))
    o_grid.add_widget(widget=widgets.ColorPicker(name="theme_color",
                                                 value=dict_base.get("theme_color", theme_color)))
    o_panel.add_widget(o_grid.render())
    o_panel.add_widget(widgets.Row())

    o_grid = widgets.Grid(min_height=min_height)
    o_grid.set_col_attr(col=0, width=left_width, horizontal="right")
    o_grid.set_col_attr(col=1, width=right_width)
    o_grid.add_widget(col=0, widget=widgets.Text(text="顶部背景颜色 : "))
    o_grid.add_widget(widget=widgets.ColorPicker(name="top_bg_color",
                                                 value=dict_base.get("top_bg_color", "#588DD6")))
    o_panel.add_widget(o_grid.render())
    o_panel.add_widget(widgets.Row())

    o_grid = widgets.Grid(min_height=min_height)
    o_grid.set_col_attr(col=0, width=left_width, horizontal="right")
    o_grid.set_col_attr(col=1, width=right_width)
    o_grid.add_widget(col=0, widget=widgets.Text(text="左侧背景颜色 : "))
    o_grid.add_widget(widget=widgets.ColorPicker(name="left_bg_color",
                                                 value=dict_base.get("left_bg_color", "#252D33")))
    o_panel.add_widget(o_grid.render())
    o_panel.add_widget(widgets.Row())

    o_grid = widgets.Grid(min_height=min_height)
    o_grid.set_col_attr(col=0, width=left_width, horizontal="right")
    o_grid.set_col_attr(col=1, width=right_width)
    o_grid.add_widget(col=0, widget=widgets.Text(text="菜单位置 : "))
    menu_position = o_theme.menu_position
    o_grid.add_widget(widget=widgets.Radio(name="menu_position", theme="button",
                                           data=[("left", u"左侧"), ("top", u"顶部")], value=menu_position,
                                           ))
    o_panel.add_widget(o_grid.render())
    o_panel.add_widget(widgets.Row())

    o_grid = widgets.Grid(min_height=min_height)
    o_grid.set_col_attr(col=0, width=left_width, horizontal="right")
    o_grid.set_col_attr(col=1, width=right_width)
    o_grid.add_widget(col=0, widget=widgets.Text(text="单位 : "))
    unit = dict_base.get("unit", "px")
    o_grid.add_widget(widget=widgets.Radio(name="unit", theme="button",
                                           data=[("px", u"px"), ("pt", u"pt")], value=unit,
                                           ))
    o_panel.add_widget(o_grid.render())
    o_panel.add_widget(widgets.Row())

    o_grid = widgets.Grid(min_height=min_height)
    o_grid.set_col_attr(col=0, width=left_width, horizontal="right")
    o_grid.add_widget(col=0, widget=widgets.Text(text="文字   "))
    o_panel.add_widget(o_grid)
    o_panel.add_widget(widgets.Row())

    dict_font = dict_style.get("font", {"family": "Microsoft YaHei", "size": 14})
    o_grid = widgets.Grid(min_height=min_height)
    o_grid.set_col_attr(col=0, width=left_width, horizontal="right")
    o_grid.set_col_attr(col=1, width=right_width)
    o_grid.add_widget(col=0, widget=widgets.Text(text="字体 : "))
    o_grid.add_widget(widget=widgets.Radio(name="font_family", data=const.FONT_FAMILY,
                                           required=True,
                                           value=dict_font.get("family", "Microsoft YaHei")))
    o_panel.add_widget(o_grid.render())
    o_panel.add_widget(widgets.Row())

    o_grid = widgets.Grid(min_height=min_height)
    o_grid.set_col_attr(col=0, width=left_width, horizontal="right")
    o_grid.set_col_attr(col=1, width=right_width)
    o_grid.add_widget(col=0, widget=widgets.Text(text="字体大小 : "))
    o_grid.add_widget(widget=widgets.Radio(name="font_size", data=[(13, "小"), (14, "较小"),
                                                                   (15, "标准"),
                                                                   (16, "大"), (17, "较大"), (18, "超大")],
                                           required=True,
                                           value=dict_font["size"]))
    o_panel.add_widget(o_grid.render())

    #
    # o_panel.add_widget(widgets.Row(height=30))
    name = "theme_detailed"
    o_panel_sub = widgets.Panel(name=name, width="100%", horizontal="center", height=0)

    # 按钮
    dict_button = dict_style.get("button", {"border": {"radius": 2}, "bg": {"color": o_theme.theme_color}})
    o_grid = widgets.Grid(min_height=min_height)
    o_grid.set_col_attr(col=0, width=left_width, horizontal="right")
    o_grid.add_widget(col=0, widget=widgets.Text(text="{{row.20}}按钮   "))
    o_panel_sub.add_widget(o_grid)

    o_grid = widgets.Grid(min_height=min_height)
    o_grid.set_col_attr(col=0, width=left_width, horizontal="right")
    o_grid.set_col_attr(col=1, width=right_width)
    o_grid.add_widget(col=0, widget=widgets.Text(text="按钮圆角 : "))
    o_grid.add_widget(widget=widgets.Slider(name="button_border_radius", min=0, max=100,
                                            value=dict_button["border"]["radius"]))
    o_panel_sub.add_widget(o_grid.render())

    o_grid = widgets.Grid(min_height=min_height)
    o_grid.set_col_attr(col=0, width=left_width, horizontal="right")
    o_grid.set_col_attr(col=1, width=right_width)
    o_grid.add_widget(col=0, widget=widgets.Text(text="按钮颜色 : "))
    o_grid.add_widget(widget=widgets.ColorPicker(name="button_bg_color", value=dict_button["bg"]["color"]))
    o_panel_sub.add_widget(o_grid)
    # o_panel.add_widget(o_panel_sub)

    # form 表单
    dict_form = dict_style.get("form", {"border": {"radius": 2, "color": o_theme.theme_color},
                                        "focus": {"color": o_theme.theme_color}})
    o_grid = widgets.Grid(min_height=min_height)
    o_grid.set_col_attr(col=0, width=left_width, horizontal="right")
    o_grid.add_widget(col=0, widget=widgets.Text(text="{{row.20}}from表单   "))
    o_panel_sub.add_widget(o_grid)

    o_grid = widgets.Grid(min_height=min_height)
    o_grid.set_col_attr(col=0, width=left_width, horizontal="right")
    o_grid.set_col_attr(col=1, width=right_width)
    o_grid.add_widget(col=0, widget=widgets.Text(text="from表单圆角 : "))
    o_grid.add_widget(widget=widgets.Slider(name="form_border_radius", min=0, max=100,
                                            value=dict_form["border"]["radius"]))
    o_panel_sub.add_widget(o_grid.render())

    o_grid = widgets.Grid(min_height=min_height)
    o_grid.set_col_attr(col=0, width=left_width, horizontal="right")
    o_grid.set_col_attr(col=1, width=right_width)
    o_grid.add_widget(col=0, widget=widgets.Text(text="边框颜色 : "))
    o_grid.add_widget(widget=widgets.ColorPicker(name="form_border_color", value=dict_form["border"]["color"]))
    o_panel_sub.add_widget(o_grid)

    o_grid = widgets.Grid(min_height=min_height)
    o_grid.set_col_attr(col=0, width=left_width, horizontal="right")
    o_grid.set_col_attr(col=1, width=right_width)
    o_grid.add_widget(col=0, widget=widgets.Text(text="边框焦点颜色 : "))
    o_grid.add_widget(widget=widgets.ColorPicker(name="form_focus_color", value=dict_form["focus"]["border_color"]))
    o_panel_sub.add_widget(o_grid)

    o_panel.add_widget(o_panel_sub)

    o_panel.add_widget(widget=widgets.Panel(width="100%", height=1, bg={"color": "#FF0000"}))

    # keyframes = [["0%", {"height": "0"}], ["100%", {"height": "{{js.getChildrenHeight('%s')}}" % name}]]
    show_animation = animation.Animation(type="fold",
                                         change_style={"height": "{{js.getChildrenHeight('%s')}}" % name},
                                         duration="0.3s")

    # keyframes = [["0%", {"height": "{{js.getChildrenHeight('%s')}}" % name}], ["100%", {"height": "0"}]]
    hide_animation = animation.Animation(type="fold",
                                         change_style={"height": 0}, duration="0.3s")

    font_color = common.calc_black_white_color(o_theme.bg_color)
    o_widget = widgets.ButtonMutex(text="更多", active_text="隐藏更多",
                                   prefix=widgets.Icon(icon="el-icon-caret-bottom"),
                                   active_prefix=widgets.Icon(icon="el-icon-caret-top"),
                                   font={"color": font_color},
                                   bg={"color": "transparent"},
                                   focus={"bg_color": "transparent", "font_color": font_color},
                                   margin_top=-5, value=0,

                                   # event={"click": step.WidgetShow(name=name, animation=show_animation)},
                                   # active_event={"click": step.WidgetHide(name=name,
                                   #                                        animation=hide_animation, )}
                                   event={
                                       "click": step.RunAnimation(name=name, animation=show_animation)},
                                   active_event={
                                       "click": step.RunAnimation(name=name, animation=hide_animation)}
                                   )
    o_panel.add_widget(widget=o_widget)
    o_panel.add_widget(widgets.Row(height=30))

    o_step_1 = step.Post(url="v_theme_submit/", check_required=True)
    o_step_2 = step.Get(url="v_theme_submit/", submit_type="hide")
    o_panel_sub = widgets.Panel(width="100%", horizontal="center")

    bg_color = dict_button["bg"]["color"]
    font_color = common.calc_black_white_color(bg_color)
    focus_color = common.calc_focus_color(bg_color)
    o_panel_sub.add_widget([widgets.Button(text="应用", step=o_step_1, bg_color=bg_color,
                                           font_color=font_color, focus_bg_color=focus_color),
                            widgets.Col(width=20),
                            widgets.Button(text="恢复默认", step=o_step_2, bg_color=bg_color,
                                           font_color=font_color, focus_bg_color=focus_color)])
    o_panel.add_widget(o_panel_sub)
    o_panel.add_widget(widgets.Row(height=20))

    return o_panel


def get_theme(user_id=None):
    from django.conf import settings
    # from django.core.cache import cache
    from vadmin.models import ThemeConfig
    # o_theme = cache.get("theme_!@#_%s" % user_id)
    # if o_theme is None:
    if not settings.V_TOP_THEME:  # 不支持修改主题，返回默认
        return get_theme_be_template()

    if user_id is None:
        return get_theme_be_template()

    if not isinstance(user_id, (int, str)):
        user_id = user_id.user.pk

    o_config = ThemeConfig.objects.filter(user_id=user_id).first()
    if o_config is None:
        template = settings.V_DEFAULT_TEMPLATE
        theme_color = settings.V_DEFAULT_THEME_COLOR
        left_color = settings.V_DEFAULT_LEFT_COLOR
        top_color = settings.V_DEFAULT_TOP_COLOR

        if theme_color in settings.V_STYLE_CONFIG[template]:
            dict_style = settings.V_STYLE_CONFIG[template][theme_color]
        else:
            template_data = list(settings.V_STYLE_CONFIG[template].items())[0]
            theme_color = theme_color or template_data[0]
            dict_style = template_data[1]

        dict_style = set_theme(dict_style, theme_color, left_color, top_color)

        try:
            o_config = ThemeConfig.objects.create(user_id=user_id, template=template, color=theme_color,
                                                  style=json.dumps(dict_style, ensure_ascii=False))
        except (BaseException,):
            o_config = ThemeConfig.objects.filter(user_id=user_id).first()
    o_theme = Theme(o_config)
    # cache.set("theme_!@#_%s" % user_id, o_theme)

    return o_theme


def get_theme_be_template(template=None, theme_color=None):
    from vadmin.models import ThemeConfig
    from django.conf import settings
    left_color = top_color = None
    if template is None:
        template = settings.V_DEFAULT_TEMPLATE
        theme_color = settings.V_DEFAULT_THEME_COLOR
        left_color = settings.V_DEFAULT_LEFT_COLOR
        top_color = settings.V_DEFAULT_TOP_COLOR

    if theme_color in settings.V_STYLE_CONFIG[template]:
        dict_style = settings.V_STYLE_CONFIG[template][theme_color]
    else:
        template_data = list(settings.V_STYLE_CONFIG[template].items())[0]
        theme_color = theme_color or template_data[0]
        dict_style = template_data[1]

    dict_style = set_theme(dict_style, theme_color, left_color, top_color)
    dict_style["base"]["title"] = settings.V_TITLE.replace("{{\n}}", "")
    o_config = ThemeConfig(template=template, color=theme_color,
                           style=json.dumps(dict_style, ensure_ascii=False))

    o_theme = Theme(o_config)
    return o_theme


def set_theme(dict_style, theme_color, left_color=None, top_color=None, menu_position=None):
    from vadmin import common
    dict_style.setdefault("base", {})
    dict_style.setdefault("font", {})
    dict_style.setdefault("button", {})
    dict_style.setdefault("icon", {})
    dict_style.setdefault("form", {})
    dict_style.setdefault("table", {})
    dict_style.setdefault("menu", {})
    dict_style["base"]['theme_color'] = theme_color

    if left_color:
        dict_style["base"]["left_bg_color"] = left_color

    if top_color:
        dict_style["base"]["top_bg_color"] = top_color

    if menu_position is None and dict_style["base"].get("menu_position", None):
        pass
    else:
        dict_style["base"]["menu_position"] = menu_position or "left"

    dict_style["button"].setdefault("bg", {})
    dict_style["button"].setdefault("focus", {})
    dict_style["button"]['bg']["color"] = theme_color
    dict_style["button"]['focus']["bg_color"] = common.calc_focus_color(theme_color)
    dict_style["button"]['focus']["font_color"] = common.calc_black_white_color(theme_color)

    dict_style["icon"]["color"] = theme_color

    dict_style["form"].setdefault("focus", {})
    dict_style["form"]["focus"]["border_color"] = theme_color

    dict_style["table"].setdefault("focus", {})
    dict_style["table"]["focus"]["color"] = common.calc_light_color(theme_color)

    dict_style["menu"].setdefault("active", {})
    if dict_style["base"]["left_bg_color"] == theme_color:
        dict_style["menu"]["active"]["line_color"] = common.calc_focus_color(theme_color)
    else:
        dict_style["menu"]["active"]["line_color"] = theme_color

    return dict_style


class Theme(object):
    def __init__(self, o_config):
        from django.conf import settings
        dict_style = json.loads(o_config.style)
        self.template = o_config.template  # 皮肤模板
        self.skin_color = o_config.color  # 皮肤颜色
        self.style = o_config.style
        self.base = dict_style["base"]
        self.theme_color = self.base.get("theme_color", o_config.color)  # 主题颜色
        self.theme_round = self.base.get("theme_round", 0)  # 圆角
        self.event = dict_style.get("event", [])
        self.form = dict_style["form"]
        self.button = dict_style["button"]
        self.table = dict_style.get("table", {})
        self.menu = dict_style.get("menu", {})
        self.font = dict_style["font"]

        self.bg_color = self.base.get("bg_color", "#FFFFFF")
        self.top_bg_color = self.base.get("top_bg_color", self.theme_color)
        self.left_bg_color = self.base.get("left_bg_color", self.theme_color)
        self.right_bg_color = self.base.get("right_bg_color", "#FFFFFF")
        self.title_image = self.base.get("title_image", "")

        if "menu_position" not in self.base:
            self.menu_position = self.base["menu_position"] = settings.V_MENU_POSITION
        else:
            self.menu_position = self.base["menu_position"]


if __name__ == "__main__":
    # calc_gradient_color("#F90505")
    # print(get_inverted_by_gray("#F0F2F5"))
    pass
