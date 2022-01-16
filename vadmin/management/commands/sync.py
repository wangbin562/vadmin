# !/usr/bin/python
# -*- coding=utf-8 -*-
"""
支持mysql、sqlite
"""

import collections
import datetime
import importlib
import traceback
import re

from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import connection
from django.db import models
from django.db.utils import ProgrammingError
from django.db.utils import InternalError
from django.db.utils import OperationalError


def execute(cursor, sql):
    print(sql)
    cursor.execute(sql)


class Command(BaseCommand):

    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)
        self.cursor = connection.cursor()

    def add_arguments(self, parser):
        parser.add_argument(
            'args', metavar='app_label', nargs='*',
        )

    def handle(self, *args, **options):
        lst_err_app = []
        for app in args or settings.INSTALLED_APPS:
            try:
                module = importlib.import_module("%s.models" % app)
            except (BaseException,):
                continue

            print("app:%s" % app)
            for s in module.__dict__:
                try:
                    if s[0:2] == "__":
                        continue

                    model = getattr(module, s)
                    if (not hasattr(model, "__module__")) or (model.__module__.find(app) < 0) or \
                            (not hasattr(model, "_meta")):
                        continue

                    if model._meta.proxy or (not model._meta.db_table) or model._meta.abstract:
                        continue

                    if 'mysql' in settings.DATABASES['default']['ENGINE']:
                        obj = SyncMySql(self.cursor)
                        obj.sync_db(model)

                    elif 'sqlite3' in settings.DATABASES['default']['ENGINE']:
                        obj = SyncSqlite(self.cursor)
                        obj.sync_db(model)

                except (BaseException,):
                    print(traceback.format_exc())
                    lst_err_app.append(app)

        for app in lst_err_app:
            try:
                module = importlib.import_module("%s.models" % app)
            except (BaseException,):
                continue

            print("app:%s" % app)
            for s in module.__dict__:
                if s[0:2] == "__":
                    continue

                try:
                    model = getattr(module, s)
                    if (not hasattr(model, "__module__")) or (model.__module__.find(app) < 0) or \
                            (not hasattr(model, "_meta")):
                        continue

                    if model._meta.proxy or (not model._meta.db_table) or model._meta.abstract:
                        continue

                    if 'mysql' in settings.DATABASES['default']['ENGINE']:
                        obj = SyncMySql(self.cursor)
                        obj.sync_db(model)

                    elif 'sqlite3' in settings.DATABASES['default']['ENGINE']:
                        obj = SyncSqlite(self.cursor)
                        obj.sync_db(model)

                except (BaseException,):
                    print(traceback.format_exc())
                    return


class SyncMySql(object):
    def __init__(self, cursor):
        self.cursor = cursor

    def sync_db(self, model):
        """同步数据库"""
        print("table:%s" % model._meta.db_table)
        new = False
        lst_field_db = list()
        try:
            self.cursor.execute("show full columns from %s;" % model._meta.db_table)
        except (ProgrammingError,) as e:
            # print(traceback.format_exc())
            new = True
        else:
            lst_field_db = self.cursor.fetchall()

        if new:
            self.create_table(model)
        else:
            self.update_table(model, lst_field_db)

    def create_table(self, model):
        db_table = model._meta.db_table
        lst_sql = []
        lst_extend = []
        for db_field in model._meta.fields:
            lst_sql.append(self.make_field_sql(db_field))
            if isinstance(db_field, (models.AutoField, models.BigAutoField)):
                lst_extend.append("PRIMARY KEY (`%s`) USING BTREE" % db_field.get_attname())

        #     elif isinstance(db_field, models.ForeignKey):
        #         lst_extend.append("INDEX `%s_%s`(`%s`) USING BTREE" % (db_table, db_field.get_attname(),
        #                                                                db_field.get_attname()))
        #
        #     elif db_field.db_index:
        #         lst_extend.append("INDEX `%s_%s`(`%s`) USING BTREE" % (db_table, db_field.get_attname(),
        #                                                                db_field.get_attname()))
        #
        # for unique in model._meta.unique_together:
        #     pass
        #     # lst_extend.append("UNIQUE INDEX `%s_%s`(`%s`) USING BTREE," % (db_table, db_field.get_attname(),
        #     #                                                         db_field.get_attname()))

        lst_sql.extend(lst_extend)
        sql = ("CREATE TABLE `%s`  (\r\n" % db_table) + ",\r\n".join(lst_sql) + "\r\n)"
        if model._meta.verbose_name:
            sql += " COMMENT '%s'" % model._meta.verbose_name
        print(sql)
        self.cursor.execute(sql)

        dict_index = self.make_index(model)
        for k, v in dict_index.items():
            sql = "ALTER TABLE `%s` ADD %s;" % (db_table, v)
            print(sql)
            self.cursor.execute(sql)

        # 构造m2m
        self.make_m2m(model)

    def update_table(self, model, lst_field_db):
        """
        show columns from t_v_file;
        describe t_v_file;
        show create table t_v_file;
        show index from test;
        """
        db_table = model._meta.db_table
        sql = "SELECT TABLE_COMMENT FROM information_schema.TABLES WHERE TABLE_SCHEMA='%s' AND TABLE_NAME='%s';" % \
              (settings.DB_NAME, db_table)
        self.cursor.execute(sql)
        lst_comment = self.cursor.fetchall()
        if lst_comment and lst_comment[0] != model._meta.verbose_name:
            sql = "alter table %s comment '%s';" % (db_table, model._meta.verbose_name)
            self.cursor.execute(sql)

        dict_field = collections.OrderedDict()
        for db_field in model._meta.fields:
            field_name = db_field.get_attname()
            dict_field[field_name] = db_field

        dict_field_db = collections.OrderedDict()
        for row in lst_field_db:
            dict_field_db[row[0]] = row

        lst_del = []
        lst_add = []
        lst_update = []
        for k, v in dict_field.items():
            if k not in dict_field_db:
                lst_add.append(v)  # 增加
            else:
                sql1 = self.make_field_sql(v, row=dict_field_db[k])
                sql2 = self.make_field_sql_by_db(dict_field_db[k])
                if sql1 != sql2:
                    lst_update.append((v, sql1))  # 修改

        for k, v in dict_field_db.items():
            if k not in dict_field:
                lst_del.append(k)  # 删除

        for db_field in lst_add:
            row = self.check_field(db_field, dict_field, lst_field_db)
            if row:  # 提示修改
                if row[0] in lst_del:
                    print("是否把[%s]表[%s]字段修改成[%s]字段(y or n 默认:y):" % (db_table, row[0], db_field.get_attname()))
                    r = input()
                    if r.strip().lower() in ["", "y"]:
                        sql = self.make_field_sql(db_field)
                        sql = ("ALTER TABLE `%s` CHANGE `%s` " % (db_table, row[0])) + sql
                        print(sql)
                        self.cursor.execute(sql)
                        lst_del.remove(row[0])
                    else:
                        sql = self.make_field_sql(db_field)
                        sql = ("ALTER TABLE `%s` ADD " % db_table) + sql
                        print(sql)
                        self.cursor.execute(sql)

            else:  # 增加
                sql = self.make_field_sql(db_field)
                sql = ("ALTER TABLE `%s` ADD " % db_table) + sql
                # 表中有数据，且为非空的情况下要填写默认值
                if ('NOT NULL' in sql) and (' DEFAULT ' not in sql):
                    select_sql = "select count(*) from %s" % db_table
                    self.cursor.execute(select_sql)
                    count = self.cursor.fetchone()[0]
                    if count > 0:
                        default, is_str = self.get_default(db_field)
                        print("[%s.%s]新增字段为非空,表中有数据记录,请填写默认值(回车默认等于:%s):" %
                              (db_table, db_field.get_attname(), default))
                        r = input()
                        if r.strip() != "":
                            default = r.strip()

                        if is_str:
                            if default == '空字数串':
                                default = ""

                            sql2 = sql + (" DEFAULT '%s'" % default)
                        else:
                            sql2 = sql + (" DEFAULT %s" % default)

                        print(sql2)
                        self.cursor.execute(sql2)
                        sql = sql.replace(" ADD ", " CHANGE "). \
                            replace("`%s`" % db_field.get_attname(),
                                    "`%s` `%s`" % (db_field.get_attname(), db_field.get_attname()))

                print(sql)
                self.cursor.execute(sql)
        # 修改
        for db_field, sql in lst_update:
            sql = ("ALTER TABLE `%s` CHANGE `%s` " % (db_table, db_field.get_attname())) + sql
            print(sql)
            try:
                self.cursor.execute(sql)
            except InternalError as e:
                if e.args[0] == 1138:
                    # 没有默认值
                    if not (("NOT_PROVIDED" not in str(db_field.default)) and (not callable(db_field.default))):
                        default, is_str = self.get_default(db_field)
                        print("[%s.%s]字段修改为非空,表中数据此字段有空值,请填写修改值(回车默认等于:%s):" %
                              (db_table, db_field.get_attname(), default))
                        r = input()
                        if r.strip() != "":
                            default = r.strip()

                        if is_str:
                            if default == '空字数串':
                                default = "''"
                    else:
                        default = db_table.default

                    sql = "UPDATE `%s` SET `%s`=%s WHERE `%s` IS NULL" % \
                          (db_table, db_field.get_attname(), default, db_field.get_attname())
                    print(sql)
                    self.cursor.execute(sql)
                else:
                    raise
            except OperationalError as e:
                if e.args[0] == 1138:
                    # 没有默认值
                    if not (("NOT_PROVIDED" not in str(db_field.default)) and (not callable(db_field.default))):
                        default, is_str = self.get_default(db_field)
                        print("[%s.%s]字段修改为非空,表中数据此字段有空值,请填写修改值(回车默认等于:%s):" %
                              (db_table, db_field.get_attname(), default))
                        r = input()
                        if r.strip() != "":
                            default = r.strip()

                        if is_str:
                            if default == '空字数串':
                                default = "''"
                    else:
                        default = db_table.default

                    sql = "UPDATE `%s` SET `%s`=%s WHERE `%s` IS NULL" % \
                          (db_table, db_field.get_attname(), default, db_field.get_attname())
                    print(sql)
                    self.cursor.execute(sql)
                else:
                    raise

        # 删除
        for field_name in lst_del:
            sql = "ALTER TABLE `%s` DROP `%s`;" % (db_table, field_name)
            print(sql)
            self.cursor.execute(sql)

        # 最后修改索引
        dict_index = self.make_index(model)
        dict_index_db = self.make_index_by_db(model._meta.db_table)
        # lst_index = list(dict_index_db.values())
        # lst_index_name = list(dict_index_db.keys())
        lst_add_sql = []
        for k, v in dict_index.items():
            if (k not in dict_index_db) or (dict_index_db[k] != v):
                sql = "ALTER TABLE `%s` ADD %s;" % (db_table, v)

                try:
                    self.cursor.execute(sql)
                    print(sql)
                except (BaseException,):
                    lst_add_sql.append(sql)  # 有可能索引名称一样，内容不一样，要先删除才能生效

        for k, v in dict_index_db.items():
            if (k not in dict_index) or (v != dict_index[k]):
                sql = "DROP INDEX `%s` ON `%s`;" % (k, db_table)
                print(sql)
                self.cursor.execute(sql)
                # lst_index_name.remove(k)

        for sql in lst_add_sql:
            print(sql)
            self.cursor.execute(sql)

        # 构造m2m
        self.make_m2m(model)

    def make_field_sql(self, db_field, field_name=None, verbose_name=None,
                       null=None, primary_key=None, row=None):
        sql = ""
        is_str = False
        field_name = field_name or db_field.get_attname()
        verbose_name = verbose_name or db_field.verbose_name
        null = null or db_field.null
        if primary_key is None:
            primary_key = db_field.primary_key

        if isinstance(db_field, models.CharField):
            # sql = "`%s` varchar(%s) CHARACTER SET utf8 COLLATE utf8_general_ci" % (field_name, db_field.max_length)
            sql = "`%s` varchar(%s)" % (field_name, db_field.max_length)
            is_str = True
        elif isinstance(db_field, models.TextField):
            # sql = "`%s` longtext CHARACTER SET utf8 COLLATE utf8_general_ci" % field_name
            sql = "`%s` longtext" % field_name
            is_str = True
        elif isinstance(db_field, (models.FloatField, models.DecimalField)):
            sql = "`%s` double" % field_name
        elif isinstance(db_field, (models.BigIntegerField, models.BigAutoField)):
            sql = "`%s` bigint" % field_name
        elif isinstance(db_field, (models.SmallIntegerField, models.PositiveSmallIntegerField)):
            sql = "`%s` smallint" % field_name
        elif isinstance(db_field, (models.IntegerField, models.PositiveIntegerField, models.AutoField)):
            sql = "`%s` int" % field_name
        elif isinstance(db_field, (models.BooleanField, models.NullBooleanField)):
            sql = "`%s` tinyint" % field_name
        elif isinstance(db_field, models.DateTimeField):
            sql = "`%s` datetime(6)" % field_name
            is_str = True

        elif isinstance(db_field, models.DateField):
            sql = "`%s` date" % field_name
            is_str = True

        elif isinstance(db_field, models.TimeField):
            sql = "`%s` time" % field_name
            is_str = True
        elif isinstance(db_field, (models.FileField, models.ImageField)):
            sql = "`%s` varchar(%s)" % (field_name, db_field.max_length or 256)
            is_str = True

        elif isinstance(db_field, models.ForeignKey):
            return self.make_field_sql(db_field.target_field, field_name, verbose_name,
                                       null=null, primary_key=False, row=row)

        elif isinstance(db_field, models.ManyToManyField):
            raise ValueError(u'没有支持ManyToManyField字段！')

        if null:
            sql = sql + " NULL"
        else:
            sql = sql + " NOT NULL"

        if verbose_name:
            sql = sql + (" COMMENT '%s'" % verbose_name)

        if ("NOT_PROVIDED" not in str(db_field.default)) and (not callable(db_field.default)):
            default = db_field.default
            if isinstance(db_field, (models.BooleanField, models.NullBooleanField)):
                default = int(db_field.default)

            if isinstance(db_field, (models.SmallIntegerField, models.PositiveSmallIntegerField,
                                     models.IntegerField, models.PositiveIntegerField, models.BigIntegerField)):
                default = int(db_field.default)

            if row and row[5] is not None:
                if isinstance(default, int):
                    if int(row[5]) == default:
                        default = row[5]
                elif isinstance(default, float):
                    if float(row[5]) == default:
                        default = row[5]

                elif row[5] == default:
                    default = row[5]

            if is_str:
                sql = sql + (" DEFAULT '%s'" % default)
            else:
                sql = sql + (" DEFAULT %s" % default)

        if primary_key and isinstance(db_field, (models.BigAutoField, models.AutoField)):
            sql += " AUTO_INCREMENT"

        return sql

    def make_field_sql_by_db(self, row):
        if row[1].find("int") > -1 and row[1].find("(") > -1:
            field_type = row[1].split("(")[0]
        else:
            field_type = row[1]

        sql = "`%s` %s" % (row[0], field_type)
        # if row[2]:
        #     sql = sql + " CHARACTER SET utf8 COLLATE %s" % row[2]

        if row[3] == "YES":
            sql = sql + " NULL"
        else:
            sql = sql + " NOT NULL"

        if row[-1]:  # commnet
            sql = sql + (" COMMENT '%s'" % row[-1])

        if row[5]:  # DEFAULT
            if row[1].find("int") > -1 or row[1].find("double") > -1:
                sql = sql + (" DEFAULT %s" % row[5])
            else:
                sql = sql + (" DEFAULT '%s'" % row[5])

        if row[6]:
            sql += " AUTO_INCREMENT"

        return sql

    def check_field(self, db_field, dict_field, lst_field_db):
        for row in lst_field_db:
            if row[0] in dict_field:
                continue

            if db_field.verbose_name == row[-1]:
                return row

    def get_default(self, db_field):
        is_str = False
        if isinstance(db_field, models.CharField):
            default = "空字数串"
            is_str = True
        elif isinstance(db_field, models.TextField):
            default = "空字数串"
            is_str = True
        elif isinstance(db_field, (models.FloatField, models.DecimalField)):
            default = "0.00"
        elif isinstance(db_field, (models.BigIntegerField, models.BigAutoField)):
            default = "0"
        elif isinstance(db_field, (models.SmallIntegerField, models.PositiveSmallIntegerField)):
            default = "0"
        elif isinstance(db_field, (models.IntegerField, models.PositiveIntegerField, models.AutoField)):
            default = "0"
        elif isinstance(db_field, (models.BooleanField, models.NullBooleanField)):
            default = "0"
        elif isinstance(db_field, models.DateTimeField):
            default = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            is_str = True

        elif isinstance(db_field, models.DateField):
            default = datetime.datetime.now().strftime("%Y-%m-%d")
            is_str = True

        elif isinstance(db_field, models.TimeField):
            default = datetime.datetime.now().strftime("%H:%M:%S")
            is_str = True
        elif isinstance(db_field, (models.FileField, models.ImageField)):
            default = "空字数串"
            is_str = True
        elif isinstance(db_field, models.ForeignKey):
            default = 'NULL'
        else:
            default = ""

        return default, is_str

    def make_index(self, model):
        dict_sql = collections.OrderedDict()
        db_table = model._meta.db_table
        for db_field in model._meta.fields:
            if isinstance(db_field, models.ForeignKey):
                index_name = "%s_%s" % (db_table, db_field.get_attname())
                sql = "INDEX `%s`(`%s`)" % (index_name, db_field.get_attname())
                dict_sql[index_name] = sql
            elif not db_field.primary_key and db_field.unique:  # 主键在字段中修改
                index_name = "%s_%s" % (db_table, db_field.get_attname())
                sql = "UNIQUE `%s`(`%s`)" % (index_name, db_field.get_attname())
                dict_sql[index_name] = sql
            elif db_field.db_index:
                index_name = "%s_%s" % (db_table, db_field.get_attname())
                sql = "INDEX `%s`(`%s`)" % (index_name, db_field.get_attname())
                dict_sql[index_name] = sql

        if model._meta.unique_together and not isinstance(model._meta.unique_together[0], (tuple, list)):
            unique_together = [model._meta.unique_together, ]
        else:
            unique_together = model._meta.unique_together

        for unique in unique_together:
            if isinstance(unique, (tuple, list)):
                lst_field_name = []
                for field_name in unique:
                    field_name = model._meta.get_field(field_name).get_attname()
                    lst_field_name.append(field_name)
                index_name = "%s_%s" % (db_table,
                                        str(lst_field_name).strip("[]() ,'\"").replace(" ", "").
                                        replace(",", "_").replace("'", "").replace('"', ""))
                index_name = index_name[-64:]
                index_field = str(lst_field_name).strip("[]() ,").replace("'", "`"). \
                    replace('"', "`").replace(" ", "")
                sql = "UNIQUE `%s`(%s)" % (index_name, index_field)
                dict_sql[index_name] = sql

        return dict_sql

    def make_index_by_db(self, db_table):
        sql = "show index from `%s`;" % db_table
        self.cursor.execute(sql)
        dict_index = collections.OrderedDict()
        for row in self.cursor.fetchall():
            if row[2] == "PRIMARY":
                continue

            dict_index.setdefault(row[2], []).append(row)

        dict_sql = collections.OrderedDict()
        for k, v in dict_index.items():
            lst_field_name = []
            unique = False
            for item in v:
                lst_field_name.append(item[4])
                unique = not bool(item[1])

            if unique:
                index_name = "%s_%s" % (db_table,
                                        str(lst_field_name).strip("[]() ,'\"").replace(" ", "").
                                        replace(",", "_").replace("'", "").replace('"', ""))
                index_field = str(lst_field_name).strip("[]() ,").replace("'", "`"). \
                    replace('"', "`").replace(" ", "")
                index_name = index_name[-64:]
                sql = "UNIQUE `%s`(%s)" % (index_name, index_field)
            else:
                index_name = "%s_%s" % (db_table,
                                        str(lst_field_name).strip("[]() ,'\"").replace(" ", "").
                                        replace(",", "_").replace("'", "").replace('"', ""))
                index_name = index_name[-64:]
                index_field = str(lst_field_name).strip("[]() ,").replace("'", "`"). \
                    replace('"', "`").replace(" ", "")
                sql = "INDEX `%s`(%s)" % (index_name, index_field)

            dict_sql[k] = sql

        return dict_sql

    def make_m2m(self, model):
        db_table = model._meta.db_table
        for db_field in model._meta.local_many_to_many:
            if not hasattr(db_field, "target_field"):
                continue

            table_name = "%s_%s" % (db_table, db_field.name)
            try:
                self.cursor.execute("show full columns from %s;" % table_name)
            except (ProgrammingError,) as e:
                # print(traceback.format_exc())
                lst_sql = ["`id` int NOT NULL AUTO_INCREMENT"]
                field_name1 = "%s_id" % db_field.model.__name__.lower()
                sql = self.make_field_sql(model._meta.pk, field_name1)
                sql = sql.replace("AUTO_INCREMENT", "").strip()
                lst_sql.append(sql)
                field_name2 = "%s_%s" % (db_field.target_field.model.__name__.lower(), db_field.target_field.name)
                sql = self.make_field_sql(db_field.target_field, field_name2)
                sql = sql.replace("AUTO_INCREMENT", "").strip()
                lst_sql.append(sql)
                lst_sql.append('PRIMARY KEY (`id`) USING BTREE')
                lst_sql.append('UNIQUE INDEX `%s_%s_%s`(`%s`, `%s`) USING BTREE' %
                               (table_name, field_name1, field_name2, field_name1, field_name2))
                lst_sql.append('INDEX `%s_%s`(`%s`) USING BTREE' % (table_name, field_name2, field_name2))

                sql = ("CREATE TABLE `%s`  (\r\n" % table_name) + ",\r\n".join(lst_sql) + "\r\n)"
                print(sql)
                self.cursor.execute(sql)
            else:
                lst_field_db = self.cursor.fetchall()
                dict_field_db = collections.OrderedDict()
                for row in lst_field_db:
                    dict_field_db[row[0]] = row

                # field_name1 = "%s_id" % db_field.remote_field.name
                field_name1 = "%s_id" % db_field.model.__name__.lower()
                sql = self.make_field_sql(model._meta.pk, field_name1)
                sql1 = sql.replace("AUTO_INCREMENT", "").strip()
                lst_update = []
                lst_add = []
                if field_name1 in dict_field_db:
                    sql2 = self.make_field_sql_by_db(dict_field_db[field_name1])
                    if sql1 != sql2:
                        lst_update.append((field_name1, sql1))
                else:
                    lst_add.append((field_name1, sql1))

                field_name2 = "%s_%s" % (db_field.target_field.model.__name__.lower(), db_field.target_field.name)
                sql = self.make_field_sql(db_field.target_field, field_name2)
                sql1 = sql.replace("AUTO_INCREMENT", "").strip()
                if field_name2 in dict_field_db:
                    sql2 = self.make_field_sql_by_db(dict_field_db[field_name2])
                    if sql1 != sql2:
                        lst_update.append((field_name2, sql1))
                else:
                    lst_add.append((field_name2, sql1))

                for field_name, sql in lst_update:
                    sql = ("ALTER TABLE `%s` CHANGE `%s` " % (table_name, field_name)) + sql
                    print(sql)
                    self.cursor.execute(sql)

                for field_name, sql in lst_add:
                    sql = ("ALTER TABLE `%s` ADD " % table_name) + sql
                    print(sql)
                    self.cursor.execute(sql)


class SyncSqlite(object):
    def __init__(self, cursor):
        self.cursor = cursor

    def sync_db(self, model):
        """同步数据库"""
        print("table:%s" % model._meta.db_table)
        lst_table = list()
        try:
            self.cursor.execute("SELECT * FROM sqlite_master WHERE type='table' AND tbl_name='%s';" %
                                model._meta.db_table)
        except (ProgrammingError,) as e:
            # print(traceback.format_exc())
            pass
        else:
            lst_table = self.cursor.fetchall()

        if not lst_table:
            self.create_table(model._meta.db_table, model._meta.fields, model)
        else:
            self.update_table(model._meta.db_table, model._meta.fields, model)

    def create_table(self, db_table, lst_field, model=None):
        lst_sql = []
        for db_field in lst_field:
            lst_sql.append(self.make_field_sql(db_field))

        sql = ('CREATE TABLE "main"."%s" (\r\n' % db_table) + ",\r\n".join(lst_sql) + "\r\n)"
        execute(self.cursor, sql)

        if model:
            dict_index = self.make_index(model)
            for k, v in dict_index.items():
                sql = "CREATE %s" % v
                execute(self.cursor, sql)

            # 构造m2m
            self.make_m2m(model)

    def update_table(self, db_table, lst_field, model=None):
        dict_field = collections.OrderedDict()
        lst_field_name = []
        for db_field in lst_field:
            field_name = db_field.get_attname()
            dict_field[field_name] = db_field
            lst_field_name.append(field_name)

        self.cursor.execute("PRAGMA table_info('%s');" % db_table)
        lst_field_db = self.cursor.fetchall()
        dict_field_db = collections.OrderedDict()
        for row in lst_field_db:
            dict_field_db[row[1]] = row

        lst_del = []
        lst_add = []
        lst_update = []
        for k, v in dict_field.items():
            if k not in dict_field_db:
                lst_add.append(v)  # 增加
            else:
                sql1 = self.make_field_sql(v, row=dict_field_db[k])
                sql2 = self.make_field_sql_by_db(dict_field_db[k], db_table)
                if sql1 != sql2:
                    lst_update.append((v, sql1))  # 修改

        for k, v in dict_field_db.items():
            if k not in dict_field:
                lst_del.append(k)  # 删除

        dict_new_old = {}
        for db_field in lst_add:
            sql = self.make_field_sql(db_field, add_field=False)
            # 表中有数据，且为非空的情况下要填写默认值
            if ('NOT NULL' in sql) and (' DEFAULT ' not in sql):
                is_str = 1
                if isinstance(db_field, models.CharField):
                    default = ""
                elif isinstance(db_field, models.TextField):
                    default = ""
                elif isinstance(db_field, (models.FloatField, models.DecimalField)):
                    default = 0.00
                    is_str = 2
                elif isinstance(db_field, (models.BigIntegerField, models.BigAutoField,
                                           models.SmallIntegerField, models.PositiveSmallIntegerField,
                                           models.IntegerField, models.PositiveIntegerField, models.AutoField,
                                           models.BooleanField, models.NullBooleanField)):
                    default = 0
                    is_str = 3
                elif isinstance(db_field, models.DateTimeField):
                    default = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                elif isinstance(db_field, models.DateField):
                    default = datetime.datetime.now().strftime("%Y-%m-%d")
                elif isinstance(db_field, models.TimeField):
                    default = datetime.datetime.now().strftime("%H:%M:%S")
                elif isinstance(db_field, (models.FileField, models.ImageField)):
                    default = ""
                elif isinstance(db_field, models.ForeignKey):
                    default = None
                else:
                    default = ""

                if default is None:
                    while True:
                        print("表中有数据记录，请填写%s字段默认值(关联外键必填):" % db_field.get_attname())
                        r = input()
                        if r.strip() != "":
                            default = r.strip()
                            break
                else:
                    print("表中有数据记录，请填写%s字段默认值(回车默认等于:%s):" % (db_field.get_attname(), default))
                    r = input()
                    if r.strip() != "":
                        default = r.strip()
                        if is_str == 2:
                            default = float(default)
                        elif is_str == 3:
                            default = int(float(default))

                db_field.default = default

            sql1 = self.make_field_sql(db_field, add_field=False)
            for k in lst_del:
                sql2 = self.make_field_sql_by_db(dict_field_db[k], db_table, add_field=False)
                if sql1 == sql2:
                    print("是否把%s字段修改成%s字段(y or n 默认:y):" % (k, db_field.get_attname()))
                    r = input()
                    if r.strip().lower() in ["", "y"]:
                        dict_new_old[db_field.get_attname()] = k
                        lst_add.remove(db_field)
                    break

        if lst_update or lst_del:
            old_table = "%s-%s" % (db_table, datetime.datetime.now().strftime("%Y%m%d%H%M%S"))
            sql = "ALTER TABLE '%s' RENAME TO '%s';" % (db_table, old_table)
            execute(self.cursor, sql)

            self.create_table(db_table, lst_field)

            # 从旧表中导入数据
            new_field = []
            old_field = []
            for field_name in lst_field_name:
                if field_name in dict_field_db:
                    new_field.append('"%s"' % field_name)
                    old_field.append('"%s"' % field_name)
                elif field_name in dict_new_old:
                    new_field.append('"%s"' % field_name)
                    old_field.append('"%s"' % dict_new_old[field_name])

            try:
                sql = 'INSERT INTO "%s" (%s) SELECT %s FROM "%s";' % (db_table, ",".join(new_field),
                                                                      ",".join(old_field), old_table)
                execute(self.cursor, sql)
            except (BaseException,):

                # 恢复数据
                sql = "DROP TABLE '%s';" % db_table
                execute(self.cursor, sql)

                sql = "ALTER TABLE '%s' RENAME TO '%s';" % (old_table, db_table)
                execute(self.cursor, sql)

            else:
                # 删除旧表
                sql = "DROP TABLE '%s';" % old_table
                execute(self.cursor, sql)

        if lst_add:
            for db_field in lst_add:
                sql = self.make_field_sql(db_field, add_field=False)
                sql = 'ALTER TABLE "%s" ADD "%s" %s;' % (db_table, db_field.get_attname(), sql)
                execute(self.cursor, sql)

        # 最后修改索引
        if model and (lst_update or lst_del or lst_add):
            dict_index = self.make_index(model)
            dict_index_db = self.make_index_by_db(db_table)
            for k, v in dict_index.items():
                if k not in dict_index_db:
                    sql = "CREATE %s" % v
                    try:
                        self.cursor.execute(sql)
                        print(sql)
                    except (BaseException,):
                        sql2 = 'DROP INDEX "%s";' % k
                        self.cursor.execute(sql2)
                        execute(self.cursor, sql)

                elif dict_index_db[k] != v:
                    sql = 'DROP INDEX "%s";' % k
                    execute(self.cursor, sql)

                    sql = "CREATE %s" % v
                    execute(self.cursor, sql)

            for k, v in dict_index_db.items():
                if k not in dict_index:
                    sql = 'DROP INDEX "%s";' % k
                    execute(self.cursor, sql)

            # 构造m2m
            self.make_m2m(model)

    def make_field_sql(self, db_field, field_name=None, verbose_name=None,
                       null=None, primary_key=None, row=None, add_field=True):
        sql = ""
        is_str = False
        field_name = field_name or db_field.get_attname()
        verbose_name = verbose_name or db_field.verbose_name
        null = null or db_field.null
        if primary_key is None:
            primary_key = db_field.primary_key

        if isinstance(db_field, models.CharField):
            sql = "text(%s)" % db_field.max_length
            is_str = True
        elif isinstance(db_field, models.TextField):
            sql = "text"
            is_str = True
        elif isinstance(db_field, (models.FloatField, models.DecimalField)):
            sql = "real"
        elif isinstance(db_field, (models.BigIntegerField, models.BigAutoField,
                                   models.SmallIntegerField, models.PositiveSmallIntegerField,
                                   models.IntegerField, models.PositiveIntegerField, models.AutoField,
                                   models.BooleanField, models.NullBooleanField)):
            sql = "integer"
        elif isinstance(db_field, models.DateTimeField):
            sql = "text(6)"
            is_str = True
        elif isinstance(db_field, models.DateField):
            sql = "text(6)"
            is_str = True
        elif isinstance(db_field, models.TimeField):
            sql = "text(6)"
            is_str = True
        elif isinstance(db_field, (models.FileField, models.ImageField)):
            sql = "text(%s)" % (db_field.max_length or 256)
            is_str = True

        elif isinstance(db_field, models.ForeignKey):
            db_field.target_field.default = db_field.default
            return self.make_field_sql(db_field.target_field, field_name, verbose_name,
                                       null=null, primary_key=False, row=row, add_field=add_field)

        elif isinstance(db_field, models.ManyToManyField):
            raise ValueError(u'没有支持ManyToManyField字段！')

        if null:
            sql = sql + " NULL"
        else:
            sql = sql + " NOT NULL"

        if ("NOT_PROVIDED" not in str(db_field.default)) and (not callable(db_field.default)):
            default = db_field.default
            if isinstance(db_field, (models.BooleanField, models.NullBooleanField)):
                default = int(db_field.default)

            if isinstance(db_field, (models.SmallIntegerField, models.PositiveSmallIntegerField,
                                     models.IntegerField, models.PositiveIntegerField, models.BigIntegerField)):
                default = int(db_field.default)

            if row and row[4] is not None:
                default = row[4]
                if isinstance(default, int):
                    if int(default) == default:
                        default = default
                elif isinstance(default, float):
                    if float(default) == default:
                        default = default

                elif default == default:
                    default = default

            if is_str:
                sql = sql + (" DEFAULT '%s'" % str(default).strip("'\""))

            else:
                sql = sql + (" DEFAULT %s" % default)

        if primary_key and isinstance(db_field, (models.BigAutoField, models.AutoField)):
            sql += " PRIMARY KEY AUTOINCREMENT"
        elif primary_key:
            sql += " PRIMARY KEY"

        if add_field:
            sql = "'%s' %s" % (field_name, sql)

        return sql

    def make_field_sql_by_db(self, row, db_table, add_field=True):
        field_name = row[1]
        field_type = row[2]
        not_null = row[3]
        default = row[4]
        primary_key = row[5]

        if add_field:
            sql = "'%s' %s" % (field_name, field_type)
        else:
            sql = field_type

        if not_null == 0:
            sql = sql + " NULL"
        else:
            sql = sql + " NOT NULL"

        if default:  # DEFAULT
            if field_type.find("integer") > -1 or field_type.find("real") > -1:
                sql = sql + (" DEFAULT %s" % default)
            else:
                sql = sql + (" DEFAULT '%s'" % str(default).strip("'\""))

        if primary_key:
            sql += " PRIMARY KEY"

            # 自增只能单独判断
            self.cursor.execute("SELECT * FROM sqlite_master WHERE type='table' AND tbl_name='%s';" % db_table)
            lst_table = self.cursor.fetchall()
            if lst_table:
                if (sql + " AUTOINCREMENT") in lst_table[0][4] or "":
                    sql += " AUTOINCREMENT"
        return sql

    def make_index(self, model):
        dict_sql = collections.OrderedDict()
        db_table = model._meta.db_table
        for db_field in model._meta.fields:
            if isinstance(db_field, models.ForeignKey):
                index_name = "%s_%s" % (db_table, db_field.get_attname())
                sql = 'INDEX "%s" ON "%s" ("%s")' % (index_name, db_table, db_field.get_attname())
                dict_sql[index_name] = sql
            elif not db_field.primary_key and db_field.unique:  # 主键在字段中修改
                index_name = "%s_%s" % (db_table, db_field.get_attname())
                sql = 'UNIQUE INDEX "%s" ON "%s" ("%s")' % (index_name, db_table, db_field.get_attname())
                dict_sql[index_name] = sql
            elif db_field.db_index:
                index_name = "%s_%s" % (db_table, db_field.get_attname())
                sql = 'INDEX "%s" ON "%s" ("%s")' % (index_name, db_table, db_field.get_attname())
                dict_sql[index_name] = sql

        if model._meta.unique_together and not isinstance(model._meta.unique_together[0], (tuple, list)):
            unique_together = [model._meta.unique_together, ]
        else:
            unique_together = model._meta.unique_together

        for unique in unique_together:
            if isinstance(unique, (tuple, list)):
                lst_field_name = []
                for field_name in unique:
                    field_name = model._meta.get_field(field_name).get_attname()
                    lst_field_name.append(field_name)
                index_name = "%s_%s" % (db_table,
                                        str(lst_field_name).strip("[]() ,'\"").replace(" ", "").
                                        replace(",", "_").replace("'", "").replace('"', ""))
                index_name = index_name[-64:]
                index_field = str(lst_field_name).strip("[]() ,").replace("'", '"').replace(" ", "")
                sql = 'UNIQUE INDEX "%s" ON "%s" (%s)' % (index_name, db_table, index_field)
                dict_sql[index_name] = sql

        return dict_sql

    def make_index_by_db(self, db_table):
        sql = "select * from sqlite_master where type='index' AND tbl_name='%s';" % db_table
        self.cursor.execute(sql)
        lst_row = self.cursor.fetchall()

        dict_sql = collections.OrderedDict()
        for row in lst_row:
            unique = False
            index_name = row[1]
            o_re = re.search("\((.*)\)", row[4] or "")
            if o_re:
                index_field = o_re.groups()[0]
            else:
                continue

            if " UNIQUE " in (row[4] or ""):
                unique = True

            if unique:
                sql = 'UNIQUE INDEX "%s" ON "%s" (%s)' % (index_name, db_table, index_field)
            else:
                sql = 'INDEX "%s" ON "%s" (%s)' % (index_name, db_table, index_field)

            dict_sql[index_name] = sql

        return dict_sql

    def make_m2m(self, model):
        db_table = model._meta.db_table
        for db_field in model._meta.local_many_to_many:
            if not hasattr(db_field, "target_field"):
                continue

            table_name = "%s_%s" % (db_table, db_field.name)
            field_name1 = "%s_id" % db_field.model.__name__.lower()
            field_name2 = "%s_id" % db_field.target_field.model.__name__.lower()
            model._meta.pk.name = field_name1
            model._meta.pk.primary_key = False
            db_field.target_field.name = field_name2
            db_field.target_field.primary_key = False

            sql = "select * from sqlite_master where type='index' AND tbl_name='%s';" % table_name
            self.cursor.execute(sql)
            lst_table = self.cursor.fetchall()
            if lst_table:
                self.update_table(table_name, [models.AutoField(name="id", primary_key=True),
                                               model._meta.pk, db_field.target_field])

                index_name = "%s_%s_%s" % (table_name, field_name1, field_name2)
                sql = 'CREATE UNIQUE INDEX "%s" ON "%s" ("%s","%s")' % (index_name, table_name,
                                                                        field_name1, field_name2)
                try:
                    self.cursor.execute(sql)
                    print(sql)
                except (BaseException,):
                    pass

                index_name = "%s_%s" % (table_name, field_name2)
                sql = 'CREATE INDEX "%s" ON "%s" (%s)' % (index_name, table_name, field_name2)
                try:
                    self.cursor.execute(sql)
                    print(sql)
                except (BaseException,):
                    pass
            else:
                self.create_table(table_name, [models.AutoField(name="id", primary_key=True),
                                               model._meta.pk, db_field.target_field])

                index_name = "%s_%s_%s" % (table_name, field_name1, field_name2)
                sql = 'CREATE UNIQUE INDEX "%s" ON "%s" ("%s","%s")' % (index_name, table_name,
                                                                        field_name1, field_name2)
                execute(self.cursor, sql)
                index_name = "%s_%s" % (table_name, field_name2)
                sql = 'CREATE INDEX "%s" ON "%s" (%s)' % (index_name, table_name, field_name2)
                execute(self.cursor, sql)
