# !/usr/bin/python
# -*- coding=utf-8 -*-
"""
vadmin models
"""

import inspect
import json
import os
from importlib import import_module

from django.apps import apps
from django.conf import settings
from django.db import models
from django.db.models import fields
from django.utils.translation import gettext_lazy as _

from utils import storage
from vadmin import admin_api
from vadmin import admin_fields


class VModel(models.Model):
    class Meta(object):
        abstract = True

    def get_info(self, include=None, exclude=None):
        from utils import field_format
        dict_info = {}
        for field in self._meta.concrete_fields:
            if (exclude is not None) and (field.attname in exclude):
                continue

            if (include is not None) and (field.attname not in include):
                continue

            attname = field.attname
            val = getattr(self, field.attname)
            if isinstance(field, fields.CharField) or isinstance(field, fields.TextField):
                val = field_format.null_2_str(val)

            elif isinstance(field, fields.DateTimeField) or isinstance(field, fields.DateField) or \
                    isinstance(field, fields.TimeField):
                if val:
                    val = field_format.time_2_str(val)
            elif isinstance(field, fields.IntegerField) or isinstance(field, fields.FloatField) or \
                    isinstance(field, fields.PositiveIntegerField) or isinstance(field, fields.SmallIntegerField) or \
                    isinstance(field, fields.BigIntegerField):
                val = field_format.null_2_number(val)

            elif isinstance(field, fields.related.ForeignKey):
                val = field_format.null_2_number(val)

            elif isinstance(field, fields.files.ImageField):
                val = field_format.url_2_str(val)

            elif isinstance(field, fields.files.FileField):
                val = field_format.url_2_str(val)

            dict_info[attname] = val

        return dict_info

    def db_2_sql(self, lst_sql=None, is_ignore=False):
        lst_field = []
        lst_value = []
        for field in self._meta.concrete_fields:
            lst_field.append("`%s`" % field.attname)
            val = getattr(self, field.attname)
            if isinstance(field, fields.CharField) or isinstance(field, fields.TextField):
                if val is None:
                    lst_value.append("null")
                else:
                    try:
                        import re
                        val = re.sub(r"\\n", r"\\\\n", val)
                        val = re.sub(r"\\r", r"\\\\r", val)
                        val = re.sub(r"\\'", r"\\\\'", val)
                        val = re.sub(r'\\"', r'\\\\"', val)
                        val = re.sub(r"\'", r"\\'", val)
                        val = re.sub(r'\"', r'\\"', val)
                        val = re.sub(r"\n", r"\\n", val)
                        val = re.sub(r"\r", r"\\r", val)
                        val = re.sub(r"\\x", r"\\\\x", val)
                    except (BaseException,):
                        pass
                    # val = val.replace("\n", "\\n").replace("\'", "\\'").replace("\r", "\\r'").replace('\"', '\\"').replace(r"\x", r"\\x")
                    # val = val.replace("'\\n", "'\\\\n").replace('"\\n', '"\\\\n').replace("\\r\'", "\\\\r\'").replace('\\r\"', '\\\\r\"')

                    try:
                        val.encode(encoding='gb2312')
                        lst_value.append('"%s"' % val)
                        # lst_value.append('"%s"' % val.replace("\r\n", "\n").replace("'", "\\'").replace('"', '\\"'))
                    except (BaseException,):
                        try:
                            val = val.encode(encoding='utf-8')
                        except (BaseException,):
                            pass
                        lst_value.append('"%s"' % val)
                        # lst_value.append('"%s"' % val.replace("\r\n", "\n").replace("'", "\\'").replace('"', '\\"').encode(encoding='utf-8'))
            elif isinstance(field, (fields.files.ImageField, fields.files.FileField)):
                try:
                    if val.url.find("/media/") == 0:
                        url = val.url[7:]
                    else:
                        url = val.url
                    lst_value.append('"%s"' % url)
                except (BaseException,):
                    lst_value.append('""')

            elif isinstance(field, fields.DateTimeField) or isinstance(field, fields.DateField) or \
                    isinstance(field, fields.TimeField):
                if val is None:
                    lst_value.append("null")
                else:
                    lst_value.append('"%s"' % val)

            else:
                if val is None:
                    lst_value.append("null")
                else:
                    lst_value.append(val)

        if is_ignore:
            sql = "insert ignore into %s(%s) values(%s);" % (
                self._meta.db_table, ",".join(lst_field), ("%s," * len(lst_field)).strip(","))
        else:
            sql = "insert into %s(%s) values(%s);" % (
                self._meta.db_table, ",".join(lst_field), ("%s," * len(lst_field)).strip(","))

        sql = sql % tuple(lst_value)
        if lst_sql is not None:
            lst_sql.append(sql)

        return sql

    def add_2_sql(self):
        lst_field = []
        lst_value = []
        for field in self._meta.concrete_fields:
            lst_field.append("`%s`" % field.attname)
            val = getattr(self, field.attname)
            if isinstance(field, fields.CharField) or isinstance(field, fields.TextField):
                if val is None:
                    lst_value.append("null")
                else:
                    try:
                        val.encode(encoding='gb2312')
                        lst_value.append('"%s"' % val)
                    except (BaseException,):
                        lst_value.append('"%s"' % val.encode(encoding='utf-8'))

            elif isinstance(field, fields.DateTimeField) or isinstance(field, fields.DateField) or \
                    isinstance(field, fields.TimeField):
                if val is None:
                    lst_value.append("null")
                else:
                    lst_value.append('"%s"' % val)

            else:
                if val is None:
                    lst_value.append("null")
                else:
                    lst_value.append(val)

        sql = "INSERT INTO `%s` (%s) values(%s);" % (
            self._meta.db_table, ",".join(lst_field), ("%s," * len(lst_field)).strip(","))
        sql = sql % tuple(lst_value)
        return sql

    def del_2_sql(self):
        sql = "DELETE FROM `%s` WHERE `%s`.`id`=%s;" % (self._meta.db_table, self._meta.db_table, getattr(self, "id"))
        return sql

    def update_2_sql(self):
        # lst_field = []
        lst_value = []
        for field in self._meta.concrete_fields:

            if field.attname == "id":
                continue

            field_name = "`%s`" % field.attname
            val = getattr(self, field.attname)
            if isinstance(field, fields.CharField) or isinstance(field, fields.TextField):
                if val is None:
                    value = "null"
                else:
                    try:
                        import re
                        val = re.sub(r"\\n", r"\\\\n", val)
                        val = re.sub(r"\\r", r"\\\\r", val)
                        val = re.sub(r"\\'", r"\\\\'", val)
                        val = re.sub(r'\\"', r'\\\\"', val)
                        val = re.sub(r"\'", r"\\'", val)
                        val = re.sub(r'\"', r'\\"', val)
                        val = re.sub(r"\n", r"\\n", val)
                        val = re.sub(r"\r", r"\\r", val)
                        value = re.sub(r"\\x", r"\\\\x", val)
                    except (BaseException,):
                        pass
                    # try:
                    #     value = val.encode(encoding='gb2312')
                    # except (BaseException,):
                    # value = value.encode(encoding='utf-8')
                    value = '"%s"' % value
            elif isinstance(field, fields.DateTimeField) or isinstance(field, fields.DateField) or \
                    isinstance(field, fields.TimeField):
                if val is None:
                    value = "null"
                else:
                    value = '"%s"' % val

            else:
                if val is None:
                    value = "null"
                else:
                    value = val

            lst_value.append("%s=%s" % (field_name, value))

        sql = "UPDATE `%s` SET %s WHERE `%s`.`id`=%s;" % (self._meta.db_table, ",".join(lst_value),
                                                          self._meta.db_table, getattr(self, "id"))
        return sql

    @classmethod
    def query_model_class(cls, model_class_name):
        lst_app = settings.INSTALLED_APPS
        for app in lst_app:
            try:
                module = import_module('%s.models' % app)
                for name, obj in inspect.getmembers(module):
                    if inspect.isclass(obj) and issubclass(obj, VModel):  # 规避第三方model同名
                        if model_class_name == name:
                            return obj

            except (BaseException,):
                pass

        raise ValueError('没有找到%s对应的model类名.' % model_class_name)

    @classmethod
    def model_add(cls, request):
        model_name = request.POST["model_name"]
        dict_data = json.loads(request.POST["data"])
        model = admin_api.get_model(model_name=model_name)

        if hasattr(model, "user_id"):
            dict_data["user_id"] = request.user.pk

        m2m_data = {}
        dict_value = {}
        for k, v in dict_data.items():
            if isinstance(v, (list, tuple)):
                m2m_data[k] = v
            else:
                dict_value[k] = v
        obj = model.objects.create(**dict_value)

        for k, v in m2m_data.items():
            getattr(obj, k).set(v)

        try:
            from utils import cache_api
            cache_api.clear_table(model_name)
        except (BaseException,):
            pass

        return obj.get_info()

    @classmethod
    def model_del(cls, request):
        model_name = request.POST["model_name"]
        dict_data = json.loads(request.POST["data"])
        model = admin_api.get_model(model_name=model_name)
        lst_obj = model.objects.filter(**dict_data)
        for obj in lst_obj:
            if obj.user_id != request.user.pk:
                raise ValueError('%s类id等于%s数据非%用户新建，无权删除！' % (model_name, dict_data["id"], request.user.name))
        lst_obj.delete()

        try:
            from utils import cache_api
            cache_api.clear_table(model_name)
        except (BaseException,):
            pass

    @classmethod
    def model_edit(cls, request):
        model_name = request.POST["model_name"]
        dict_data = json.loads(request.POST["data"])
        model = admin_api.get_model(model_name=model_name)
        obj = model.objects.filter(pk=dict_data["id"]).first()
        if obj is None:
            VModel.model_add(request)
        else:
            # if not hasattr(obj, "user_id"):
            #     raise ValueError(u'%s类没有user_id字段（例如：user = models.ForeignKey(User, blank=True, '
            #                      u'null=True, on_delete=models.DO_NOTHING, verbose_name="作者"))，无权使用统一接口修改！' % model_name)
            #
            # elif obj.user_id != request.user.pk:
            #     raise ValueError(u'%s类id等于%s数据非%用户新建，无权修改！' %
            #                      (model_name, dict_data["id"], request.user.name))

            del dict_data["id"]
            for k, v in dict_data.items():
                if isinstance(v, (list, tuple)):
                    getattr(obj, k).set(v)
                else:
                    setattr(obj, k, v)
            obj.save()

        try:
            from utils import cache_api
            cache_api.clear_table(model_name)
        except (BaseException,):
            pass

    @classmethod
    def model_detail(cls, request):
        model_name = request.POST["model_name"]
        dict_data = json.loads(request.POST["data"])
        model = admin_api.get_model(model_name=model_name)
        obj = model.objects.filter(**dict_data).first()

        if not obj:
            return {}

        info_fun = request.POST.get("info_fun", "get_info")
        return getattr(obj, info_fun)()

    @classmethod
    def model_list_detail(cls, request):
        model_name = request.POST["model_name"]
        dict_data = json.loads(request.POST["data"])
        model = admin_api.get_model(model_name=model_name)
        lst_obj = model.objects.filter(**dict_data)
        lst_info = []
        for obj in lst_obj:
            lst_info.append(obj.get_info())

        return lst_info

    @classmethod
    def model_list(cls, request):
        model_name = request.POST["model_name"]
        page_size = int(request.POST.get("page_size", 30))
        if page_size > 100:
            page_size = 100
        page_num = int(request.POST.get("page_num", 1))
        dict_data = json.loads(request.POST.get("data", "{}"))
        if ("user_id" in dict_data) and dict_data["user_id"] == "request.user.id":
            dict_data["user_id"] = request.user.id

        model = admin_api.get_model(model_name=model_name)
        lst_obj = model.objects.filter(**dict_data)
        begin = page_size * (page_num - 1)
        end = begin + page_size
        lst_obj_info = []
        for obj in lst_obj[begin:end]:
            lst_obj_info.append(obj.get_info())

        return lst_obj_info

    @classmethod
    def model_class_list(cls, request):
        lst_class_info = []
        class_name = request.POST.get("model_name", None)

        for app_label in settings.INSTALLED_APPS:
            names = app_label.split(".")
            app_label = names[names.__len__() - 1]
            # 获取一个app
            app = apps.get_app_config(app_label)
            # 获取app下的所有model
            app_models = app.get_models()
            for model in app_models:
                table_name = str(model._meta.db_table)
                table_remark = str(model._meta.verbose_name)
                if issubclass(model, VModel):
                    model_class_name = str(model).split(".")[-1][0:-2]
                    if (class_name is not None) and (class_name.upper() not in model_class_name.upper()):
                        continue

                    cols = []
                    for db_field in model._meta.get_fields():
                        if isinstance(db_field, fields.related.ManyToManyRel) or isinstance(db_field,
                                                                                            models.ManyToOneRel):
                            continue

                        # col_name = str(db_field.name)
                        # col = db_field.column
                        verbose_name = str(db_field.verbose_name)
                        help_text = str(db_field.help_text)
                        field_type = str(type(db_field)).split(".")[-1][0:-2]
                        if help_text:
                            filed_info = "%s = models.%s(verbose_name='%s',help_text='%s')" % (
                                db_field.column, field_type, verbose_name, help_text)
                        else:
                            filed_info = "%s = models.%s(verbose_name='%s')" % (
                                db_field.column, field_type, verbose_name)
                        cols.append(filed_info)

                    lst_class_info.append({"table_name": table_name, "table_remark": table_remark,
                                           "model_class_name": model_class_name, "cols": cols})

        return lst_class_info


class ThemeConfig(VModel):
    """
    主题
    """
    id = admin_fields.UuidField(max_length=16, primary_key=True, verbose_name="ID")
    user_id = models.CharField(max_length=32, db_index=True, unique=True, verbose_name=u"用户ID")
    template = models.CharField(max_length=32, verbose_name="样式模板")
    color = models.CharField(max_length=8, verbose_name="主题颜色", blank=True, null=True)
    style = models.TextField(verbose_name="样式")

    # menu_position = models.CharField(max_length=5, default="left", choices=(("left", u"左侧"), ("top", u"顶部")))
    # round = models.IntegerField(default=0, verbose_name=u"圆角")
    # font_family = models.CharField(max_length=32, default="Microsoft YaHei",
    #                                choices=[("Microsoft YaHei", "微软雅黑"), ("Microsoft YaHei UI", "新版微软雅黑"),
    #                                         ("NSimSun", "新宋体"),
    #                                         ("SimSun", "宋体"), ("SimSun-ExtB", "扩展宋体"), ("SimHei", "黑体"),
    #                                         ("SimKai", "楷体")], verbose_name="字体")
    # font_size = models.IntegerField(default=14, choices=((13, "小"), (14, "标准"), (15, "较大"), (16, "大"), (17, "超大")),
    #                                 verbose_name="文字大小")

    class Meta(object):  # pylint: disable=C0111
        db_table = "t_v_theme"
        verbose_name = verbose_name_plural = u"主题"

    def __str__(self):
        return self.color


#
# class Image(VModel):
#     """
#     图片统一管理
#     """
#     id = admin_fields.UuidField(max_length=16, primary_key=True, verbose_name="ID")
#     user_id = models.CharField(max_length=32, blank=True, null=True, db_index=True, verbose_name=u'作者')
#     # image = models.ImageField(max_length=256, upload_to='images/%Y-%m-%d', storage=storage.ImageStorage(), blank=True, null=True,
#     #                           verbose_name=u'图片')
#     image = admin_fields.ImageField(upload_to='images/%Y-%m-%d', storage=storage.ImageStorage(), verbose_name=u'图片')
#     # image_thumb = models.ImageField(max_length=256, upload_to='images/%Y-%m-%d', storage=storage.ThumbStorage(), blank=True, null=True,
#     #                                 verbose_name=u'缩略图')
#     image_thumb = admin_fields.ImageField(upload_to='images/%Y-%m-%d', storage=storage.ThumbStorage(), blank=True,
#                                           null=True,
#                                           verbose_name=u'缩略图')
#     type = models.PositiveIntegerField(default=1, choices=((1, u"我的图片"), (2, u"全部图片")), verbose_name=u"类型")
#     # name = models.CharField(max_length=256, blank=True, null=True, verbose_name=u'名称')
#     image_size = models.IntegerField(blank=True, null=True, verbose_name=u"图片大小")
#     image_info = models.CharField(max_length=128, db_index=True, verbose_name=u"图片信息")
#     order = models.IntegerField(default=2147483647, db_index=True, verbose_name=u'排序')
#     create_time = models.DateTimeField(auto_now_add=True, verbose_name=u'创建时间')
#     update_time = models.DateTimeField(auto_now=True, verbose_name=u'修改时间')
#     del_flag = models.BooleanField(default=False, verbose_name=u'是否删除')
#
#     class Meta(object):  # pylint: disable=C0111
#         ordering = ("order", "-create_time")
#         db_table = "t_v_image"
#         verbose_name = verbose_name_plural = u"图片管理"
#
#     def __str__(self):
#         return "%s" % self.image


class GroupEx(VModel):
    # id = admin_fields.UuidField(max_length=16, primary_key=True, verbose_name="ID")
    name = models.CharField(_('name'), max_length=80)
    group_id = models.IntegerField(blank=True, null=True, verbose_name="权限ID", help_text="django权限ID")
    key = models.CharField(verbose_name="关键字", max_length=32, db_index=True, blank=True, null=True)  # base
    desc = models.CharField(verbose_name="说明", max_length=256, blank=True, null=True)
    # 在界面显示的菜单数据
    menu_data = models.TextField(blank=True, null=True, verbose_name="菜单数据")  # all
    # settings配置的,都用base_menu, 用来比较使用，如果settings中菜单配置数据和上一次的不一样，要重新清空数据
    menu = models.TextField(blank=True, null=True, verbose_name="配置菜单")  # base

    # 在权限组的显示的树数据,只在base_menu中有数据
    tree_data = models.TextField(blank=True, null=True, verbose_name="菜单树数据")  # base
    tree_value = models.TextField(blank=True, null=True, verbose_name="选择值")  # all(base为空）
    # 不在菜单中配置的model # base
    other_data = models.TextField(blank=True, null=True, verbose_name="其它权限", help_text="不在菜单中，但要显示的")
    other_value = models.TextField(blank=True, null=True, verbose_name="其它权限选择值")  # all(base为空）

    create_time = models.DateTimeField(auto_now_add=True, verbose_name=u'创建时间')
    del_flag = models.BooleanField(default=False, verbose_name=u'删除')
    order = models.IntegerField(db_index=True, default=2147483647, verbose_name=u'排序')

    class Meta:
        db_table = "t_v_auth_group"
        verbose_name = _('group')
        verbose_name_plural = _('groups')
        ordering = ["order", "create_time"]

    def __str__(self):
        return self.name


class PermissionEx(VModel):
    id = admin_fields.UuidField(max_length=16, primary_key=True, verbose_name="ID")
    name = models.CharField(_('name'), unique=True, max_length=128)
    codename = models.CharField(_('codename'), unique=True, max_length=128)

    class Meta:
        db_table = "t_v_auth_permission"
        verbose_name = _('permission')
        verbose_name_plural = _('permission')

    def __str__(self):
        return self.name
