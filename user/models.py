# !/usr/bin/python
# -*- coding=utf-8 -*-
"""
user models
"""

import six
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.contrib.auth.models import Permission, Group
from django.contrib.auth.models import UserManager
from django.contrib.auth.validators import ASCIIUsernameValidator, UnicodeUsernameValidator
from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from utils import storage
from vadmin import admin_fields
from vadmin.models import VModel


class Department(VModel):
    """
    部门
    """
    name = models.CharField(max_length=56, verbose_name="名称")
    group = admin_fields.ForeignKey(Group, blank=True, null=True, verbose_name="权限")
    order = models.IntegerField(default=2147483647, db_index=True, verbose_name=u'排序')
    create_time = models.DateTimeField(auto_now_add=True, verbose_name=u'创建时间')
    del_flag = models.BooleanField(default=False, verbose_name=u'是否删除')

    class Meta(object):  # pylint: disable=C0111
        db_table = "t_department"
        verbose_name = verbose_name_plural = u"部门"
        ordering = ["order", ]

    def __str__(self):
        return self.name


class Role(VModel):
    """
    角色
    """
    department = admin_fields.ForeignKey(Department, blank=True, null=True, verbose_name="部门")
    name = models.CharField(max_length=56, verbose_name="名称", help_text="部分为空时，角色适用所有部门")
    order = models.IntegerField(default=2147483647, db_index=True, verbose_name=u'排序')
    create_time = models.DateTimeField(auto_now_add=True, verbose_name=u'创建时间')
    del_flag = models.BooleanField(default=False, verbose_name=u'是否删除')

    class Meta(object):  # pylint: disable=C0111
        db_table = "t_role"
        verbose_name = verbose_name_plural = u"角色"
        ordering = ["order", ]

    def __str__(self):
        return self.name


class User(AbstractBaseUser, PermissionsMixin):
    """
    用户
    """
    username_validator = UnicodeUsernameValidator() if six.PY3 else ASCIIUsernameValidator()
    username = models.CharField(u"平台帐号", max_length=150, unique=True,
                                help_text=_("Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only."),
                                validators=[username_validator],
                                error_messages={"unique": _("A user with that username already exists."), }, )
    email = models.EmailField(blank=True, null=True, verbose_name=_('email address'))
    name = models.CharField(max_length=64, blank=True, null=True, verbose_name=u'名称')
    # sex = models.IntegerField(blank=True, null=True, default=1, choices=((1, "男"), (2, "女")), verbose_name=u'性别')
    mobile = models.CharField(max_length=64, blank=True, null=True, verbose_name=u'电话号码')
    head = models.ImageField(upload_to='images/', storage=storage.ImageStorage(), blank=True, null=True,
                             verbose_name=u'头像')
    department = admin_fields.ForeignKey(Department, search_field=["name"], blank=True, null=True, verbose_name=u"部门")
    role = admin_fields.ForeignKey(Role, search_field=["name"], blank=True, null=True, verbose_name=u"角色")

    # type = models.IntegerField(blank=True, null=True, default=1, choices=((1, "管理员"), (2, "操作员")),
    # verbose_name=u'用户类别')
    last_login_time = models.DateTimeField(blank=True, null=True, verbose_name=u'上次登陆时间')
    is_active = models.BooleanField(default=True, verbose_name=u"有效")
    is_staff = models.BooleanField(_("staff status"), default=False,
                                   help_text=_("Designates whether the user can log into this admin site."))
    date_joined = models.DateTimeField(_("date joined"), default=timezone.now)
    create_time = models.DateTimeField(auto_now_add=True, verbose_name=u"创建时间")
    update_time = models.DateTimeField(auto_now=True, verbose_name=u"修改时间")
    # update_pwd_time = models.DateTimeField(auto_now_add=True, verbose_name=u"修改密码时间")
    del_flag = models.BooleanField(default=False, verbose_name=u'是否删除')

    objects = UserManager()

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["email", ]

    class Meta(object):  # pylint: disable=C0111
        db_table = "t_user"
        verbose_name = verbose_name_plural = u"用户"

    def __str__(self):
        return self.name or self.username
