# !/usr/bin/python
# -*- coding=utf-8 -*-
import re

import docx
from docx import shared
from docx.enum.dml import MSO_THEME_COLOR_INDEX
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.text import WD_COLOR_INDEX
from docx.opc import constants
from docx.oxml import OxmlElement
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls
from docx.oxml.ns import qn
from docx.oxml.numbering import CT_Num

RE_LOWERCASE = "emsp;+|[0-9a-zA-Z().,`~!@#$%^&*()_+-='/?<>\\|\{}\[\]\" ]+"
# 字体宽度px:cm
DICT_FONT_WIDTH = {
    8: 0.23,  # 小六
    10: 0.26,  # 六号
    12: 0.32,  # 小五
    14: 0.37,  # 五号
    16: 0.42,  # 小四
    18: 0.49,  # 四号
    20: 0.53,  # 小三
    21: 0.56,  # 三号
    24: 0.63,  # 小二
    29: 0.78,  # 二号
    32: 0.85,  # 小一
    34: 0.92,  # 一号
    48: 1.27,  # 一初
    56: 1.48,  # 初号
}

DICT_COLOR_NAME_2_HEX = {
    "black": "#000000",
    "navy": "#000080",
    "darkblue": "#00008b",
    "mediumblue": "#0000cd",
    "blue": "#0000ff",
    "darkgreen": "#006400",
    "green": "#008000",
    "teal": "#008080",
    "darkcyan": "#008b8b",
    "deepskyblue": "#00bfff",
    "darkturquoise": "#00ced1",
    "mediumspringgreen": "#00fa9a",
    "lime": "#00ff00",
    "springgreen": "#00ff7f",
    "aqua": "#00ffff",
    "cyan": "#00ffff",
    "midnightblue": "#191970",
    "dodgerblue": "#1e90ff",
    "lightseagreen": "#20b2aa",
    "forestgreen": "#228b22",
    "seagreen": "#2e8b57",
    "darkslategray": "#2f4f4f",
    "limegreen": "#32cd32",
    "mediumseagreen": "#3cb371",
    "turquoise": "#40e0d0",
    "royalblue": "#4169e1",
    "steelblue": "#4682b4",
    "darkslateblue": "#483d8b",
    "mediumturquoise": "#48d1cc",
    "indigo": "#4b0082",
    "darkolivegreen": "#556b2f",
    "cadetblue": "#5f9ea0",
    "cornflowerblue": "#6495ed",
    "mediumaquamarine": "#66cdaa",
    "dimgray": "#696969",
    "slateblue": "#6a5acd",
    "olivedrab": "#6b8e23",
    "slategray": "#708090",
    "lightslategray": "#778899",
    "mediumslateblue": "#7b68ee",
    "lawngreen": "#7cfc00",
    "chartreuse": "#7fff00",
    "aquamarine": "#7fffd4",
    "maroon": "#800000",
    "purple": "#800080",
    "olive": "#808000",
    "gray": "#808080",
    "skyblue": "#87ceeb",
    "lightskyblue": "#87cefa",
    "blueviolet": "#8a2be2",
    "darkred": "#8b0000",
    "darkmagenta": "#8b008b",
    "saddlebrown": "#8b4513",
    "darkseagreen": "#8fbc8f",
    "lightgreen": "#90ee90",
    "mediumpurple": "#9370db",
    "darkviolet": "#9400d3",
    "palegreen": "#98fb98",
    "darkorchid": "#9932cc",
    "yellowgreen": "#9acd32",
    "sienna": "#a0522d",
    "brown": "#a52a2a",
    "darkgray": "#a9a9a9",
    "lightblue": "#add8e6",
    "greenyellow": "#adff2f",
    "paleturquoise": "#afeeee",
    "lightsteelblue": "#b0c4de",
    "powderblue": "#b0e0e6",
    "firebrick": "#b22222",
    "darkgoldenrod": "#b8860b",
    "mediumorchid": "#ba55d3",
    "rosybrown": "#bc8f8f",
    "darkkhaki": "#bdb76b",
    "silver": "#c0c0c0",
    "mediumvioletred": "#c71585",
    "indianred": "#cd5c5c",
    "peru": "#cd853f",
    "chocolate": "#d2691e",
    "tan": "#d2b48c",
    "lightgray": "#d3d3d3",
    "thistle": "#d8bfd8",
    "orchid": "#da70d6",
    "goldenrod": "#daa520",
    "palevioletred": "#db7093",
    "crimson": "#dc143c",
    "gainsboro": "#dcdcdc",
    "plum": "#dda0dd",
    "burlywood": "#deb887",
    "lightcyan": "#e0ffff",
    "lavender": "#e6e6fa",
    "darksalmon": "#e9967a",
    "violet": "#ee82ee",
    "palegoldenrod": "#eee8aa",
    "lightcoral": "#f08080",
    "khaki": "#f0e68c",
    "aliceblue": "#f0f8ff",
    "honeydew": "#f0fff0",
    "azure": "#f0ffff",
    "sandybrown": "#f4a460",
    "wheat": "#f5deb3",
    "beige": "#f5f5dc",
    "whitesmoke": "#f5f5f5",
    "mintcream": "#f5fffa",
    "ghostwhite": "#f8f8ff",
    "salmon": "#fa8072",
    "antiquewhite": "#faebd7",
    "linen": "#faf0e6",
    "lightgoldenrodyellow": "#fafad2",
    "oldlace": "#fdf5e6",
    "red": "#ff0000",
    "fuchsia": "#ff00ff",
    "magenta": "#ff00ff",
    "deeppink": "#ff1493",
    "orangered": "#ff4500",
    "tomato": "#ff6347",
    "hotpink": "#ff69b4",
    "coral": "#ff7f50",
    "darkorange": "#ff8c00",
    "lightsalmon": "#ffa07a",
    "orange": "#ffa500",
    "lightpink": "#ffb6c1",
    "pink": "#ffc0cb",
    "gold": "#ffd700",
    "peachpuff": "#ffdab9",
    "navajowhite": "#ffdead",
    "moccasin": "#ffe4b5",
    "bisque": "#ffe4c4",
    "mistyrose": "#ffe4e1",
    "blanchedalmond": "#ffebcd",
    "papayawhip": "#ffefd5",
    "lavenderblush": "#fff0f5",
    "seashell": "#fff5ee",
    "cornsilk": "#fff8dc",
    "lemonchiffon": "#fffacd",
    "floralwhite": "#fffaf0",
    "snow": "#fffafa",
    "yellow": "#ffff00",
    "lightyellow": "#ffffe0",
    "ivory": "#fffff0",
    "white": "#ffffff",
}


class UnitApi(object):
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

    @staticmethod
    def pt_2_px(pt):
        return round(pt * 4 / 3.0)

    @staticmethod
    def pt_2_cm(pt):
        """
        磅转换成厘米
        """
        return round(pt * 2.54 / 76, 2)

    @staticmethod
    def pt_2_twips(pt):
        """
        磅转缇
        """
        return round(pt * shared.Length._EMUS_PER_PT, 2)

    @staticmethod
    def px_2_pt(px):
        return round(px * 3 / 4.0, 2)

    @staticmethod
    def cm_2_pt(cm):
        return round(cm * 72.0 / 2.54, 2)

    @staticmethod
    def cm_2_px(cm):
        return UnitApi.pt_2_px(UnitApi.cm_2_pt(cm))

    @staticmethod
    def px_2_mm(px):
        """
        转换成毫米 1lin = 2.54cm = 25.4 mm
        """
        return round(px * 1 / UnitApi.CON_DPI * 25.4, 2)

    @staticmethod
    def px_2_in(px):
        """
        像素转英寸
        """
        return round(px * 1 / UnitApi.CON_DPI, 2)

    @staticmethod
    def px_2_twips(px):
        pt = UnitApi.px_2_pt(px)
        return int(round(pt * shared.Length._EMUS_PER_PT))

    @staticmethod
    def in_2_px(inc):
        """
        英寸转像素
        """
        return round(inc * UnitApi.CON_DPI)

    @staticmethod
    def in_2_pt(inc):
        """
        英寸转磅
        """
        return round(inc * 72.0, 2)

    @staticmethod
    def twips_2_pt(twips):
        """
        缇转磅
        """
        return round(twips / shared.Length._EMUS_PER_PT, 2)

    @staticmethod
    def twips_2_px(twips):
        """
        缇转像素
        """
        return int(round(UnitApi.pt_2_px(twips / shared.Length._EMUS_PER_PT)))

    @staticmethod
    def twips_2_cm(twips):
        """
        缇转厘米
        """
        return twips / shared.Length._EMUS_PER_CM


class FontApi(object):
    """html、word字体互转"""
    dict_doc = {
        "黑体": "SimHei",
        "楷体": "SimKai",
        "新宋体": "NSimSun",
        "宋体": "SimSun",
        "仿宋": "FangSong",
        "仿宋_GB2312": "FangSong_GB2312",
        "楷体_GB2312": "KaiTi_GB2312",
        "扩展宋体": "SimSun-ExtB",
        "微软雅黑": "Microsoft YaHei",
        "新版微软雅黑": "Microsoft YaHei UI",

    }

    dict_html = {
        "SimHei": "黑体",
        "SimKai": "楷体",
        "NSimSun": "新宋体",
        "SimSun": "宋体",
        "FangSong": "仿宋",
        "FangSong_GB2312": "仿宋_GB2312",
        "KaiTi_GB2312": "楷体_GB2312",
        "SimSun-ExtB": "扩展宋体",
        "Microsoft YaHei": "微软雅黑",
        "Microsoft YaHei UI": "新版微软雅黑",
    }

    @staticmethod
    def doc_2_html(family, text=None):
        if family in FontApi.dict_doc:
            return FontApi.dict_doc[family]
        elif family in FontApi.dict_doc.values():
            return family

        if text:
            if re.findall(RE_LOWERCASE, text, re.S):
                return "Calibri"  # word上英文和数字默认字体

        return None

    @staticmethod
    def html_2_doc(family, text=None):
        if family in FontApi.dict_html:
            return FontApi.dict_html[family]
        elif family in FontApi.dict_html.values():
            return family

        if text:
            if re.findall(RE_LOWERCASE, text, re.S):
                return "Calibri (西文正文)"  # word上英文和数字默认字体

        return "宋体"

    # def format_font_family(self, family):
    #     # dict_family = {
    #     #     "黑体": "SimHei",
    #     #     "楷体": "SimKai",
    #     #     "新宋体": "NSimSun",
    #     #     "宋体": "SimSun",
    #     #     "扩展宋体": "SimSun-ExtB",
    #     #     "微软雅黑": "Microsoft YaHei",
    #     #     "新版微软雅黑": "Microsoft YaHei UI",
    #     #     "Calibri": "Calibri",
    #     # }
    #     lst_family = family.split(",")
    #     for s in lst_family:
    #         s = s.replace("'", "").replace('"', "")
    #         if s in dict_html:
    #             return dict_html[s]
    #         elif s in dict_html.values():
    #             return s
    #
    #     # if text:
    #     #     if re.findall(RE_LOWERCASE, text, re.S):
    #     #         return "Calibri"  # word上英文和数字默认字体
    #
    #     return None


class CssStyleApi(object):

    @staticmethod
    def color_idx_2_rgb(color_idx):
        """
        背景颜色格式化
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

    # @staticmethod
    # def style_color_2_hex(color):
    #     """
    #     颜色格式化，css样式颜色转化成十六进制
    #     """
    #     r, g, b = CssStyleApi.style_color_2_rgb(color)
    #     return "%02X%02X%02X" % (r, g, b)

    @staticmethod
    def format_unit(unit, dict_style):
        """格式化单位，将css单位转成px"""
        if isinstance(unit, (int, float)):
            return unit

        elif "h" in unit:
            dict_h = {
                "h1": 28,
                "h2": 24,
                "h3": 19,
                "h4": 16,
                "h5": 13,
                "h6": 12,
            }
            return dict_h[unit]

        elif "px" in unit:
            return round(float(unit.strip().replace("px", "")))

        elif "pt" in unit:
            pt = float(unit.strip().replace("pt", ""))
            return UnitApi.pt_2_px(pt)

        elif "em" in unit:
            if "font-size" in dict_style:
                size = CssStyleApi.format_unit(dict_style["font-size"], dict_style)
                if isinstance(size, int):
                    return round(float(unit.strip().replace("em", "")) * size)

        return unit

    @staticmethod
    def format_color(color):
        color = color.strip().replace(" ", "")
        if color in DICT_COLOR_NAME_2_HEX:
            return DICT_COLOR_NAME_2_HEX[color]

        elif "rgba" in color:
            rgb = color.strip().replace('rgba', '').replace("(", "").replace(")", "").strip().split(",")
            return "#{:0>2}{:0>2}{:0>2}".format(hex(int(rgb[0]))[2:], hex(int(rgb[1]))[2:], hex(int(rgb[2]))[2:])
        elif "rgb" in color:
            rgb = color.strip().replace('rgb', '').replace("(", "").replace(")", "").strip().split(",")
            return "#{:0>2}{:0>2}{:0>2}".format(hex(int(rgb[0]))[2:], hex(int(rgb[1]))[2:], hex(int(rgb[2]))[2:])

        elif "#" in color:
            return color

        elif type(color) in [type([]), type(())]:
            return color

        return "#FFFFFF"

    @staticmethod
    def format_margin_padding(dict_style, key="margin"):
        """将CSS样式转化成vadmin格式"""
        margin = [0, 0, 0, 0]
        top_key = "%s-top" % key
        if top_key in dict_style:
            margin[0] = CssStyleApi.format_unit(dict_style[top_key], dict_style)

        right_key = "%s-right" % key
        if right_key in dict_style:
            margin[1] = CssStyleApi.format_unit(dict_style[right_key], dict_style)

        bottom_key = "%s-bottom" % key
        if bottom_key in dict_style:
            margin[2] = CssStyleApi.format_unit(dict_style[bottom_key], dict_style)

        left_key = "%s-left" % key
        if left_key in dict_style:
            margin[3] = CssStyleApi.format_unit(dict_style[left_key], dict_style)

        if key in dict_style:
            lst_margin = dict_style[key].split(" ")
            margin_len = len(lst_margin)
            if margin_len == 1:
                margin = [CssStyleApi.format_unit(lst_margin[0], dict_style)] * 4
            elif margin_len == 2:
                top_bottom = CssStyleApi.format_unit(lst_margin[0], dict_style)
                left_right = CssStyleApi.format_unit(lst_margin[1], dict_style)
                margin = [top_bottom, left_right, top_bottom, left_right]
            elif margin_len == 3:
                top = CssStyleApi.format_unit(lst_margin[0], dict_style)
                left_right = CssStyleApi.format_unit(lst_margin[1], dict_style)
                bottom = CssStyleApi.format_unit(lst_margin[1], dict_style)
                margin = [top, left_right, bottom, left_right]
        return margin


class DocApi(object):
    """
    生成word api（一般是特殊情况）
    """

    @staticmethod
    def set_list_number_restat(doc, paragraph):
        """
        设置列表重新开始编号（暂不支持多级列表）
        """
        next_num_id = doc.part.numbering_part.element._next_numId
        num = CT_Num.new(next_num_id, 7)
        num.add_lvlOverride(ilvl=0).add_startOverride(1)
        doc.part.numbering_part.element._insert_num(num)

        p = paragraph._p
        pPr = p.get_or_add_pPr()
        numPr = OxmlElement('w:numPr')
        numId = OxmlElement('w:numId')
        numId.set(qn('w:val'), "%s" % next_num_id)
        numPr.append(numId)
        pPr.append(numPr)

    @staticmethod
    def set_row_height(row, height, rule="exact"):
        """
        设置行高
        height:高度,单位:pt
        Returns:

        """
        tr = row._tr
        tr_pr = tr.get_or_add_trPr()
        tr_height = OxmlElement('w:trHeight')
        # pt = UnitChangeApi.px_2_pt(height)
        tr_height.set(qn('w:val'), "%s" % int(height * 20))  # val - 指定行的高度，在二十分之一的点。
        tr_height.set(qn('w:hRule'), rule)
        tr_pr.append(tr_height)

    @staticmethod
    def set_col_width(table, col_idx, width):
        """
        设置行高，由于office和wps要求不一样，所有cell和col都设置
        width:宽度,单位：像素
        Args:
            col_idx: 列索引
            width: 单位是PT
        """
        # inch = UnitChangeApi.px_2_in(width)
        # in_width = shared.Inches(inch)
        for row in table.rows:
            cell = row.cells[col_idx]
            cell.width = shared.Pt(width)

        col = table.columns[col_idx]
        col.width = shared.Pt(width)

    @staticmethod
    def set_table_background_color(table, color):
        """
        设置表格背景色
        """
        # element = parse_xml(r'<w:shd {} w:fill="{}"/>'.format(nsdecls('w'), "%s%s%s" % (hex(r)[2:], hex(g)[2:], hex(b)[2:])))
        # element = parse_xml(r'<w:shd {} w:color="auto" w:fill="{}"/>'.format(nsdecls('w'), "%s%s%s" % (color_int_2_hex(r, g, b))))
        # < w:shd        w:val = "clear"        w:color = "auto"        w:fill = "FF0000" / >
        element = OxmlElement('w:shd')
        element.set(qn('w:w'), "clear")
        element.set(qn('w:color'), "auto")
        element.set(qn('w:fill'), color[1:])
        table._tblPr.append(element)  # 修改单元格颜色

    @staticmethod
    def set_table_padding(table, top, bottom, left, right):
        """
        设置表格padding
        单位pt
        """
        #     < w:tblCellMar >
        #     < w:top        w:w = "57"        w:type = "dxa" / >
        #     < w:left        w:w = "85"        w:type = "dxa" / >
        #     < w:bottom        w:w = "113"        w:type = "dxa" / >
        #     < w:right        w:w = "142"        w:type = "dxa" / >
        # < / w:tblCellMar >
        if top is None:
            top_20_pt = 0
        else:
            top_20_pt = int(round(top * 20))
        element = OxmlElement('w:tblCellMar')
        element_sub = OxmlElement('w:top')
        element_sub.set(qn('w:w'), "%s" % top_20_pt)
        element_sub.set(qn('w:type'), "dxa")
        element.append(element_sub)

        if bottom is None:
            bottom_20_pt = 0
        else:
            bottom_20_pt = int(round(bottom * 20))
        element_sub = OxmlElement('w:bottom')
        element_sub.set(qn('w:w'), "%s" % bottom_20_pt)
        element_sub.set(qn('w:type'), "dxa")
        element.append(element_sub)

        if left is None:
            left_20_pt = 0
        else:
            left_20_pt = int(round(left * 20))
        element_sub = OxmlElement('w:left')
        element_sub.set(qn('w:w'), "%s" % left_20_pt)
        element_sub.set(qn('w:type'), "dxa")
        element.append(element_sub)

        if right is None:
            right_20_pt = 0
        else:
            right_20_pt = int(round(right * 20))
        element_sub = OxmlElement('w:right')
        element_sub.set(qn('w:w'), "%s" % right_20_pt)
        element_sub.set(qn('w:type'), "dxa")
        element.append(element_sub)
        table._tblPr.append(element)

    @staticmethod
    def set_table_width(table, width):
        """
        设置表格宽度
        """
        # element = parse_xml(r'<w:shd {} w:fill="{}"/>'.format(nsdecls('w'), "%s%s%s" % (hex(r)[2:], hex(g)[2:], hex(b)[2:])))
        # element = parse_xml(r'<w:shd {} w:color="auto" w:fill="{}"/>'.format(nsdecls('w'), "%s%s%s" % (color_int_2_hex(r, g, b))))
        # < w:shd        w:val = "clear"        w:color = "auto"        w:fill = "FF0000" / >
        lst_tbl = table._tblPr.xpath("w:tblW")
        if lst_tbl:
            tbl = lst_tbl[0]
            tbl.set(qn('w:type'), "dxa")
            twips = UnitApi.px_2_twips(width)
            s_w = str(round(twips / shared.Length._EMUS_PER_TWIP))
            tbl.set(qn('w:w'), s_w)

    @staticmethod
    def set_cell_padding(cell, top, bottom, left, right):
        """
        设置单元格padding
        单位pt
        """
        # < w:tcMar >
        # < w:top        w:w = "85"        w:type = "dxa" / >
        # < w:left        w:w = "113"        w:type = "dxa" / >
        # < w:bottom        w:w = "170"        w:type = "dxa" / >
        # < w:right        w:w = "198"        w:type = "dxa" / >
        # < / w:tcMar >
        if top is None:
            top_20_pt = 0
        else:
            top_20_pt = int(round(top * 20))
        element = OxmlElement('w:tcMar')
        element_sub = OxmlElement('w:top')
        element_sub.set(qn('w:w'), "%s" % top_20_pt)
        element_sub.set(qn('w:type'), "dxa")
        element.append(element_sub)

        if bottom is None:
            bottom_20_pt = 0
        else:
            bottom_20_pt = int(round(bottom * 20))
        element_sub = OxmlElement('w:bottom')
        element_sub.set(qn('w:w'), "%s" % bottom_20_pt)
        element_sub.set(qn('w:type'), "dxa")
        element.append(element_sub)

        if left is None:
            left_20_pt = 0
        else:
            left_20_pt = int(round(left * 20))
        element_sub = OxmlElement('w:left')
        element_sub.set(qn('w:w'), "%s" % left_20_pt)
        element_sub.set(qn('w:type'), "dxa")
        element.append(element_sub)

        if right is None:
            right_20_pt = 0
        else:
            right_20_pt = int(round(right * 20))
        element_sub = OxmlElement('w:right')
        element_sub.set(qn('w:w'), "%s" % right_20_pt)
        element_sub.set(qn('w:type'), "dxa")
        element.append(element_sub)
        cell._tc.append(element)

    @staticmethod
    def set_table_left_indent(table, size):
        """
        设置表格整体移动
        # < w:tblInd
        # w:w = "210"
        # w:type = "dxa" / >
        size:单位pt
        """
        if size is not None:
            element = OxmlElement('w:tblInd')
            element.set(qn('w:w'), "%s" % int(round(size * 20.0)))
            element.set(qn('w:type'), "dxa")
            table._tblPr.append(element)

    @staticmethod
    def set_cell_background_color(cell, color):
        """
        设置单元格背景色
        """
        if color:
            element = parse_xml(r'<w:shd {} w:fill="{}"/>'.format(nsdecls('w'), color[1:]))
            cell._tc.get_or_add_tcPr().append(element)  # 修改单元格颜色

    @staticmethod
    def get_cell_background_color(cell):
        lst_shd = cell._tc.xpath('./w:tcPr/w:shd')
        if lst_shd:
            element = lst_shd[0]
            fill = element.get(qn("w:fill"))
            return "#%s" % fill

    @staticmethod
    def set_paragraph_background_color(paragraph, color):
        """
        设置段落背景颜色
        """
        element = parse_xml(r'<w:shd {} w:fill="{}"/>'.format(nsdecls('w'), color[1:]))
        paragraph._p.get_or_add_pPr().append(element)

    @staticmethod
    def set_text_background_color(run, color):
        """
        设置文字背景颜色
        """
        element = parse_xml(r'<w:shd {} w:fill="{}"/>'.format(nsdecls('w'), color[1:]))
        run._r.get_or_add_rPr().append(element)

    @staticmethod
    def set_cell_vertical(cell, vertical):
        """
        设置单元格内容垂直对齐方式
        cell:单元格对象
        vertical:center和bottom，默认是居上，不用调用此函数设置
        """
        tc_pr = cell._tc.get_or_add_tcPr()
        element = OxmlElement('w:vAlign')
        element.set(qn('w:val'), "%s" % vertical)
        tc_pr.append(element)

    @staticmethod
    def set_cell_horizontal(cell, horizontal):
        """
        设置单元格内容垂直对齐方式
        cell:单元格对象
        alingment:center和bottom，默认是居上，不用调用此函数设置
        """
        lst_p = cell._tc.xpath("./w:p")
        if lst_p:
            p = lst_p[0]
            element = OxmlElement('w:pPr')
            p.append(element)
            sub = OxmlElement('w:jc')
            sub.set(qn('w:val'), "%s" % horizontal)
            element.append(sub)
        #
        # tc_pr = cell._tc.get_or_add_tcPr()
        # element = OxmlElement('w:vAlign')
        # element.set(qn('w:val'), "%s" % horizontal)
        # tc_pr.append(element)

    @staticmethod
    def get_cell_horizontal(cell):
        horizontal = "left"
        lst_horizontal = cell._tc.xpath("./w:p/w:pPr/w:jc")
        if lst_horizontal:
            horizontal = lst_horizontal[0].val
            if horizontal == WD_TABLE_ALIGNMENT.LEFT:
                horizontal = "left"
            elif horizontal == WD_TABLE_ALIGNMENT.CENTER:
                horizontal = "center"
            elif horizontal == WD_TABLE_ALIGNMENT.RIGHT:
                horizontal = "right"
        return horizontal

    @staticmethod
    def set_text_alingment(paragraph, alingment):
        """
        设置内容水平对齐方式
        paragraph:段落对象
        alingment:center和right和left，默认是居左
        """
        if alingment == "center":
            paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
        elif alingment == "right":
            paragraph.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        else:
            paragraph.alignment = WD_ALIGN_PARAGRAPH.LEFT

    @staticmethod
    def set_line_spacing(paragraph, line_spacing):
        paragraph.paragraph_format.line_spacing = 1.0
        if line_spacing > 1:
            space = (line_spacing - 1.0) / 2.0
            paragraph.paragraph_format.space_after += shared.Pt(space)
            paragraph.paragraph_format.space_before += shared.Pt(space)

    @staticmethod
    def add_hyperlink(paragraph, text, url, dict_style):
        """
        增加链接对象
        """
        src = url.strip()
        src = src.strip("(){}\r\n;")
        # This gets access to the document.xml.rels file and gets a new relation id value
        part = paragraph.part
        r_id = part.relate_to(src, constants.RELATIONSHIP_TYPE.HYPERLINK, is_external=True)

        # Create the w:hyperlink tag and add needed values
        hyperlink = docx.oxml.shared.OxmlElement('w:hyperlink')
        hyperlink.set(docx.oxml.shared.qn('r:id'), r_id)

        # Create a w:r element
        new_run = docx.oxml.shared.OxmlElement('w:r')

        # Create a new w:rPr element
        rPr = docx.oxml.shared.OxmlElement('w:rPr')

        # Join all the xml elements together add add the required text to the w:r element
        new_run.append(rPr)
        new_run.text = text
        hyperlink.append(new_run)

        paragraph._p.append(hyperlink)
        r = paragraph.add_run()
        r._r.append(hyperlink)
        r.font.color.theme_color = MSO_THEME_COLOR_INDEX.HYPERLINK
        r.font.underline = True
        # DocApi.set_text_style(r, [dict_style, ], get_page_style("a"))

        return hyperlink

    @staticmethod
    def delete_paragraph(paragraph):
        """
        删除段落
        Args:
            paragraph:

        Returns:

        """
        p = paragraph._element
        p.getparent().remove(p)
        p._p = p._element = None
