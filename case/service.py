# !/usr/bin/python
# -*- coding=utf-8 -*-
"""
case业务模块
"""
import json
import logging
import collections
import os

from django.conf import settings
from case.models import TemplateExample
from vadmin import widgets
from vadmin import report
from vadmin import step
from vadmin import const
from vadmin import common
from vadmin.json_encoder import Encoder
from case.models import Rich
from utils import word_template_2_vadmin
from utils import word_template_2_word

logger = logging.getLogger(__name__)


def report_test(request):
    """
    :param request:分页默认名称是p，在request.GET中会传入，同时request.GET也会传入自定义的过滤器参数
    :return:
    1、过滤器列表
    2、v_change_list_config配置，必须是全部字段配置, col_name必须用有序dict
    3、数据，二维数组
    """
    lst_filter = [widgets.Select(name="select_filter", data=[("1", ">60分"), ("2", ">80分")],
                                 width=220, clearable=False)]
    # col_width、col_fixed可以不配置，  col_name必须配置全
    col_name = collections.OrderedDict((("field_0", "班级"), ("field_1", "语文平均分数"),
                                        ("field_2", "数学平均分数"), ("field_3", "英语平均分数")))
    v_change_list_config = {"col_width": {"field_1": 300, "field_2": 300, "field_3": 300}, "col_fixed": {"left": 0, },
                            "col_name": col_name}
    data = [["1班", "60", "30", "60"], ["2班", "60", "50", "70"], ["3班", "60", "40", "50"], ["4班", "60", "50", "80"],
            ["1班", "60", "30", "60"], ["2班", "60", "50", "70"], ["3班", "60", "40", "50"], ["4班", "60", "50", "80"]]

    o_report = report.ReportConfig()
    o_report.row_data = data
    o_report.title = "测试图表"
    o_report.v_change_list_config = v_change_list_config
    o_report.lst_filter = lst_filter
    # o_report.chart_type = "line"
    o_report.chart_type = "bar"
    # o_report.chart_type = "pic"
    # o_report.chart_range = "B1:D4"
    o_report.v_export = True
    o_report.v_export_config = {"width": {1: 200, "field_3": 100}}
    o_report.page_total = 100
    o_report.page_index = 1
    return o_report


def test_html_2_word(request, **kwargs):
    from utils import html_2_word
    from utils import html_transform
    widget_data = kwargs["widget_data"]
    content = widget_data["input"]
    o_html = html_transform.Html(content)
    lst_panel = o_html.to_vadmin()
    output = json.dumps(lst_panel, ensure_ascii=False, cls=Encoder)
    id = request.GET.get("id", None)
    if id:
        obj = Rich.objects.filter(pk=id).first()
        obj.output = output
        obj.save()

    o_html.to_doc("1.docx")
    return [step.Msg("转换完成!"), step.WebViewOpera(reload=True)]


def cascader_load(request):
    return [{"label": "加载城市1"}, {"label": "加载城市2"}]


def tree_sort(request):
    return step.Msg("操作完成！")


def tree_click(request):
    event_data = request.POST.get("event_data", "{}")
    return step.Msg(event_data)


def word_2_vadmin(request):
    object_id = request.GET["object_id"]
    # mode = int(request.GET["mode"])
    obj = TemplateExample.objects.filter(pk=object_id).first()

    if obj and obj.input:
        from utils import word_2_vadmin
        path = common.get_file_path(obj.input.name)
        output = word_2_vadmin.generate(path)
        obj.vadmin_output = json.dumps(output, ensure_ascii=False, cls=Encoder)
        obj.save()

        return step.ViewOpera()

    # template_path = os.path.join(settings.BASE_DIR, obj.input.name.lstrip("/\\"))
    # path, file_name = os.path.split(template_path)
    # output_path = common.get_export_path(file_name)
    # o_panel = word_template_2_vadmin.generate(template_path, param)
    # word_template_2_word.generate(template_path, output_path, param)
    #
    # obj.vadmin_output = json.dumps(o_panel, ensure_ascii=False, cls=Encoder)
    # obj.output = output_path.replace(settings.BASE_DIR, "")
    # obj.save()


def word_2_pdf(request):
    object_id = request.GET["object_id"]
    # mode = int(request.GET["mode"])
    obj = TemplateExample.objects.filter(pk=object_id).first()

    if obj and obj.input:
        # from utils import word_2_vadmin
        from utils import vadmin_2_pdf
        path = common.get_file_path(obj.input.name)
        # obj = word_2_vadmin.Compiler(path)
        # lst_widget = obj.parse()

        pdf_path = common.get_export_path(path, suffix=".pdf")
        vadmin_2_pdf.word_2_pdf(path, pdf_path)
        file_url = common.get_download_url(pdf_path)
        return step.DownloadFile(file_url)
