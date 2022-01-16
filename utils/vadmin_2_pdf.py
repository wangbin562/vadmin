# !/usr/bin/python
# -*- coding=utf-8 -*-
"""
"""
import copy
import json
import math
import os

from reportlab.lib import colors
from reportlab.lib import fonts
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Paragraph, SimpleDocTemplate, Table, Spacer, Image

from utils import word_api

try:
    pdfmetrics.registerFont(TTFont('simsun', 'utils/fonts/SIMSUN.TTC'))
    pdfmetrics.registerFont(TTFont('simsun-italic', 'utils/fonts/SIMSUN_ITALIC_100W.ttf'))
    pdfmetrics.registerFont(TTFont('simsun-bold', 'utils/fonts/SIMHEI.TTF'))
    pdfmetrics.registerFont(TTFont('simsun-italic-bold', 'utils/fonts/SIMSUN_ITALIC_500W.ttf'))
except (BaseException,):
    pdfmetrics.registerFont(TTFont('simsun', 'fonts/SIMSUN.TTC'))
    pdfmetrics.registerFont(TTFont('simsun-italic', 'fonts/SIMSUN_ITALIC_100W.ttf'))
    pdfmetrics.registerFont(TTFont('simsun-bold', 'fonts/SIMHEI.TTF'))
    pdfmetrics.registerFont(TTFont('simsun-italic-bold', 'fonts/SIMSUN_ITALIC_500W.ttf'))

fonts.addMapping('simsun', 0, 0, 'simsun')
fonts.addMapping('simsun', 0, 1, 'simsun-italic')  # italic
fonts.addMapping('simsun', 1, 0, 'simsun-bold')  # bold
fonts.addMapping('simsun', 1, 1, 'simsun-italic-bold')  # italic and bold


class Compiler(object):
    def __init__(self, pdf_path, **kwargs):
        self.lst_paragraph = []
        self.paragraph = None
        self.style = None
        self.dict_style = getSampleStyleSheet()
        self.lst_text = []
        self.prev_node = None
        self.next_node = None
        self.pdf_path = pdf_path
        self.base_path = os.path.split(self.pdf_path)[0]
        self.img_idx = -1

        self.page_width = kwargs.get("page_width", None)
        self.page_height = kwargs.get("page_height", None)
        self.left_margin = kwargs.get("left_margin", 0)
        self.right_margin = kwargs.get("left_margin", 0)
        self.top_margin = kwargs.get("top_margin", 0)
        self.bottom_margin = kwargs.get("bottom_margin", 0)
        self.content_width = self.page_width - self.left_margin - self.right_margin

        self.lst_anchor_name = kwargs.get("lst_anchor_name", 0)

    def get_text_style(self, dict_widget):
        dict_font = {}
        lst_before = []
        lst_after = []

        # 获取字体
        font = dict_widget.get("font", {})

        # 文字大小
        if "size" in font:
            size = font["size"]
            dict_font['size'] = size
            # if (1.3 * size) > self.style.leading:
            #     self.style.leading = 1.3 * size

            if size > self.style.fontSize:
                self.style.fontSize = size

        # if dict_widget.get("line_height"):
        #     if dict_widget["line_height"] > self.style.leading:
        #         self.style.leading = dict_widget["line_height"]

        # 文字颜色
        color = font.get("color", None)
        if color is not None:
            dict_font['color'] = font["color"]

        # 背景颜色
        bg = dict_widget.get("bg", {})
        if "color" in bg:
            dict_font["backColor"] = bg["color"]

        # 文字划线
        decoration = font.get("decoration", None)
        if decoration is not None:
            # 下划线
            if decoration == "underline":
                lst_before.insert(0, "<u>")
                lst_after.append("</u>")

            # 删除线
            elif decoration == "line-through":
                lst_before.insert(0, "<strike>")
                lst_after.append("</strike>")

            # 上划线
            elif decoration == "overline":
                pass

        # 粗体
        weight = font.get("weight", None)
        if weight == "bold":
            lst_before.insert(0, "<b>")
            lst_after.append("</b>")

        # 斜体
        style = font.get("style", None)
        if style in ["italic", "oblique"]:
            lst_before.insert(0, "<i>")
            lst_after.append("</i>")

        # 锚点
        o_step = self.paragraph.get("step", None) or dict_widget.get("step", None)
        if o_step:
            if o_step.type == "anchor_point":
                # 规避格式错误 http://baike.baidu.com/item/%E9%BB%91%E7%9B%92%E6%B5%8B%E8%AF%95/934030" \t "_blank
                name = o_step.name.strip()
                if name in self.lst_anchor_name:
                    name = o_step.name.strip().split(" ")[0]
                    name = name.strip().strip('"\'')
                    lst_before.insert(0, '<link href="#%s">' % name)
                    lst_after.append("</link>")
            else:
                pass

        if dict_widget.get("name"):
            name = dict_widget["name"]
            name = name.strip().strip('"\'')
            lst_before.insert(0, '<a name="%s"/>' % name)

        if dict_font and lst_before:
            return "<font %s>%s" % (" ".join(["%s=%s" % (k, v) for k, v in dict_font.items()]),
                                    "".join(lst_before)), "%s</font>" % "".join(lst_after)

        elif dict_font:
            return "<font %s>%s" % (" ".join(["%s=%s" % (k, v) for k, v in dict_font.items()]),
                                    "".join(lst_before)), "</font>"

        elif lst_before:
            return "".join(lst_before), "".join(lst_after)

        return "", ""

    def get_paragraph_style(self, node):
        self.style = self.dict_style['Normal']
        self.style.fontName = 'simsun'
        # height = node.get("height", None) or node.get("min_height", 0)
        # self.style.leading = height
        dict_font = node.get("font", {})
        font_size = dict_font.get("size", 16)
        self.style.fontSize = font_size

        horizontal = node.get("horizontal", None)
        if horizontal == "left":
            self.style.alignment = 0
        elif horizontal == "right":
            self.style.alignment = 2
        elif horizontal == "center":
            self.style.alignment = 1
        else:
            self.style.alignment = 0

        self.style.firstLineIndent = node.get("first_line_indent", 0)
        self.style.leftIndent = node.get("left_indent", 0)
        self.style.rightIndent = node.get("right_indent", 0)
        self.style.spaceBefore = node.get("space_before", 0)
        self.style.spaceAfter = node.get("space_after", 0)

        if node.get("line_spacing_rule") or node.get("line_spacing", None):
            self.style.leading = word_api.get_paragraph_line_height(node.line_spacing_rule, node.line_spacing,
                                                                    font_size)
        else:
            height = node.get("height", None) or node.get("min_height", 0)
            self.style.leading = height

        return self.style

    def get_table_col_width(self, dict_table):
        data = dict_table.get("data", [])
        if data:
            col_num = len(data[0])
        else:
            col_num = 0

        lst_width = []
        col_width = dict_table["col_width"]
        if col_width:
            width = sum(col_width.values())
            content_width = self.page_width - self.left_margin - self.right_margin
            default_width = content_width / col_num
            keys = col_width.keys()
            key_num = len(keys)
            if key_num < col_num:
                if content_width > width:
                    default_width = (content_width - width) / (col_num - key_num)

            for i in range(0, col_num):
                if i in col_width:
                    lst_width.append(col_width[i])
                else:
                    lst_width.append(default_width)
        else:
            lst_width = [None] * col_num

        return lst_width

    def get_table_row_height(self, dict_table):
        data = dict_table.get("data", [])
        if data:
            row_num = len(data)
        else:
            row_num = 0

        lst_height = []
        row_height = dict_table["row_height"] or dict_table["min_row_height"]
        if row_height:
            for i in range(0, row_num):
                if i in row_height:
                    lst_height.append(row_height[i])
                else:
                    lst_height.append(0)
        else:
            lst_height = [0] * row_num

        return lst_height

    def get_table_horizontal(self, dict_table, table_data):
        def set_table_data_horizontal(row, col, h2='left'):
            if h2 == "left":
                alignment = 0
            elif h2 == "right":
                alignment = 2
            elif h2 == "center":
                alignment = 1
            else:
                alignment = 0

            row_data = table_data[row]
            cell_data = row_data[col]
            for c in cell_data:
                if hasattr(c, "style"):
                    c.style.alignment = alignment

        data = dict_table.get("data", [])
        if data:
            row_num = len(data)
            col_num = len(data[0])
        else:
            row_num = 0
            col_num = 0

        horizontal = dict_table.get("horizontal", None)
        col_horizontal = dict_table.get("col_horizontal", {})
        cell_horizontal = dict_table.get("cell_horizontal", {})

        result = []
        for row_idx in range(row_num):
            for col_idx in range(col_num):
                k = "%s-%s" % (row_idx, col_idx)
                if k in cell_horizontal:
                    v = cell_horizontal[k]
                    result.append(('ALIGN', (col_idx, row_idx), (col_idx, row_idx), v.upper()))
                    set_table_data_horizontal(row_idx, col_idx, v)

                elif col_idx in col_horizontal:
                    v = col_horizontal[col_idx]
                    result.append(('ALIGN', (col_idx, row_idx), (col_idx, row_idx), v.upper()))
                    set_table_data_horizontal(row_idx, col_idx, v)

                elif horizontal:
                    v = horizontal
                    result.append(('ALIGN', (col_idx, row_idx), (col_idx, row_idx), v.upper()))
                    set_table_data_horizontal(row_idx, col_idx, v)

                else:
                    v = 'left'
                    result.append(('ALIGN', (col_idx, row_idx), (col_idx, row_idx), v.upper()))
                    set_table_data_horizontal(row_idx, col_idx, v)

        return result

    def get_table_vertical(self, dict_table):
        data = dict_table.get("data", [])
        if data:
            row_num = len(data)
            col_num = len(data[0])
        else:
            row_num = 0
            col_num = 0

        vertical = dict_table.get("vertical", None)
        row_vertical = dict_table.get("row_vertical", {})
        cell_vertical = dict_table.get("cell_vertical", {})
        result = []

        for row_idx in range(row_num):
            for col_idx in range(col_num):
                k = "%s-%s" % (row_idx, col_idx)
                if k in cell_vertical:
                    v = cell_vertical[k]
                    result.append(('VALIGN', (col_idx, row_idx), (col_idx, row_idx), v.upper()))
                    # set_table_data_horizontal(row_idx, col_idx, v)

                elif row_idx in row_vertical:
                    v = row_vertical[col_idx]
                    result.append(('VALIGN', (col_idx, row_idx), (col_idx, row_idx), v.upper()))

                elif vertical:
                    v = vertical
                    result.vertical(('VALIGN', (col_idx, row_idx), (col_idx, row_idx), v.upper()))

                else:
                    v = 'top'
                    result.append(('VALIGN', (col_idx, row_idx), (col_idx, row_idx), v.upper()))

        return result

    def get_table_merge(self, dict_table):
        result = []
        for merged_cell in dict_table.get("merged_cells", []):
            begin, end = merged_cell.split(":")
            begin_row, begin_col = begin.split("-")
            end_row, end_col = end.split("-")
            begin_row = int(begin_row)
            begin_col = int(begin_col)
            end_row = int(end_row)
            end_col = int(end_col)
            result.append(('SPAN', (begin_col, begin_row), (end_col, end_row)))
        return result

    def write(self, lst_node, lst_paragraph):
        count = len(lst_node)
        for i, node in enumerate(lst_node):
            if not node:
                continue

            widget_type = node.get("type", None)
            if widget_type == "paragraph":
                self.paragraph = node
                self.style = self.get_paragraph_style(node)
                children = node.get("children", [])
                if children:
                    widget = children[- 1]
                    if widget.type == "text":
                        text = widget.text.strip()
                        if text == "":
                            width = node.get("first_line_indent", 0)
                            width += node.get("left_indent", 0)
                            width = word_api.get_paragraph_space_pos(node, width)
                            if width > self.content_width:
                                remainder = width % self.content_width
                                font_size = widget.get("font", {}).get("size") or node.get("font", {}).get("size", 16)
                                num = math.floor(remainder / (font_size / 2.0))
                                children[- 1].text = widget.text[0:num * -1]
                else:
                    children.append({"type": "text", "text": " "})

                self.write(children, lst_paragraph)
                if node.get("line_spacing_rule") or node.get("line_spacing", None):
                    self.style.leading = word_api.get_paragraph_line_height(node.line_spacing_rule,
                                                                            node.line_spacing,
                                                                            self.style.fontSize)
                self.add_paragraph(lst_paragraph)

            # elif widget_type == "panel":
            #     self.style = self.get_paragraph_style(node)
            #     children = node.get("children", [])
            #     if children:
            #         self.write(children, lst_paragraph)
            #     elif self.style and self.style.leading > 0:
            #         p = Spacer(0, self.style.leading)
            #         lst_paragraph.append(p)
            #         self.lst_text = []

            elif widget_type == "text":
                if (i == 0) and (not node.get("name", None)):
                    node["name"] = self.paragraph.get("name")
                self.prev_node = node
                self.write_text(node)

            elif widget_type == "image":
                # self.add_paragraph(lst_paragraph)
                self.write_image(node, lst_paragraph)
                # self.style = self.get_paragraph_style(node)

            elif widget_type == "row":
                self.prev_node = None
                self.add_paragraph(lst_paragraph)
                p = Spacer(0, node.get("height", 0))
                lst_paragraph.append(p)
                self.style = self.get_paragraph_style(node)

            elif widget_type == "col":
                if node.get("width"):
                    text = "&nbsp;" * round(node["width"] / 5)  # 5是测试经验值
                    self.lst_text.append(text)

            elif widget_type in ["input", "date", "datetime", "time"]:
                if self.prev_node is None:
                    if (i + 1) < count:
                        self.next_node = lst_node[i + 1]
                self.write_form(node)

            elif widget_type == "lite_table":
                self.write_table(node, lst_paragraph)
            else:
                print(widget_type)

    def write_text(self, dict_widget):
        text = dict_widget.get("text", None) or dict_widget.get("value", "")
        text = str(text)
        # print(text)

        text = text.replace("\r\n", "\n").replace("\r", "\n").replace("\n", "<br/>")
        text = text.replace(" ", "&nbsp;").replace("\t", "&nbsp;&nbsp;&nbsp;&nbsp;")
        before, after = self.get_text_style(dict_widget)
        if dict_widget.get("inline", True):
            text = "%s%s%s" % (before, text, after)
        else:
            text = "<br/>%s%s%s" % (before, text, after)

        self.lst_text.append(text)

        bg = dict_widget.get("bg", {})
        if "image" in bg:
            dict_attr = dict()
            dict_attr["width"] = dict_widget.get("width")
            dict_attr["height"] = dict_widget.get("height")
            dict_attr["valign"] = '"middle"'
            dict_attr["src"] = '"%s"' % bg["image"]
            text = '<font>&nbsp;<img %s/></font>' % " ".join(["%s=%s" % (k, v) for k, v in dict_attr.items()])
            self.lst_text.append(text)

    def write_form(self, dict_widget):
        text = dict_widget.get("value", "")
        text = str(text)
        text = text.replace("\r\n", "\n").replace("\r", "\n").replace("\n", "<br/>")
        try:
            if text.find("{") == 0:
                dict_w = eval(text)
                if dict_w["type"]:
                    self.write_text(dict_w)
                    return
        except (BaseException,):
            pass

        text = text.replace(" ", "&nbsp;").replace("\t", "&nbsp;&nbsp;&nbsp;&nbsp;")
        if not text:
            text = "&nbsp;&nbsp;&nbsp;&nbsp;"
        else:
            text = "&nbsp;%s&nbsp;" % text

        if self.prev_node:
            before, after = self.get_text_style(self.prev_node)
        elif self.next_node:
            before, after = self.get_text_style(self.next_node)
        else:
            before, after = self.get_text_style(dict_widget)

        text = "%s%s%s" % (before, text, after)
        self.lst_text.append(text)

    def write_image(self, dict_widget, lst_paragraph):
        dict_attr = dict()
        width = dict_widget["width"]
        height = dict_widget["height"]
        if width and isinstance(width, (int, float)):
            dict_attr["width"] = width
        if height and isinstance(height, (int, float)):
            dict_attr["height"] = height
            # self.style.leading = height + 20  # 图片上下各空一点

        data = dict_widget["data"]
        if data:
            self.img_idx += 1
            img_path = os.path.join(self.base_path, "img_%s.jpg" % self.img_idx)
            open(img_path, "wb").write(data)
            dict_attr["src"] = '"%s"' % img_path

            # "baseline", "sub", "super",
            # "top", "text-top", "middle", "bottom", "text-bottom"
            float1 = dict_widget["float"]
            if float1:
                dict_attr["valign"] = '"text-top"'
                text = '<font>&nbsp;<img %s/></font>' % " ".join(["%s=%s" % (k, v) for k, v in dict_attr.items()])
                self.lst_text.append(text)
            else:
                image = Image(img_path, width, height)
                # image._offs_x = float1["left"]
                # image._offs_y = float1["top"]
                lst_paragraph.append(image)

    def write_table(self, dict_table, lst_paragraph):
        data = dict_table.get("data", [])
        table_data = []
        for row_idx, row_data in enumerate(data):
            row = []
            for col_idx, cell_data in enumerate(row_data):
                if not isinstance(cell_data, list):
                    cell_data = [cell_data]

                self.lst_text = []
                lst_p = []
                self.write(cell_data, lst_p)
                row.append(lst_p)
            table_data.append(row)

        style = [
            ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black),
            ('BOX', (0, 0), (-1, -1), 0.25, colors.black),
        ]

        result = self.get_table_vertical(dict_table)
        style.extend(result)
        result = self.get_table_horizontal(dict_table, table_data)
        # result = [('ALIGN', (0, 0), (0, 0), 'LEFT'), ('ALIGN', (0, 1), (0, 1), 'RIGHT')]
        style.extend(result)
        result = self.get_table_merge(dict_table)
        style.extend(result)

        lst_width = self.get_table_col_width(dict_table)
        lst_height = self.get_table_row_height(dict_table)
        t = Table(table_data, colWidths=lst_width, minRowHeights=lst_height, style=style)
        lst_paragraph.append(t)

    def add_paragraph(self, lst_paragraph):
        # if self.lst_text:
        #     self.style.backColor = "#FF00FF"
        #     self.style.spaceAfter = 100
        #     is_image = False
        #     for text in self.lst_text:
        #         if text.find("<img") > -1:
        #             is_image = True
        #             break
        #
        #     if is_image:
        #         leading = self.style.font_size * 1.3
        #         self.style.spaceAfter = ((self.style.leading - leading) + 2) or 2
        #         self.style.leading = leading
        #     else:
        #         leading = self.style.font_size * 1.3  # Paragraph无法上下居中，变通处理
        #         if self.style.leading > leading:
        #             space = (self.style.leading - leading) / 2
        #             self.style.leading = leading
        #             self.style.spaceAfter = space
        #             self.style.spaceBefore = space
        #             pass
        #         else:
        #             self.style.leading = leading

        p = Paragraph("".join(self.lst_text), copy.deepcopy(self.style))
        lst_paragraph.append(p)
        self.lst_text = []
        self.style = None

    def to_pdf(self, title=None):
        if title is None:
            title = os.path.splitext(os.path.split(self.pdf_path)[1])[0]
        pdf = SimpleDocTemplate(self.pdf_path, title=title)
        pdf.topMargin = self.top_margin
        pdf.bottomMargin = self.bottom_margin
        pdf.leftMargin = (self.left_margin - 10) or 0
        # pdf.leftMargin = self.left_margin
        pdf.rightMargin = (self.right_margin - 10) or 0
        # pdf.rightMargin = self.right_margin
        if self.page_width and self.page_height:
            pdf.pagesize = [self.page_width, self.page_height]

        pdf.multiBuild(self.lst_paragraph)

        # 删除图片临时文件
        for idx in range(self.img_idx + 1):
            img_path = os.path.join(self.base_path, "img_%s.jpg" % idx)
            try:
                os.remove(img_path)
            except (BaseException,):
                pass


def generate(path, lst_widget, title=None, **kwargs):
    """
    path:生成的文件路径
    lst_node:节点数据
    template_file：模板文件(只支持*.docx)
    """
    obj = Compiler(path, **kwargs)
    obj.write(lst_widget, obj.lst_paragraph)
    obj.to_pdf(title)


def word_2_pdf(word_path, pdf_path, title=None, **kwargs):
    from utils import word_2_vadmin
    obj = word_2_vadmin.Compiler(word_path, is_pdf=True)
    lst_widget = obj.parse()
    obj = Compiler(pdf_path, page_width=obj.page_width, page_height=obj.page_height,
                   top_margin=obj.top_margin, bottom_margin=obj.bottom_margin,
                   left_margin=obj.left_margin, right_margin=obj.right_margin,
                   lst_anchor_name=obj.lst_anchor_name, **kwargs)
    obj.write(lst_widget, obj.lst_paragraph)
    obj.to_pdf(title)


def pdf_2_image(pdf_path, image_path=None, cache=False):
    import fitz
    from vadmin import widgets
    from vadmin import common
    from vadmin.json_encoder import Encoder
    path, name = os.path.split(pdf_path)
    file_name = os.path.splitext(name)[0]
    file_name = common.format_file_name(file_name)
    if image_path is None:
        image_path = path

    if not os.path.exists(image_path):
        os.makedirs(image_path)

    widget_path = os.path.join(path, "%s.vadmin" % file_name)
    if cache:
        if os.path.exists(widget_path):
            buf = open(widget_path).read()
            try:
                o_panel = json.loads(buf)
                return o_panel
            except (BaseException,):
                pass

    pdf_doc = fitz.open(pdf_path)
    for page_idx in range(pdf_doc.pageCount):
        page = pdf_doc[page_idx]
        rotate = int(0)
        # 每个尺寸的缩放系数为1.3，这将为我们生成分辨率提高2.6的图像。
        # 此处若是不做设置，默认图片大小为：792X612, dpi=72
        zoom_x = 1.33333333  # (1.33333333-->1056x816)   (2-->1584x1224)
        zoom_y = 1.33333333
        mat = fitz.Matrix(zoom_x, zoom_y).preRotate(rotate)
        pix = page.getPixmap(matrix=mat, alpha=False)
        # pix = page.getPixmap(alpha=False)

        path = os.path.join(image_path, '%s_%s.png' % (file_name, page_idx))
        pix.writePNG(path)  # 将图片写入指定的文件夹内

    o_panel = widgets.Panel(width="100%")
    for page_idx in range(pdf_doc.pageCount):
        o_paragraph = widgets.Paragraph(horizontal="center")
        path = os.path.join(image_path, '%s_%s.png' % (file_name, page_idx))
        href = common.get_download_url(path)
        o_paragraph.append(widgets.Image(href))
        o_panel.append(o_paragraph)

    if cache:
        open(widget_path, "w").write(json.dumps(o_panel, ensure_ascii=False, cls=Encoder))
    return o_panel


if __name__ == "__main__":
    word_2_pdf("/Users/wangbin/Downloads/AAA BBB.docx", "/Users/wangbin/Downloads/AAA BBB.pdf")
