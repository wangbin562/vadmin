# !/usr/bin/python
# -*- coding=utf-8 -*-
"""
vadmin自定义字段
"""
from django.db import models
from django.db.models.fields import related

count = 0


def create_uuid_16():
    """
    生成uuid 字符串(16个字节)
    :return: str  uuid
    """
    # data = uuid.UUID(bytes=os.urandom(16), version=4)
    # return str(data).replace("-", "")
    # import time
    import datetime
    # import random

    # now = time.time()
    # return "%s%s" % ("".join(random.sample("0123456789", 3)), str(now).replace(".", "")[-13:])
    global count
    count += 1

    now = datetime.datetime.now()
    s = "%s%03d" % (str(now).replace("-", "").replace(":", "").replace(".", "").replace(" ", "")[4:17], count % 999)
    if count >= 999:
        count = 0
    return s


def create_uuid_32():
    """
    生成uuid 字符串(32个字节)
    :return: str  uuid
    """
    import time
    import random
    import datetime
    # now = time.time()
    now = datetime.datetime.now()
    # return "%s%s" % ("".join(random.sample("0123456789012345", 15)), str(now).replace(".", "")[-17:])
    s = str(now).replace("-", "").replace(":", "").replace(".", "").replace(" ", "")
    s = "%s%s" % (s, "".join(random.sample("01234567890123456789", 32 - len(s))))
    return s


class UuidField(models.CharField):
    """
    字符串主键
    """

    # models.CharField(1max_length=32, primary_key=True, default=create_uuid, editable=False, verbose_name=u'主键')
    def __init__(self, **kwargs):
        kwargs.setdefault('max_length', 16)
        kwargs.setdefault('primary_key', True)
        if kwargs['max_length'] >= 32:
            kwargs.setdefault('default', create_uuid_32)
        else:
            kwargs['max_length'] = 16
            kwargs.setdefault('default', create_uuid_16)

        kwargs.setdefault('editable', False)
        kwargs.setdefault('verbose_name', 'ID')
        super(UuidField, self).__init__(**kwargs)


class HtmlField(models.TextField):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class ImageField(models.FileField):
    def __init__(self, verbose_name=None, name=None, upload_to='', upload_url=None,
                 storage=None, multiple=False, width=120, height=120, **kwargs):
        kwargs.setdefault('max_length', 1024)
        upload_to = upload_to or 'images/%Y-%m-%d'
        try:
            if not storage:
                from utils.storage import ThumbStorage
                storage = storage.ThumbStorage()
        except (BaseException,):
            pass
        super().__init__(verbose_name=verbose_name, name=name, upload_to=upload_to,
                         storage=storage, **kwargs)
        self.multiple = multiple
        self.upload_url = upload_url  # 上传文件保存路径
        self.kwargs = kwargs
        self.width = width
        self.height = height


class VideoFileField(models.FileField):
    def __init__(self, verbose_name=None, name=None, upload_to='', upload_url=None,
                 storage=None, multiple=False, width=600, height=400, **kwargs):
        kwargs.setdefault('max_length', 1024)
        upload_to = upload_to or 'images/%Y-%m-%d'
        try:
            if not storage:
                from utils.storage import ThumbStorage
                storage = ThumbStorage()
        except (BaseException,):
            pass
        super().__init__(verbose_name=verbose_name, name=name, upload_to=upload_to,
                         storage=storage, **kwargs)
        self.multiple = multiple
        self.upload_url = upload_url  # 上传文件保存路径
        self.kwargs = kwargs
        self.width = width
        self.height = height


class ImageManagerField(models.IntegerField):
    """图片管理字段，为此字段时，图片字段后面会自动增加一个图片管理器的链接"""

    def __init__(self, to=None, search_url=None, select_url=None, **kwargs):
        self.to = to
        self.search_url = search_url
        self.select_url = select_url
        super(ImageManagerField, self).__init__(**kwargs)


class FileField(models.FileField):
    """
    文件字段
    """

    def __init__(self, verbose_name=None, name=None, upload_to='', upload_url=None, storage=None,
                 multiple=False, **kwargs):
        kwargs.setdefault('max_length', 1024)
        upload_to = upload_to or 'files/%Y-%m-%d'
        try:
            if not storage:
                from utils.storage import FileStorage
                storage = FileStorage()
        except (BaseException,):
            pass
        super().__init__(verbose_name=verbose_name, name=name, upload_to=upload_to,
                         storage=storage, **kwargs)
        self.multiple = multiple
        self.upload_url = upload_url  # 上传文件保存路径
        self.kwargs = kwargs


class UEditorField(models.TextField):
    """
    富文本编辑器字段
    """

    def __init__(self, verbose_name=None, upload_to='', upload_url=None, width=800, height=400, **kwargs):
        super(UEditorField, self).__init__(verbose_name=verbose_name, **kwargs)
        self.width = width
        self.height = height
        self.upload_to = upload_to  # 上传文件保存路径
        self.upload_url = upload_url  # 上传文件保存路径


class VideoField(models.CharField):
    """
    视频字段，只显示
    """

    def __init__(self, verbose_name=None, width=None, height=None, **kwargs):
        kwargs.setdefault('max_length', 128)
        super().__init__(verbose_name=verbose_name, **kwargs)
        self.width = width
        self.height = height


class WordFiled(models.TextField):
    """word字段"""

    def __init__(self, verbose_name=None, width=600, height=300, **kwargs):
        super().__init__(verbose_name=verbose_name, **kwargs)
        self.width = width
        self.height = height


class ColorField(models.CharField):
    def __init__(self, **kwargs):
        kwargs.setdefault('max_length', 8)
        super(ColorField, self).__init__(**kwargs)


class CheckboxField(models.CharField):
    """checkbox字段，此字段在form界面显示checkbox"""

    def __init__(self, **kwargs):
        super(CheckboxField, self).__init__(**kwargs)


class SelectFilterField(models.Field):
    def __init__(self, **kwargs):
        if "max_length" in kwargs:
            self.__class__ = models.CharField
        else:
            self.__class__ = models.IntegerField

        super().__init__(**kwargs)
        self.field_type = SelectFilterField


#
# class SelectFilterCharField(models.CharField):
#     """
#     过滤响应字段
#     切换后响应消息，v_select_change_filter请求
#     """
#
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#
#
# class SelectFilterIntegerField(models.IntegerField):
#     """
#     过滤响应字段
#     切换后响应消息，v_select_change_filter请求
#     """
#
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)


class ForeignKey(related.ForeignKey):
    """外键字段，和django ForeignKey 唯一区别是在数据库中不创建关联关系"""

    def __init__(self, to, search_field=None, on_delete=None, related_name=None, related_query_name=None,
                 limit_choices_to=None, parent_link=False, to_field=None,
                 db_constraint=True, **kwargs):
        self.search_field = search_field
        # if related_name is None:
        #     related_name = "%s_%s" % (to._meta.model_name.lower(), 'a')
        if on_delete is None:
            if kwargs.get("null", False):
                on_delete = models.SET_NULL
            else:
                on_delete = models.CASCADE
        super().__init__(to, on_delete=on_delete, related_name=related_name, related_query_name=related_query_name,
                         limit_choices_to=limit_choices_to, parent_link=parent_link, to_field=to_field,
                         db_constraint=db_constraint, **kwargs)
        self.db_constraint = False
        # self.remote_field = False


class FileForeignKey(ForeignKey):
    """文件外键字段，自动转换保存到file_manager.model.File中"""

    def __init__(self, to, search_field=None, on_delete=None, related_name=None, related_query_name=None,
                 limit_choices_to=None, parent_link=False, to_field=None,
                 db_constraint=True, **kwargs):
        super().__init__(to, search_field, on_delete, related_name, related_query_name,
                         limit_choices_to, parent_link, to_field, db_constraint, **kwargs)


class ImageForeignKey(ForeignKey):
    def __init__(self, to, search_field=None, on_delete=None, related_name=None, related_query_name=None,
                 limit_choices_to=None, parent_link=False, to_field=None,
                 db_constraint=True, **kwargs):
        super().__init__(to, search_field, on_delete, related_name, related_query_name,
                         limit_choices_to, parent_link, to_field, db_constraint, **kwargs)


class CascadeFilterForeignKey(related.ForeignKey):
    """多级过滤外键字段"""

    def __init__(self, to, search_field=None, on_delete=None, related_name=None, related_query_name=None,
                 limit_choices_to=None, parent_link=False, to_field=None,
                 db_constraint=True, data=None, **kwargs):
        """
        data数据格式说明：
        {"parent": {"field": "province_id", "related_field": "province_id"},
                    sub": {"model": Area, "field": "area_id", "related_field": "city_id"}
        parent：父类， field:父类在此表中的字段名称  related_field：关联表中的关联字段名称
        sub:子类， model：子类的model名称 field:子类在此表中的字段名称  related_field：关联表中的关联字段名称
        """
        self.search_field = search_field
        # if related_name is None:
        #     related_name = "%s_%s" % (to._meta.model_name.lower(), 'a')
        if on_delete is None:
            if kwargs.get("null", False):
                on_delete = models.SET_NULL
            else:
                on_delete = models.CASCADE
        super().__init__(to, on_delete=on_delete, related_name=related_name, related_query_name=related_query_name,
                         limit_choices_to=limit_choices_to, parent_link=parent_link, to_field=to_field,
                         db_constraint=db_constraint, **kwargs)
        self.db_constraint = False
        self.data = data


class TreeField(models.TextField):
    """树字段"""

    def __init__(self, data=None, select=True, add_del=True, edit=True, order=False, **kwargs):
        self.data = data
        self.select = select
        self.add_del = add_del
        self.edit = edit
        self.order = order
        # self.model_name = model_name
        # self.field_name = field_name
        super(TreeField, self).__init__(**kwargs)


class DateField(models.DateField):
    """自定义日期字段"""

    def __init__(self, format="YYYY-mm-dd", verbose_name=None, name=None, auto_now=False,
                 auto_now_add=False, **kwargs):
        super(DateField, self).__init__(verbose_name, name, auto_now, auto_now_add, **kwargs)
        self.format = format
