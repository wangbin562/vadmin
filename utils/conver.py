#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
各单位之间转换
pt (point，磅) 是一个物理长度单位，指的是72分之一英寸
px (pixel，像素)是一个虚拟长度单位，是计算机系统的数字化图像长度单位，如果px要换算成物理长度，
需要指定精度DPI(Dots Per Inch，每英寸像素数)，在扫描打印时一般都有DPI可选。
Windows系统默认是96dpi，Apple系统默认是72dpi。
em是一个相对长度单位，最初是指字母M的宽度，故名em。现指的是字符宽度的倍数，
用法类似百分比，如：0.8em, 1.2em,2em等。通常1em=16px。

Twips（缇，微软喜好的一种蜜汁尺寸）
in（inches 英寸）
mm（毫米）
cm（厘米）
"""

CON_DPI = 96.0  # dpi


def pt_2_px(pt):
    return round(pt * 4.0 / 3.0, 2)


def pt_2_cm(pt):
    """
    磅转换成厘米
    """
    return round(pt * 2.54 / 76, 2)


def pt_2_twips(pt):
    """
    磅转缇
    """
    from docx import shared
    return round(pt * shared.Length._EMUS_PER_PT, 2)


def px_2_pt(px):
    return round(px * 3 / 4.0, 2)


def cm_2_pt(cm):
    return round(cm * 72.0 / 2.54, 2)


def cm_2_px(cm):
    return pt_2_px(cm_2_pt(cm))


def px_2_cm(px):
    """
    转换成厘米 1lin = 2.54cm = 25.4 mm
    """
    return round(px / CON_DPI * 25.4, 2)


def px_2_mm(px):
    """
    转换成毫米 1lin = 2.54cm = 25.4 mm
    """
    return round(px / CON_DPI * 25.4 * 10, 2)


def px_2_in(px):
    """
    像素转英寸 1英寸 = 2.54cm = 25.4 mm
    """
    # from docx import shared
    # pt = px_2_pt(px)
    # return round(pt * shared.Length._EMUS_PER_PT / shared.Length._EMUS_PER_INCH, 2)
    return round(px / CON_DPI, 2)


def px_2_twips(px):
    pt = px_2_pt(px)
    from docx import shared
    return int(round(pt * shared.Length._EMUS_PER_PT))


def in_2_px(inc):
    """
    英寸转像素
    """
    return round(inc * CON_DPI)


def in_2_pt(inc):
    """
    英寸转磅
    """
    return round(inc * 72.0, 2)


def twips_2_pt(twips):
    """
    缇转磅
    """
    from docx import shared
    return round(float(twips) / shared.Length._EMUS_PER_PT, 2)


def twips_2_px(twips):
    """
    缇转像素
    """
    from docx import shared
    r = round(pt_2_px(float(twips) / shared.Length._EMUS_PER_PT), 2)
    if r % 1.0 == 0:
        r = int(r)

    return r


def twips_2_cm(twips):
    """
    缇转厘米
    """
    from docx import shared
    return twips / shared.Length._EMUS_PER_CM


def color_2_rgb(color):
    """
    颜色转rgb
    :param color:颜色格式 #FFFFFF
    :return:
    """
    DICT_COLOR_NAME_2_HEX = {
        "black": "#000000", "navy": "#000080", "darkblue": "#00008b",
        "mediumblue": "#0000cd", "blue": "#0000ff", "darkgreen": "#006400",
        "green": "#008000", "teal": "#008080", "darkcyan": "#008b8b",
        "deepskyblue": "#00bfff", "darkturquoise": "#00ced1", "mediumspringgreen": "#00fa9a",
        "lime": "#00ff00", "springgreen": "#00ff7f", "aqua": "#00ffff",
        "cyan": "#00ffff", "midnightblue": "#191970", "dodgerblue": "#1e90ff",
        "lightseagreen": "#20b2aa", "forestgreen": "#228b22", "seagreen": "#2e8b57",
        "darkslategray": "#2f4f4f", "limegreen": "#32cd32", "mediumseagreen": "#3cb371",
        "turquoise": "#40e0d0", "royalblue": "#4169e1", "steelblue": "#4682b4",
        "darkslateblue": "#483d8b", "mediumturquoise": "#48d1cc", "indigo": "#4b0082",
        "darkolivegreen": "#556b2f", "cadetblue": "#5f9ea0", "cornflowerblue": "#6495ed",
        "mediumaquamarine": "#66cdaa", "dimgray": "#696969", "slateblue": "#6a5acd",
        "olivedrab": "#6b8e23", "slategray": "#708090", "lightslategray": "#778899",
        "mediumslateblue": "#7b68ee", "lawngreen": "#7cfc00", "chartreuse": "#7fff00",
        "aquamarine": "#7fffd4", "maroon": "#800000", "purple": "#800080",
        "olive": "#808000", "gray": "#808080", "skyblue": "#87ceeb",
        "lightskyblue": "#87cefa", "blueviolet": "#8a2be2", "darkred": "#8b0000",
        "darkmagenta": "#8b008b", "saddlebrown": "#8b4513", "darkseagreen": "#8fbc8f",
        "lightgreen": "#90ee90", "mediumpurple": "#9370db", "darkviolet": "#9400d3",
        "palegreen": "#98fb98", "darkorchid": "#9932cc", "yellowgreen": "#9acd32",
        "sienna": "#a0522d", "brown": "#a52a2a", "darkgray": "#a9a9a9",
        "lightblue": "#add8e6", "greenyellow": "#adff2f", "paleturquoise": "#afeeee",
        "lightsteelblue": "#b0c4de", "powderblue": "#b0e0e6", "firebrick": "#b22222",
        "darkgoldenrod": "#b8860b", "mediumorchid": "#ba55d3", "rosybrown": "#bc8f8f",
        "darkkhaki": "#bdb76b", "silver": "#c0c0c0", "mediumvioletred": "#c71585",
        "indianred": "#cd5c5c", "peru": "#cd853f", "chocolate": "#d2691e",
        "tan": "#d2b48c", "lightgray": "#d3d3d3", "thistle": "#d8bfd8",
        "orchid": "#da70d6", "goldenrod": "#daa520", "palevioletred": "#db7093",
        "crimson": "#dc143c", "gainsboro": "#dcdcdc", "plum": "#dda0dd",
        "burlywood": "#deb887", "lightcyan": "#e0ffff", "lavender": "#e6e6fa",
        "darksalmon": "#e9967a", "violet": "#ee82ee", "palegoldenrod": "#eee8aa",
        "lightcoral": "#f08080", "khaki": "#f0e68c", "aliceblue": "#f0f8ff",
        "honeydew": "#f0fff0", "azure": "#f0ffff", "sandybrown": "#f4a460",
        "wheat": "#f5deb3", "beige": "#f5f5dc", "whitesmoke": "#f5f5f5",
        "mintcream": "#f5fffa", "ghostwhite": "#f8f8ff", "salmon": "#fa8072",
        "antiquewhite": "#faebd7", "linen": "#faf0e6", "lightgoldenrodyellow": "#fafad2",
        "oldlace": "#fdf5e6", "red": "#ff0000", "fuchsia": "#ff00ff",
        "magenta": "#ff00ff", "deeppink": "#ff1493", "orangered": "#ff4500",
        "tomato": "#ff6347", "hotpink": "#ff69b4", "coral": "#ff7f50",
        "darkorange": "#ff8c00", "lightsalmon": "#ffa07a", "orange": "#ffa500",
        "lightpink": "#ffb6c1", "pink": "#ffc0cb", "gold": "#ffd700",
        "peachpuff": "#ffdab9", "navajowhite": "#ffdead", "moccasin": "#ffe4b5",
        "bisque": "#ffe4c4", "mistyrose": "#ffe4e1", "blanchedalmond": "#ffebcd",
        "papayawhip": "#ffefd5", "lavenderblush": "#fff0f5", "seashell": "#fff5ee",
        "cornsilk": "#fff8dc", "lemonchiffon": "#fffacd", "floralwhite": "#fffaf0",
        "snow": "#fffafa", "yellow": "#ffff00", "lightyellow": "#ffffe0",
        "ivory": "#fffff0", "white": "#ffffff",
    }
    if color in DICT_COLOR_NAME_2_HEX:
        color = DICT_COLOR_NAME_2_HEX[color]
        return int(color[1:3], 16), int(color[3:5], 16), int(color[5:7], 16)

    elif "rgb" in color:
        rgb = color.strip().replace('rgb', '').replace("(", "").replace(")", "").strip().split(",")
        return int(rgb[0]), int(rgb[1]), int(rgb[2])

    elif "#" in color:
        color = color.strip("# ")
        try:
            return int(color[0:2], 16), int(color[2:4], 16), int(color[4:6], 16)
        except (BaseException,):
            pass

    elif type(color) in [type([]), type(())]:
        return color

    return 0xFF, 0xFF, 0xFF


def calc_2_px(expression, width):
    if isinstance(expression, (int, float)):
        return expression

    # import re
    # o_re = re.search("(.*%)", expression)
    if expression.find("%") > -1:
        script = expression.replace("%", " / 100.0", 1) + " * " + str(width)
        width = round(eval(script))

    return width


def word_color_idx_2_rgb(color_idx):
    from docx.enum.text import WD_COLOR_INDEX
    """
    word背景颜色格式化(word背景是索引，转成具体颜色值）
    """
    # word文字背景颜色只固定几种格式，html可以自定义颜色，需要计算相近的颜色
    dict_color = {
        WD_COLOR_INDEX.WHITE: "#FFFFFF",  # 白色
        WD_COLOR_INDEX.BLACK: "#000000",  # 黑色
        WD_COLOR_INDEX.BLUE: "#0000FF",  # 蓝
        WD_COLOR_INDEX.BRIGHT_GREEN: "#00FF00",  # 鲜绿
        WD_COLOR_INDEX.DARK_BLUE: "#000080",  # 深蓝
        WD_COLOR_INDEX.DARK_RED: "#800000",  # 深红
        WD_COLOR_INDEX.DARK_YELLOW: "#808000",  # 深黄
        WD_COLOR_INDEX.GRAY_25: "#C0C0C0",  # 灰色， 25%
        WD_COLOR_INDEX.GRAY_50: "#808080",  # 灰色， 50%
        WD_COLOR_INDEX.GREEN: "#008000",  # 绿色
        WD_COLOR_INDEX.PINK: "#FF00FF",  # 粉红
        WD_COLOR_INDEX.RED: "#FF0000",  # 红色
        WD_COLOR_INDEX.TEAL: "#008080",  # 青色
        WD_COLOR_INDEX.TURQUOISE: "#00FFFF",  # 青绿
        WD_COLOR_INDEX.VIOLET: "#800080",  # 紫罗兰
        WD_COLOR_INDEX.YELLOW: "#FFFF00",  # 黄色
    }

    return dict_color[color_idx]


def color_2_background_color(color):
    """
    背景颜色格式化
    """
    from docx.enum.text import WD_COLOR_INDEX
    # word文字背景颜色只固定几种格式，html可以自定义颜色，需要计算相近的颜色
    dict_background_color = {
        (255, 255, 255): WD_COLOR_INDEX.WHITE,  # 白色
        (0, 0, 0): WD_COLOR_INDEX.BLACK,  # 黑色
        (0, 0, 255): WD_COLOR_INDEX.BLUE,  # 蓝
        (0, 255, 0): WD_COLOR_INDEX.BRIGHT_GREEN,  # 鲜绿
        (0, 0, 128): WD_COLOR_INDEX.DARK_BLUE,  # 深蓝
        (128, 0, 0): WD_COLOR_INDEX.DARK_RED,  # 深红
        (128, 128, 0): WD_COLOR_INDEX.DARK_YELLOW,  # 深黄
        (192, 192, 192): WD_COLOR_INDEX.GRAY_25,  # 灰色， 25%
        (128, 128, 128): WD_COLOR_INDEX.GRAY_50,  # 灰色， 50%
        (0, 128, 0): WD_COLOR_INDEX.GREEN,  # 绿色
        (255, 0, 255): WD_COLOR_INDEX.PINK,  # 粉红
        (255, 0, 0): WD_COLOR_INDEX.RED,  # 红色
        (0, 128, 128): WD_COLOR_INDEX.TEAL,  # 青色
        (0, 255, 255): WD_COLOR_INDEX.TURQUOISE,  # 青绿
        (128, 0, 128): WD_COLOR_INDEX.VIOLET,  # 紫罗兰
        (255, 255, 0): WD_COLOR_INDEX.YELLOW,  # 黄色
    }

    def to_hsv(c):
        from colorsys import rgb_to_hsv
        """ converts color tuples to floats and then to hsv """
        return rgb_to_hsv(*[x / 255.0 for x in c])  # rgb_to_hsv wants floats!

    def color_dist(c1, c2):
        """ returns the squared euklidian distance between two color vectors in hsv space """
        return sum((a - b) ** 2 for a, b in zip(to_hsv(c1), to_hsv(c2)))

    def min_color_diff(color_to_match, colors):
        """ returns the `(distance, color_name)` with the minimal distance to `colors`"""
        return min(  # overal best is the best match to any color:
            (color_dist(color_to_match, c), i)  # (distance to `test` color, color name)
            for c, i in colors.items())

    r, g, b = color_2_rgb(color)
    if (r, g, b) in dict_background_color:
        return dict_background_color[(r, g, b)]

    del dict_background_color[(255, 255, 255)]  # 删除白色
    value, idx = min_color_diff((r, g, b), dict_background_color)
    return idx


def paragraph_number_2_text(paragraph_symbol, level):
    """level:从0开始"""
    dict_symbol = paragraph_symbol[level]
    if "number" in dict_symbol:
        number = dict_symbol["number"] + 1
    else:
        number = dict_symbol.get('start', 1)

    dict_symbol["number"] = number
    format = dict_symbol["format"]
    lst_format = []
    lst_item = format.split("%")
    for i, item in enumerate(lst_item[1:]):
        item = "%" + item
        if item.count("%s") == 1:
            item = item.replace("%s", lst_item[0] + "%s", 1)
        else:
            item = item.replace("%%%s" % (i + 1), lst_item[0] + "%s", 1)
        lst_format.append(item)

    length = len(lst_format)
    if dict_symbol["type"] == "decimal":
        if length == 1:
            lst_format[0] = lst_format[0] % number
        else:
            for i in range(level + 1):
                lst_format[i] = lst_format[i] % paragraph_symbol[i].get("number", str(i + 1))

        number = "".join(lst_format)

    elif dict_symbol["type"] == "lowerLetter":
        if length == 1:
            number = number_2_letter(number)
            lst_format[0] = lst_format[0] % number
        else:
            for i in range(level + 1):
                if "number" in paragraph_symbol[i]:
                    number = number_2_letter(number)
                else:
                    number = number_2_letter(i + 1)
                lst_format[i] = lst_format[i] % number
        number = "".join(lst_format)

    elif dict_symbol["type"] == "upperLetter":
        if length == 1:
            number = number_2_letter(number).upper()
            lst_format[0] = lst_format[0] % number
        else:
            for i in range(level + 1):
                if "number" in paragraph_symbol[i]:
                    number = number_2_letter(number)
                else:
                    number = number_2_letter(i + 1)
                lst_format[i] = lst_format[i] % number.upper()
        number = "".join(lst_format)

    elif dict_symbol["type"] == "chineseCountingThousand":
        if length == 1:
            number = number_2_chinese(number)
            lst_format[0] = lst_format[0] % number
        else:
            for i in range(level + 1):
                if "number" in paragraph_symbol[i]:
                    number = number_2_chinese(number)
                else:
                    number = number_2_chinese(i + 1)
                lst_format[i] = lst_format[i] % number
        number = "".join(lst_format)

    elif dict_symbol["type"] == "chineseCounting":
        if length == 1:
            number = number_2_chinese(number)
            lst_format[0] = lst_format[0] % number
        else:
            for i in range(level + 1):
                if "number" in paragraph_symbol[i]:
                    number = number_2_chinese(number)
                else:
                    number = number_2_chinese(i + 1)
                lst_format[i] = lst_format[i] % number
        number = "".join(lst_format)

    elif dict_symbol["type"] == "bullet":
        number = dict_symbol["format"]

    else:
        for i in range(length):
            lst_format[i] = lst_format[i] % paragraph_symbol[i].get("number", str(i + 1))

        number = "".join(lst_format)

    if number[-1] != " ":
        number = number + " "

    return number


def paragraph_bullet_word_2_html(paragraph_symbol):
    if paragraph_symbol["type"] == "bullet":
        dict_symbol = {
            "\uf06e": "&#9641",  # 正方形
            "\uf075": "&#9670",  # 菱形
            "\uf06c": "&#10026",  # 圆
            "\uf0d8": "&#10148",  # 箭头
            "\uf0b2": "&#10022",  # 四星
            "\uf0fc": "&#10003",  # 勾
        }

        if paragraph_symbol["format"] in dict_symbol:
            paragraph_symbol["format"] = dict_symbol[paragraph_symbol["format"]]
            paragraph_symbol["id"] = "bullet-%s" % paragraph_symbol["format"]
        else:
            paragraph_symbol["format"] = "&#9733"  # 五星
            paragraph_symbol["id"] = "bullet-%s" % paragraph_symbol["format"]

    else:
        if "%1." in paragraph_symbol["format"]:
            # paragraph_symbol["format"] = "%s."
            paragraph_symbol["id"] = "%s-%s" % (paragraph_symbol["type"], paragraph_symbol["format"])
        elif "" == paragraph_symbol["format"]:
            paragraph_symbol["format"] = "%s"
            paragraph_symbol["id"] = "%s-%s" % (paragraph_symbol["type"], paragraph_symbol["format"])
        else:
            import re
            r = re.search('(%[0-9]*)', paragraph_symbol["format"])
            if r:
                s = r.group()
                paragraph_symbol["format"] = paragraph_symbol["format"].replace(s, "%s")
                paragraph_symbol["id"] = "%s-%s" % (paragraph_symbol["type"], paragraph_symbol["format"])
            else:
                # paragraph_symbol["format"] = "%s"
                paragraph_symbol["id"] = "%s-%s" % (paragraph_symbol["type"], paragraph_symbol["format"])

    return paragraph_symbol


def excel_color_2_rgb(color):
    from openpyxl.styles import colors
    rgb = None
    if color is None:
        rgb = None

    elif color and isinstance(color, str):
        color = color.strip()
        if color.find("#") == 0:
            rgb = color
        else:
            rgb = "#%s" % color

    else:
        if color.type == "theme":
            dict_theme = {
                # 0: {0.0: "FFFFFF", -4.998931: "FFFFFF", -0.149998: "D8D8D8", -0.249977: "BFBFBF", -0.349986: "A5A5A5", 0.499984: "7F7F7F"},
                1: {0.0: "FFFFFF", -4.998931: "FFFFFF", -0.149998: "D8D8D8", -0.249977: "BFBFBF", -0.349986: "A5A5A5",
                    0.499984: "7F7F7F"},
                2: {0.0: "000000", 0.499984: "808080", 0.349986: "5A5A5A", 0.249977: "404040", 0.149998: "272727",
                    4.99893: "0D0D0D"},
                3: {0.0: "EEECE1", -9.997863: "DDD9C3", -0.249977: "C5BE97", -0.499984: "948B54", -0.749992: "4A452A",
                    -0.89999: "1D1B11"},
                4: {0.0: "1F497D", 0.799981: "1F497D", 0.599993: "8DB4E3", 0.399975: "538ED5", -0.249977: "17375D",
                    -0.499984: "0F253F"},
                5: {0.0: "4F81BD", 0.799981: "DBE5F1", 0.599993: "B8CCE4", 0.399975: "95B3D7", -0.249977: "376091",
                    -0.499984: "254061"},
                6: {0.0: "C0504D", 0.799981: "F2DDDC", 0.599993: "E6B9B8", 0.399975: "D99795", -0.249977: "953735",
                    -0.499984: "C0504D"},
                7: {0.0: "9BBB59", 0.799981: "EAF1DD", 0.599993: "D7E4BC", 0.399975: "C2D69A", -0.249977: "75923C",
                    -0.499984: "9BBB59"},
                8: {0.0: "8064A2", 0.799981: "E5E0EC", 0.599993: "CCC0DA", 0.399975: "B2A1C7", -0.249977: "60497B",
                    -0.499984: "8064A2"},
                9: {0.0: "4BACC6", 0.799981: "DBEEF3", 0.599993: "B6DDE8", 0.399975: "93CDDD", -0.249977: "31849B",
                    -0.499984: "4BACC6"},
                10: {0.0: "F79646", 0.799981: "FDE9D9", 0.599993: "FCD5B4", 0.399975: "FAC090", -0.249977: "E46D0A",
                     -0.499984: "F79646"},
            }
            rgb = "#%s" % dict_theme[color.theme + 1].get(round(color.tint, 6), "FFFFFF")

        elif color.type == "indexed":
            if 0 <= color.indexed <= 62:
                rgb = "#%s" % colors.COLOR_INDEX[color.indexed][2:]

        elif color.type == "rgb":
            if color.rgb == "00000000":
                rgb = "#FFFFFF"
            else:
                rgb = "#%s" % color.rgb[2:]

    return rgb


def font_size_2_height(size):
    """字体大小对应字体高度（word显示高度）"""
    default_size = {
        96: 145.6,  # 72
        # 74.67: [77.27, 129], # 56
        64: 104.0,  # 48
        56: 83.2,  # 初号
        48: 83.2,  # 小初    36
        37.33: 62.4,  # 28
        34.67: 62.4,  # 一号    26
        32: 62.4,  # 小一
        29.33: 41.6,  # 二号    22
        26.67: 41.6,  # 20
        24: 41.6,  # 小二    18
        21.33: 41.6,  # 三号    16
        20: 41.6,  # 小三
        18.67: 41.6,  # 四号    14
        16: 41.6,  # 小四    12
        14.67: 20.8,  # 11
        14: 20.8,  # 五号    10.5
        13.33: 20.8,  # 10
        12: 20.8,  # 小五    9
        10.67: 20.8,  # 8
        10: 20.8,  # 六号    7.5
        8.67: 20.8,  # 小六    6.5
        7.33: 20.8,  # 七号    5.5
        6.67: 20.8,  # 八号    5
    }

    return default_size.get(size, 20.8)


def number_2_letter(number):
    import math
    dict_c = {
        "1": "a", "2": "b",
        "3": "c", "4": "d",
        "5": "e", "6": "f",
        "7": "g", "8": "h",
        "9": "i", "10": "j",
        "11": "k", "12": "l",
        "13": "m", "14": "n",
        "15": "o", "16": "p",
        "17": "q", "18": "r",
        "19": "s", "20": "t",
        "21": "u", "22": "v",
        "23": "w", "24": "x",
        "25": "y", "26": "z",
    }
    n = math.floor(number / 26)
    k = number % 26 or 1
    v = dict_c[str(k)]
    return n * v + v


def number_2_chinese(number):
    """数字转中文，不包含小数（最大支持到万）"""

    dict_c = {
        "0": "零",
        "1": "一",
        "2": "二",
        "3": "三",
        "4": "四",
        "5": "五",
        "6": "六",
        "7": "七",
        "8": "八",
        "9": "九",
    }

    dict_d = {
        2: "十",
        3: "百",
        4: "千",
        5: "万",
        # 6: "百万",
        # 7: "千万",
        # 8: "亿",
        # 9: "十亿",
        # 10: "百亿",
        # 11: "千亿",
    }

    s = str(int(number))
    length = len(s)
    lst_result = []
    prev = None
    for i in range(0, length):
        char = s[i]
        if char == "0":
            if int(s[i:]) == 0:
                pass
            elif prev != "0":
                lst_result.append("零")
        else:
            n = length - i
            if n in dict_d:
                lst_result.append(dict_c[char] + dict_d[n])
            elif char in dict_c:
                lst_result.append(dict_c[char])

        prev = char

    if len(lst_result) == 1 or len(lst_result) == 2:
        if lst_result[0] == "一十":
            lst_result[0] = "十"

    return "".join(lst_result)


if __name__ == "__main__":
    pass
