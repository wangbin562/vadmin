# !/usr/bin/python
# -*- coding=utf-8 -*-
"""
case models
"""

from django.db import models
from vadmin.models import VModel
# from vadmin.models import Image
from vadmin import admin_fields
from vadmin import settings
from utils.storage import ImageStorage, FileStorage


class Province(VModel):
    """
    省
    """
    name = models.CharField(max_length=32, verbose_name=u'名称')
    order = models.PositiveIntegerField(db_index=True, default=2147483647, verbose_name=u'排序')

    class Meta(object):  # pylint: disable=C0111
        db_table = "t_province"
        verbose_name_plural = u"省"
        verbose_name = u"省"

    def __str__(self):
        return self.name


class City(VModel):
    """
    市
    """
    province = models.ForeignKey(Province, on_delete=models.CASCADE, verbose_name=u"省")
    name = models.CharField(max_length=32, verbose_name=u'市名称')
    del_flag = models.BooleanField(default=False, verbose_name=u'删除')
    order = models.IntegerField(db_index=True, default=2147483647, verbose_name=u'排序')

    class Meta(object):  # pylint: disable=C0111
        db_table = "t_city"
        verbose_name_plural = u"市"
        verbose_name = u"市"
        ordering = ("id",)

    def __str__(self):
        return self.name


class Area(VModel):
    """
    区
    """
    city = admin_fields.ForeignKey(City, search_field=["name", ], on_delete=models.CASCADE, blank=True, null=True,
                                   verbose_name=u"市")
    # unit = models.ForeignKey(Unit, on_delete=models.DO_NOTHING, verbose_name=u"工作单位")
    # address = models.ForeignKey(Address, on_delete=models.DO_NOTHING, verbose_name=u"地址")
    name = models.CharField(max_length=32, verbose_name=u'区名称')
    no = models.IntegerField(default=1, blank=True, null=True, verbose_name=u"区号")
    del_flag = models.BooleanField(default=False, verbose_name=u'删除')

    class Meta(object):  # pylint: disable=C0111
        db_table = "t_area"
        verbose_name_plural = u"区"
        verbose_name = u"区"

    def __str__(self):
        return self.name


class Unit(VModel):
    """
    工作单位
    """
    area = admin_fields.ForeignKey(Area, blank=True, null=True, verbose_name=u"区域")
    name = models.CharField(max_length=32, verbose_name=u'名称')
    age_float = models.DecimalField(max_digits=3, decimal_places=2, blank=True, null=True, verbose_name=u"年龄(float)")
    age_int = models.IntegerField(blank=True, null=True, default=1, choices=((1, 1), (2, 2)), verbose_name=u"年龄(int)")
    age_chart = models.CharField(max_length=32, blank=True, null=True, choices=(("1", 1), ("2", 2)),
                                 verbose_name=u"年龄(char)")

    # json = JSONField(verbose_name=u"json")
    # store = HStoreField(verbose_name=u"store")
    # array = ArrayField(verbose_name=u"array")

    class Meta(object):  # pylint: disable=C0111
        db_table = "t_unit"
        verbose_name_plural = u"工作单位"
        verbose_name = u"工作单位"

    def __str__(self):
        return self.name


class Widget(VModel):
    """
    图例类
    """
    input_rich = admin_fields.UEditorField(verbose_name=u'富文本', help_text="输入控件")
    input = models.CharField(verbose_name="输入", max_length=32, blank=True, null=True)
    input_text = models.TextField(verbose_name="多行输入", blank=True, null=True)
    radio = models.PositiveIntegerField(choices=((1, "是"), (2, "否")), verbose_name=u'单选框')
    checkbox = models.CharField(max_length=32, choices=(("1", "香蕉"), ("2", "苹果"), ("3", "西瓜")), verbose_name=u'多选框')
    switch = models.BooleanField(default=False, verbose_name=u'开关')
    date = models.DateField(verbose_name=u'日期', blank=True, null=True)
    time = models.TimeField(verbose_name=u'时间', blank=True, null=True)
    datetime = models.DateTimeField(verbose_name=u'日期时间', blank=True, null=True)
    color = models.CharField(max_length=16, blank=True, null=True, verbose_name=u"颜色")
    multiple = models.CharField(max_length=32, blank=True, null=True, verbose_name=u"多选",
                                choices=[["1", u"北京"], ["2", u"上海"], ["3", u"武汉"]], help_text=u"可以多选")
    slider = models.IntegerField(blank=True, null=True, verbose_name=u"滑块")
    image = admin_fields.ImageField(verbose_name=u'图片', blank=True, null=True, multiple=True)
    file = admin_fields.FileField(verbose_name='文件', blank=True, null=True)
    video_file = admin_fields.VideoFileField(verbose_name='视频文件', blank=True, null=True)
    video = admin_fields.VideoField(verbose_name="视频", max_length=512, blank=True, null=True,
                                    default="http://flv.bn.netease.com/29e65938275f223fdea9599723f7385e60321a9389efa1296ab5609c2110988cb39a77818d9770051b23429973dcd4f41367a67711d140cdfc8266bee4e8dabdb8da335a9791c45399bb1816731ee913fc636dadefa8b5ce6a408c3fbdb8f53278304aee3abb60dc574832c6564df53a2356116031f69d29.mp4")
    province = models.ForeignKey(Province, on_delete=models.CASCADE, blank=True, null=True, verbose_name=u'省',
                                 help_text="级联处理")
    city = models.ForeignKey(City, on_delete=models.CASCADE, blank=True, null=True, verbose_name=u'市')
    area = models.ForeignKey(Area, on_delete=models.CASCADE, blank=True, null=True, verbose_name=u'区')

    rate = models.FloatField(blank=True, null=True, verbose_name="评分")
    radio_button = models.IntegerField(blank=True, null=True, verbose_name="button样式单选",
                                       choices=((1, "香蕉"), (2, "苹果"), (3, "西瓜")))
    checkbox_button = models.CharField(max_length=16, blank=True, null=True, verbose_name="button样式多选",
                                       choices=(("1", "香蕉"), ("2", "苹果"), ("3", "西瓜")))

    create_time = models.DateTimeField(auto_now_add=True, verbose_name=u'创建时间')
    update_time = models.DateTimeField(auto_now=True, verbose_name=u'修改时间')
    del_flag = models.BooleanField(default=False, verbose_name=u'删除')
    order = models.IntegerField(db_index=True, default=2147483647, verbose_name=u'排序')

    class Meta(object):  # pylint: disable=C0111
        db_table = "t_widget"
        verbose_name_plural = u"图例类"
        verbose_name = u"图例类"
        ordering = ('order',)

    def __str__(self):
        return "%s-%s" % (self.pk, self.order)


class Rich(VModel):
    """
    图例类
    """
    input = admin_fields.UEditorField(verbose_name=u'输入')
    output = models.TextField(verbose_name=u"输出", blank=True, null=True)
    html_output = models.TextField(verbose_name=u"html输出", blank=True, null=True)
    create_time = models.DateTimeField(auto_now_add=True, verbose_name=u'创建时间')
    del_flag = models.BooleanField(default=False, verbose_name=u'删除')
    order = models.IntegerField(db_index=True, default=2147483647, verbose_name=u'排序')

    class Meta(object):  # pylint: disable=C0111
        db_table = "t_rich"
        verbose_name = verbose_name_plural = u"富文本"
        ordering = ('order',)

    def __str__(self):
        return "%s" % self.pk


class TemplateExample(VModel):
    """模板"""
    input = admin_fields.FileField(verbose_name='WORD模板')
    output = admin_fields.FileField(verbose_name="输出WORD", blank=True, null=True)
    vadmin_output = models.TextField(verbose_name="输出VAdmin", blank=True, null=True)
    html_output = models.TextField(verbose_name="输出HTML", blank=True, null=True)
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    order = models.IntegerField(db_index=True, default=2147483647, verbose_name='排序')

    class Meta(object):  # pylint: disable=C0111
        db_table = "t_template_example"
        verbose_name = verbose_name_plural = "模板"
        ordering = ('order',)

    def __str__(self):
        return "%s" % self.pk


class CollapseExample(VModel):
    """
    折叠、图片统一管理器、多级过滤案例
    """
    first = models.CharField(max_length=16, blank=True, null=True, verbose_name="第一部分")
    second = models.CharField(max_length=16, blank=True, null=True, verbose_name="第二部分")
    # image_id = admin_fields.ImageManagerField(Image, blank=True, null=True, verbose_name="图片")
    province = admin_fields.CascadeFilterForeignKey(Province,
                                                    data={"sub": {"field": "city_id", "related_field": "province_id"}},
                                                    blank=True, null=True,
                                                    verbose_name=u'省', help_text="级联处理")
    city = admin_fields.CascadeFilterForeignKey(City,
                                                data={
                                                    "parent": {"field": "province_id", "related_field": "province_id"},
                                                    "sub": {"field": "area_id", "related_field": "city_id"}},
                                                blank=True, null=True, verbose_name=u'市')
    area = admin_fields.CascadeFilterForeignKey(Area,
                                                data={"parent": {"field": "city_id", "related_field": "city_id"}, },
                                                blank=True, null=True, verbose_name=u'区')

    class Meta(object):  # pylint: disable=C0111
        db_table = "t_collapse_example"
        verbose_name_plural = u"折叠案例"
        verbose_name = u"折叠案例"

    def __str__(self):
        return str(self.first)


class TreeLevel(VModel):
    """
    同级树
    """
    name = models.CharField(max_length=16, blank=True, null=True, verbose_name="名称")
    parent = admin_fields.ForeignKey("self", search_field=["id", "name"],
                                     blank=True, null=True, verbose_name=u'父结点')
    level = models.PositiveIntegerField(blank=True, null=True, verbose_name=u'级别')
    order = models.IntegerField(db_index=True, default=2147483647, verbose_name=u'排序')

    class Meta(object):  # pylint: disable=C0111
        db_table = "t_tree"
        verbose_name_plural = u"同级树"
        verbose_name = u"同级树"

    def __str__(self):
        return self.name


class TreeLevel1(VModel):
    """
    一级树
    """
    name = models.CharField(max_length=16, blank=True, null=True, verbose_name="名称")
    order = models.IntegerField(db_index=True, default=2147483647, verbose_name=u'排序')

    class Meta(object):  # pylint: disable=C0111
        db_table = "t_tree_1"
        verbose_name_plural = u"一级树"
        verbose_name = u"一级树"

    def __str__(self):
        return self.name


class TreeLevel2(VModel):
    """
    二级树
    """
    tree_level_1 = admin_fields.ForeignKey(TreeLevel1, search_field=["id", "name"], verbose_name=u'一级树')
    name = models.CharField(max_length=16, blank=True, null=True, verbose_name="名称")
    order = models.IntegerField(db_index=True, default=2147483647, verbose_name=u'排序')

    class Meta(object):  # pylint: disable=C0111
        db_table = "t_tree_2"
        verbose_name_plural = u"二级树"
        verbose_name = u"二级树"

    def __str__(self):
        return self.name


class TreeLevel3(VModel):
    """
    三级树
    """
    tree_level_2 = admin_fields.ForeignKey(TreeLevel2, search_field=["id", "name"], verbose_name=u'二级树')
    name = models.CharField(max_length=16, blank=True, null=True, verbose_name="名称")
    order = models.IntegerField(db_index=True, default=2147483647, verbose_name=u'排序')

    class Meta(object):  # pylint: disable=C0111
        db_table = "t_tree_3"
        verbose_name_plural = u"三级树"
        verbose_name = u"三级树"

    def __str__(self):
        return self.name


class TreeExample(VModel):
    """
    树案例
    """
    desc = models.CharField(max_length=64, verbose_name=u'说明')
    # 同一张表，必须有level_field关键字
    # model:表model
    # label_field:树上显示label对应字段
    # order_field:排序对应字段，如果没有排序功能，可能不用填写"order_field"字段
    # parent_field：父结点字段
    data_same = admin_fields.TreeField(
        {"model": TreeLevel, "label_field": "name", "order_field": "order", "parent_field": "parent_id",
         "level_field": "level"},
        blank=True, null=True, verbose_name="同级排序", help_text="树结构在一张表中")
    # model:表model
    # label_field:树上显示label对应字段
    # order_field:排序对应字段，如果没有排序功能，可能不用填写"order_field"字段
    # parent_field：父结点字段
    data = admin_fields.TreeField([{"model": TreeLevel1, "label_field": "name", "order_field": "order"},
                                   {"model": TreeLevel2, "label_field": "name", "order_field": "order",
                                    "parent_field": "tree_level_1_id"},
                                   {"model": TreeLevel3, "label_field": "name", "order_field": "order",
                                    "parent_field": "tree_level_2_id"}
                                   ],
                                  blank=True, null=True, verbose_name="非同级排序", help_text="树结构根据层级在不同的表中")

    class Meta(object):  # pylint: disable=C0111
        db_table = "t_tree_example"
        verbose_name = verbose_name_plural = u"树编辑案例"

    def __str__(self):
        return ""


class DateExample(VModel):
    """
    时间组件案例
    """
    date1 = admin_fields.DateField(format="YYYY-mm", verbose_name="年月")
    date2 = admin_fields.DateField(format="YYYY", verbose_name="年")
    date3 = admin_fields.DateField(format="mm", verbose_name="月")

    class Meta(object):  # pylint: disable=C0111
        db_table = "t_date_example"
        verbose_name = verbose_name_plural = u"时间组件案例"

    def __str__(self):
        return ""


class FileExample(VModel):
    """
    文件组件案例
    """

    image = admin_fields.ImageField(upload_to='images/%Y-%m-%d', storage=ImageStorage(), blank=True, null=True,
                                    verbose_name=u'单图片')
    image_multiple = admin_fields.ImageField(upload_to='images/%Y-%m-%d', storage=ImageStorage(), blank=True,
                                             null=True, multiple=True,
                                             verbose_name=u'多图片')
    file = admin_fields.FileField(upload_to='files/%Y-%m-%d', storage=FileStorage(), blank=True, null=True,
                                  verbose_name=u'单文件')
    file_multiple = admin_fields.FileField(upload_to='files/%Y-%m-%d', storage=FileStorage(), blank=True, null=True,
                                           multiple=True, verbose_name=u'多文件')

    # image_id = admin_fields.ImageManagerField(Image, blank=True, null=True, verbose_name="图片管理")

    class Meta(object):  # pylint: disable=C0111
        db_table = "t_file_example"
        verbose_name = verbose_name_plural = u"文件组件案例"

    def __str__(self):
        return ""


class Address(VModel):
    """
    地址
    """
    area = models.ForeignKey(Area, on_delete=models.CASCADE, verbose_name=u"区域")
    name = models.CharField(max_length=32, verbose_name=u"地址名称")
    image = admin_fields.ImageField(blank=True, null=True, verbose_name="图片")
    address = admin_fields.ForeignKey("self", blank=True, null=True, related_name="address_address", verbose_name="地址")
    date_example = admin_fields.ForeignKey(DateExample, blank=True, null=True, verbose_name="时间组件")

    class Meta(object):  # pylint: disable=C0111
        db_table = "t_address"
        verbose_name_plural = u"地址"
        verbose_name = u"地址"

    def __str__(self):
        return self.name


class TreeTable(VModel):
    """
    tree_table
    """
    name = models.CharField(max_length=32, verbose_name=u"名称")
    parent = admin_fields.ForeignKey("self", search_field=["id", "name"], blank=True, null=True,
                                     verbose_name=u'父结点')

    class Meta(object):  # pylint: disable=C0111
        db_table = "t_tree_table"
        verbose_name_plural = u"树表格"
        verbose_name = u"树表格"

    def __str__(self):
        return self.name
