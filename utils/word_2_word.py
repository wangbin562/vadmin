# !/usr/bin/python
# -*- coding=utf-8 -*-
"""
v1.2
"""
import os

import docx
from docx.oxml.table import CT_Tbl
from docx.oxml.text.paragraph import CT_P
from docx.table import Table
from docx.text.paragraph import Paragraph

try:
    import xml.etree.cElementTree as ET
except (BaseException,):
    import xml.etree.ElementTree as ET

BEGIN_KEY = "<%"
END_KEY = "%>"


class Compiler(object):
    def __init__(self, template_file, **kwargs):
        # self.lst_import = []
        # self.lst_global = []
        # self.lst_code = []

        self.doc = docx.Document(template_file)
        self.dict_param = kwargs
        # self.tree = ET.ElementTree()
        # self.root = ET.Element("body")
        # self.lst_paragraph = []
        # self.dict_run = {}
        # self.page_height = None
        # self.page_width = None
        self.script = None
        self.prev_run = None  # 上一段
        self.next_run = None  # 下一段
        # self.idx = None
        self.run = None

    def save(self, path):
        global _w
        global _write_widget
        _w = self.write
        _write_widget = self.write_widget
        globals().update(self.dict_param)
        self.parse()
        path_name = os.path.split(path)[0]
        if not os.path.exists(path_name):
            os.makedirs(path_name)
        self.doc.save(path)

    def write(self, content, **kwargs):
        if content:
            self.run.text += str(content)

    def write_widget(self, **kwargs):
        self.run.text += str(kwargs.get("value", ""))

    def parse_paragraph(self, paragraph, cell=None):
        run_len = len(paragraph.runs)
        if run_len == 0 and cell:
            return None

        for i, run in enumerate(paragraph.runs):
            if run.text:
                self.parse_run(run)
            # else:
            #     self.parse_image(run)

    def parse_script(self, run, script):
        self.run = run
        exec(script)
        self.script = None

    def parse_run(self, run):
        text = run.text
        begin_idx = text.find(BEGIN_KEY)
        end_idx = text.find(END_KEY)

        if self.script is not None:
            if end_idx < 0:
                self.script += text
                run.text = ""
            else:
                self.script += text[:end_idx]
                run.text = text[end_idx + 2:]
                self.parse_script(run, script=self.script)
                pass

        elif (begin_idx >= 0) and (end_idx >= 0):  # 在同一段
            run.text = text[:begin_idx] + text[end_idx + 2:]
            self.parse_script(run, script=text[begin_idx + 2: end_idx])
            pass

        elif begin_idx >= 0:
            self.script = text[begin_idx + 2:]
            run.text = text[:begin_idx]

    def parse_table(self, table):
        for row_idx, row in enumerate(table.rows):
            for col_idx, cell in enumerate(row.cells):
                for paragraph in cell.paragraphs:
                    self.parse_paragraph(paragraph, cell=cell)

    def parse(self):
        """
        解释文件
        """
        for child in self.doc._body._body:
            if isinstance(child, CT_P):
                paragraph = Paragraph(child, self.doc)
                self.parse_paragraph(paragraph)

            elif isinstance(child, CT_Tbl):
                table = Table(child, self.doc)
                self.parse_table(table)
            # else:
            # print(child)


def generate(template_file, path, **kwargs):
    """
    template_file：模板文件(只支持*.docx)
    is_compile:强制编译（模板转换成代码）
    """
    compiler = Compiler(template_file, **kwargs)
    compiler.save(path)


if __name__ == "__main__":
    generate(r"C:\wangbin\code_sync\code_sync\project_management\templates\winning.docx", "1.docx",
             project_name="aaaaaaaa")
