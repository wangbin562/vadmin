# !/usr/bin/python
# -*- coding=utf-8 -*-

"""
# url 中配置方法
url(r'^admin/', include('vadmin.urls', 'admin')),

# 第一个页面请求"vadmin/v_index_view/"在前端固定，如果V_BASE_URL不等于vadmin，在工程url中要增加如下一行
# 可以重写v_index_view函数，重定义登录页面
url(r'^vadmin/v_index_view/$', vadmin_views.v_index_view),
"""
import collections

V_LOGO = ""  # LOGO # 顶部菜单左上角显示图片
V_TITLE = "VAdmin"  # 顶部菜单左上角显示标题
V_URL_BASE = "vadmin/"

V_OPERATION_LOG = True  # 是否记录操作日志
V_CACHE = False  # 是否使用缓存
V_LOGGED_JUMP = True  # 登录超时后，是否跳转到登录页
# V_PRIMARY_KEY_CHAR = False  # 主键是否为字符串（只针对vadmin自带的model)
V_TOP_THEME = False  # 是否在头部显示修改主题图标
V_TOP_UPDATE_PWD = True  # 是否在头部显示修改密码图标
V_TOP_ICON = True  # 是否在头部显示默认图标
V_TOP_HOVER = True  # 顶部菜单是否悬浮

V_MENU_POSITION = "top"  # 菜单显示位置 "left" or "top"

# 密码区域
# 密码加密
V_PWD_ENCRYPT_KEY = "hello,2020,2021,"
# 默认密码，设置后，必需修改后才能登录
# V_DEFAULT_PWD = "123456"
V_DEFAULT_PWD = None
# 最长必须修改密码时间（单位：天）, 如果V_PWD_LONG_DAY配置不等于None, User表中必须有
# update_pwd_time = models.DateTimeField(auto_now_add=True, verbose_name=u"修改密码时间")
# V_PWD_LONG_DAY = 30
# V_PWD_LONG_DAY = None
V_POPUP_ERROR = True  # 是否弹出错误日志信息

# 头部新增项（目前默认有4个），列表或方法，方法参数request
V_TOP_ADD_ITEMS = []
# def V_TOP_ADD_ITEMS(request):

# 首页，可以自定义，可以使用接口
V_INDEX_PAGE = {'label': u'首页', 'icon': 'el-icon-s-home', 'url': 'v_home_view/'}

# 菜单
V_MENU_ITEMS = []

# 默认支持的菜单权限
V_SUPPORT_MENU_PERMISSIONS = []
# 皮肤颜色
skin_color = "#588DD6"
skin_color_black = "#101110"
skin_color_red = "#CC3333"
skin_color_blue = "#108CE0"  # 晴空蓝
skin_color_technology_blue = "#0E2233"  # 科技蓝
skin_color_healthy_green = "#19B955"  # 健康绿

# 主题颜色
theme_color = "#91BB2B"
theme_color_black = "#01DAC3"
theme_color_red = "#CC3333"
theme_color_blue = "#0492F2"  # 晴空蓝
theme_color_technology_blue = "#39A4FF"  # 科技蓝
theme_color_healthy_green = "#19B955"  # 健康绿

# 自定义显示样式
V_DEFAULT_TEMPLATE = "default"  # 模板
# V_DEFAULT_COLOR = skin_color  # 皮肤颜色, 目前支持"基础"、"太空黑"、"政务红"、"晴空蓝"、"科技蓝" 5种
V_DEFAULT_THEME_COLOR = None  # 主题颜色
V_DEFAULT_LEFT_COLOR = None  # 左边区域背景颜色
V_DEFAULT_TOP_COLOR = None  # 顶部区域背景颜色

# ("bootstrap", "bootstrap")
V_STYLE_TEMPLATE = (("default", "基础"), ("material", "material"), ("inspinia", "inspinia"))
V_STYLE_COLOR = {"default":
    {
        "label": "基础",
        "color": ((skin_color, "基础"), (skin_color_black, "太空黑"), (skin_color_red, "政务红"),
                  (skin_color_blue, "晴空蓝"),
                  (skin_color_technology_blue, "科技蓝"), (skin_color_healthy_green, "健康绿"))
    }
}

# 参考模板 http://en.dongwufuli.com/
font_color = "#6F89B1"
V_STYLE_CONFIG = collections.OrderedDict()
from vadmin import common

V_STYLE_CONFIG["default"] = {
    skin_color:  # 基础
        {
            "base":  # 基础配置（后端使用）
                {
                    "theme_color": theme_color,
                    "unit": "px",  # 没有指定的情况下，所有int类型都使用此单位（前端宽高根据这个单位传回来）
                    "menu_position": "top",
                    "bg_color": "#F3F3F4",  # 页面背景颜色
                    "top_bg_color": "#588DD6",  # 头部背景颜色
                    "left_bg_color": "#252D33",  # 左边背景颜色
                    "right_bg_color": "#FFFFFF",  # 右边背景颜色
                    "title_image": "vadmin/img/default/content_image_default.png",  # 头部标题背景图片
                },
            "font":
                {
                    "size": 14,
                    # "family": "Microsoft YaHei",
                    "color": "#6F7986",
                },

            # 图标基础样式，默认等于字体，但不支持family
            "icon":
                {
                    "size": 16,
                    "color": theme_color,
                },

            "disabled_style":
                {
                    "bg_color": "#EEEEEE",
                    "font_color": "#AAAAAA",
                },
            #
            # "placeholder_style":
            #     {
            #         "font_color": "#00FF00",
            #     },
            #
            # "tooltip_style":
            #     {
            #         "font_color": "#FF0000",
            #         "font_size": 20,
            #         "bg_color": "#383838",
            #         "radius": 2,
            #     },

            # 滚动条样式
            # "scroll":
            #     {
            #
            #     },

            # 界面loading样式(暂时不支持）
            # "loading_style":
            #     {
            #         # "bg_color": "#FF0000",  # 背景色
            #         # "opacity": 0.5,  # 透明度
            #         # 动画, 默认等于element UI
            #         # "time_out": 30  # 超时时间（单位秒）
            #         "keyframes": [["0%", {"transform": "rotate(0deg)"}],
            #                       ["100%", {"transform": "rotate(360deg)"}]]
            #     },

            # msg效果（暂时不支持）
            # "msg": {
            #     "border": {"radius": 20},
            #     "font": {"color": "#FFFFFF"},
            #     "info": {},
            #     "warning": {},
            #     "success": {},
            #     "error": {},
            #
            # },

            # 弹出层效果（包括弹出程动画和标题）

            # form表单样式, form表单包括:input、
            "form":
                {
                    "border": {"style": "solid, solid, solid, solid", "color": "#E4EAEC",
                               "weight": "1,1,1,1", "radius": 4},
                    # "active": {"bg_color": "transparent", "border_color": theme_color, "font_color": font_color},
                    "focus": {"bg_color": "transparent", "border_color": theme_color, "font_color": font_color},
                },

            # 按钮样式
            "button":
                {
                    "bg": {"color": theme_color},
                    "font": {"color": "#FFFFFF"},
                    "border": {"style": "none, none, none, none", "radius": 2},
                    "focus": {"bg_color": common.calc_focus_color(theme_color),
                              "font_color": common.calc_black_white_color(theme_color),
                              "animation": {"type": "ripple"}}
                },

            # 表格
            "table":
                {
                    "zebra": ["#F4F8F8", "#FCFDFE"],  # change_list中表格斑马线
                    "focus": {"color": "#F6F1F1"},  # 行焦点颜色
                },

            # 包括常用图标样式
            "menu":
                {
                    "bg": {"color": "#252D33"},
                    # "font": {"color": "#FFFFFF", "size": 14},
                    # "focus": {"line_color": theme_color, "line_width": 3},
                },

            # "animation":  # 默认动画
            #     {
            #         "event": "click,",
            #         "type": "ripple",
            #         "notify": {"type": "translate", "duration": 5, "speed": 3,
            #                    "cycles": 1, "position": [",0", ",50"]},  # 通知动画
            #     },
        },

    skin_color_red:  # 政务红
        {
            "base":  # 基础配置（后端使用）
                {
                    "theme_color": theme_color_red,
                    "unit": "px",  # 没有指定的情况下，所有int类型都使用此单位（前端宽高根据这个单位传回来）
                    "bg_color": "#F3F3F4",  # 页面背景颜色
                    "top_bg_color": "#CC3333",  # 头部背景颜色
                    "left_bg_color": "#FFFFFF",  # 左边背景颜色
                    "right_bg_color": "#FFFFFF",  # 右边背景颜色
                    #
                    "title_image": "vadmin/img/default/content_image_red.png",  # 头部标题背景图片

                },
            "font":
                {
                    "size": 14,
                    # "family": "Microsoft YaHei",
                    "color": "#858585",
                },

            # 图标基础样式，默认等于字体，但不支持family
            # "icon":
            #     {
            #         "size": 16,
            #         "color": "#0088CC",
            #     },
            # 可以不填，使用系统默认
            # "disabled_style":
            #     {
            #         "bg_color": "#eeeeee",
            #         "font_color": "#909399",
            #     },

            # 可以不填，使用系统默认
            # "placeholder_style":
            #     {
            #         "font_color": "#C0C4CC",
            #     },

            # 可以不填，使用系统默认
            # "tooltip_style":
            #     {
            #         "font_color": "#FF0000",
            #         "font_size": 20,
            #         "bg_color": "#383838",
            #         "radius": 2,
            #     },

            # form表单样式, form表单包括:input、
            "form":
                {
                    "border": {"style": "solid, solid, solid, solid", "color": "#E4EAEC",
                               "width": "1,1,1,1", "radius": 4},
                    # "active": {"bg_color": "transparent", "border_color": theme_color, "font_color": font_color},
                    "focus": {"bg_color": "transparent", "border_color": theme_color_red, "font_color": font_color},
                },

            # 按钮样式
            "button":
                {
                    "bg": {"color": theme_color_red},
                    "font": {"color": "#FFFFFF"},
                    "border": {"style": "none, none, none, none", "radius": 2},
                    "focus": {"bg_color": common.calc_focus_color(theme_color_red),
                              "font_color": common.calc_black_white_color(theme_color_red)},
                },

            # 表格
            "table":
                {
                    "zebra": ["#FDFDFD", "#FAF8F8"],  # change_list中表格斑马线
                    "focus": {"color": "#F6F1F1"},  # 行焦点颜色
                }

        },

    skin_color_black:  # 太空黑
        {
            "base":  # 基础配置（后端使用）
                {
                    "theme_color": theme_color_black,
                    "unit": "px",  # 没有指定的情况下，所有int类型都使用此单位（前端宽高根据这个单位传回来）
                    "bg_color": "#2D302F",  # 页面背景颜色
                    "top_bg_color": "#101110",  # 头部背景颜色
                    "left_bg_color": "#212423",  # 左边背景颜色
                    "right_bg_color": "#212423",  # 右边背景颜色
                    "title_image": "vadmin/img/default/content_image_black.png",  # 头部标题背景图片

                },
            "font":
                {
                    "size": 14,
                    # "family": "Microsoft YaHei",
                    "color": "#FFFFFF",
                },
            "icon":
                {
                    "color": "#FFFFFF",
                },
            # form表单样式, form表单包括:input、
            "form":
                {
                    "border": {"style": "solid, solid, solid, solid", "color": "#E4EAEC",
                               "weight": "1,1,1,1", "radius": 4},
                    # "active": {"bg_color": "transparent", "border_color": theme_color, "font_color": font_color},
                    "focus": {"bg_color": "transparent", "border_color": theme_color_black, "font_color": font_color},
                },

            # 按钮样式
            "button":
                {
                    "bg": {"color": theme_color_black},
                    "font": {"color": "#FFFFFF"},
                    "border": {"style": "none, none, none, none", "radius": 2},
                    "focus": {"bg_color": common.calc_focus_color(theme_color_black),
                              "font_color": common.calc_black_white_color(theme_color_black)},
                },

            # 表格
            "table":
                {
                    "zebra": ["#1F2221", "#292C2C"],  # change_list中表格斑马线
                    "focus": {"color": "#F6F1F1"},  # 行焦点颜色
                }

        },
}

theme_color = "#4CAF50"
theme_round = 3
V_STYLE_CONFIG["material"] = {
    theme_color:
        {
            "base":  # 基础配置（后端使用）
                {
                    "theme_color": theme_color,  # 主题颜色
                    "theme_round": theme_round,  # 弧度
                    "unit": "px",  # 没有指定的情况下，所有int类型都使用此单位（前端宽高根据这个单位传回来）
                    "bg_color": "#EEEEEE",  # 页面背景颜色
                    "top_bg_color": "#EEEEEE",  # 头部背景颜色
                    "left_bg_color": "#FFFFFF",  # 左边背景颜色
                    "right_bg_color": "#FFFFFF",  # 右边背景颜色
                    "menu_position": "left",
                    # 可切换的颜色列表
                    "color_list": ["#4CAF50", "#9F39B5", "#00BBD4", "#FF9800", "#F34236", "#E81F63"]
                },
            "font":
                {
                    "size": 14,
                    # "family": "Microsoft YaHei",
                    "color": "#333333",
                },

            # 图标基础样式，默认等于字体，但不支持family
            "icon":
                {
                    "size": 16,
                    "color": theme_color,
                },

            "disabled_style":
                {
                    "bg_color": "#EEEEEE",
                    "font_color": "#AAAAAA",
                },

            # form表单样式, form表单包括:input、
            "form":
                {
                    "border": {"color": "#D2D2D2", "radius": theme_round},
                    # "active": {"bg_color": "transparent", "border_color": theme_color, "font_color": font_color},
                    "focus": {"bg_color": "transparent", "border_color": theme_color, "font_color": font_color},
                },

            # 按钮样式
            "button":
                {
                    "bg": {"color": theme_color},
                    "font": {"color": "#FFFFFF"},
                    "border": {"radius": theme_round, "style": ["none", "none", "box_shadow", "none"]},
                    "focus": {"bg_color": common.calc_focus_color(theme_color),
                              "font_color": common.calc_black_white_color(theme_color),
                              "animation": {"type": "ripple"}}
                },

            # 表格
            "table":
                {
                    "zebra": ["#F9F9F9", "#FFFFFF"],  # change_list中表格斑马线
                    "focus": {"color": common.calc_light_color(theme_color)},  # 行焦点颜色
                },

            # 包括常用图标样式
            "menu":
                {
                    # "bg": {"color": "#588DD6"},
                    "font": {"color": "#3C4858", "size": 14},
                    "hover": {"bg_color": "#EFF0F2", "font_color": "#3C4858"},
                    "focus": {"bg_color": theme_color, "font_color": "#FFFFFF"},
                },

            # "animation":  # 默认动画
            #     {
            #         "event": "click,",
            #         "type": "ripple",
            #         "notify": {"type": "translate", "duration": 5, "speed": 3,
            #                    "cycles": 1, "position": [",0", ",50"]},  # 通知动画
            #     },
        },
}

theme_color = "#19B393"
theme_round = 3
V_STYLE_CONFIG["inspinia"] = {
    theme_color:
        {
            "base":  # 基础配置（后端使用）
                {
                    "theme_color": theme_color,  # 主题颜色
                    "theme_round": theme_round,  # 弧度
                    "unit": "px",  # 没有指定的情况下，所有int类型都使用此单位（前端宽高根据这个单位传回来）
                    "bg_color": "#F3F3F4",  # 页面背景颜色
                    "top_bg_color": "#F3F3F4",  # 头部背景颜色
                    "left_bg_color": "#27384A",  # 左边背景颜色
                    "right_bg_color": "#FFFFFF",  # 右边背景颜色
                    "menu_position": "left",
                },
            "font":
                {
                    "size": 14,
                    "color": "#696B6D",
                },
            # 图标基础样式，默认等于字体，但不支持family
            "icon":
                {
                    "size": 16,
                    "color": theme_color,
                },

            "disabled_style":
                {
                    "bg_color": "#EEEEEE",
                    "font_color": "#AAAAAA",
                },

            # form表单样式, form表单包括:input、
            "form":
                {
                    "border": {"color": "#DDDFE6", "radius": theme_round},
                    # "active": {"bg_color": "transparent", "border_color": theme_color, "font_color": font_color},
                    "focus": {"bg_color": "transparent", "border_color": theme_color, "font_color": font_color},
                },

            # 按钮样式
            "button":
                {
                    "bg": {"color": theme_color},
                    "font": {"color": "#FFFFFF"},
                    "border": {"radius": theme_round, "style": ["none", "none", "box_shadow", "none"], },
                    "focus": {"bg_color": common.calc_focus_color(theme_color),
                              "font_color": common.calc_black_white_color(theme_color),
                              "animation": {"type": "ripple"}}
                },

            # 表格
            "table":
                {
                    "zebra": ["#F9F9F9", "#FFFFFF"],  # change_list中表格斑马线
                    "focus": {"color": common.calc_light_color(theme_color)},  # 行焦点颜色
                },

            # 包括常用图标样式
            "menu":
                {
                    # "bg": {"color": "#588DD6"},
                    "font": {"color": "#FFFFFF", "size": 14},
                    "focus": {"bg_color": theme_color},
                },

            # "animation":  # 默认动画
            #     {
            #         "event": "click,",
            #         "type": "ripple",
            #         "notify": {"type": "translate", "duration": 5, "speed": 3,
            #                    "cycles": 1, "position": [",0", ",50"]},  # 通知动画
            #     },
        },
}
