# !/usr/bin/python
# -*- coding=utf-8 -*-
"""
ver 1.6
"""

import time
import pickle
from pymemcache.client.base import Client

try:
    from django.core.cache import cache
except (BaseException,):
    pass

from platform import platform

if 'centos' in platform():
    MEM_CACHE = True
else:
    MEM_CACHE = False

MEM_CACHE_ADDRESS = ('127.0.0.1', 11211)

FIELD_KEY_SEPARATOR = "-"
FIELD_VAL_SEPARATOR = ":"

g_timeout = 300  # 5分钟


def set(key, val, server=None, is_mem_cache=True, timeout=g_timeout):
    """
    单独使用时无法用django cache,直接存到内存中(默认永不超时）
    """
    if is_mem_cache:
        if server is None:
            server = MEM_CACHE_ADDRESS

        client = Client(server, allow_unicode_keys=True)
        buf = pickle.dumps(val, pickle.HIGHEST_PROTOCOL)
        client.set(key, buf, expire=timeout or 0, noreply=False)  # expire默认300秒， =None永不超时
        client.close()
    else:
        cache.set(key, val, timeout=timeout)  # timeout默认默认300秒， =None永不超时


def get(key, default=None, i_loop=2, server=None, is_mem_cache=True):
    ret_val = default
    if is_mem_cache:
        if server is None:
            server = MEM_CACHE_ADDRESS

        # 有时候大量数据连接时会异常，多试几次保存正确
        for i in range(i_loop + 1):
            try:
                client = Client(server, allow_unicode_keys=True)
                val = client.get(key)
                if val is None:
                    ret_val = val
                else:
                    ret_val = pickle.loads(val)
                client.close()
                break

            except (BaseException,):
                time.sleep(0.1)
                if i >= i_loop:
                    raise

    else:
        ret_val = cache.get(key, default)

    return ret_val


def delete(key, server=None, is_mem_cache=True):
    """
    删除缓存
    :param key:
    :return:
    """
    if is_mem_cache:
        if server is None:
            server = MEM_CACHE_ADDRESS
        client = Client(server, allow_unicode_keys=True)
        client.delete(key, noreply=False)
        client.close()

    else:
        cache.delete(key)


class CacheTable(object):
    """
    数据表缓存基类, 缓存django models对象
    不支持批处理，对应数据库的批处理，请在外部处理
    例如：
    try:

        o_cache_1 = CacheTable(Model)
        o_cache_2 = CacheTable(Model)
        '''
        此外修改对象
        '''
        # 下面批处理异常，数据库会回滚，但缓存没有回滚功能
        with transaction.atomic():
            o_cache_1.save()
            o_cache_2.save()
    except:
        # 所以要在此处，清空对应缓存
        o_cache_1.clear_table()
        o_cache_2.clear_table()
    """
    CACHE_KEY = ""  # 缓存一级关键字

    def __init__(self, models_class=None, is_mem_cache=MEM_CACHE):
        self.key = None
        self.models_class = models_class
        self.is_mem_cache = is_mem_cache

        # 本地缓存关键字是二级， memchache关键字是一级
        if models_class is None:
            class_name = self.__class__.__name__
        else:
            class_name = models_class._meta.db_table

        self.table_key = "%s%s" % (CacheTable.CACHE_KEY, class_name)
        self.mem_key = None

        if self.is_mem_cache:
            self.client = Client(MEM_CACHE_ADDRESS, allow_unicode_keys=True)

        self.obj = None
        # self.filter_kwargs = None
        self.is_single_obj = False

    def set_key(self, key):
        key = key.replace(" ", "")  # key不能有空格
        self.key = key
        if self.is_mem_cache:
            self.mem_key = "%s=%s" % (self.table_key, key)

    def _set_key(self, dict_key):
        key = FIELD_KEY_SEPARATOR.join(dict_key.keys())
        val = FIELD_KEY_SEPARATOR.join(map(str, dict_key.values()))
        self.set_key("%s%s%s" % (key, FIELD_VAL_SEPARATOR, val))

    def __del__(self):
        if self.is_mem_cache:
            self.client.close()

    def _set_table_key(self, **kwargs):
        if self.is_mem_cache:
            buf = self.client.get(self.table_key)

            key = FIELD_KEY_SEPARATOR.join(kwargs.keys())
            val = FIELD_KEY_SEPARATOR.join(map(str, kwargs.values()))

            if buf is not None:
                dict_field_key = pickle.loads(buf)
                if key in dict_field_key:
                    if val not in dict_field_key[key]:
                        dict_field_key[key].append(val)
                else:
                    dict_field_key[key] = [val, ]

                buf = pickle.dumps(dict_field_key, pickle.HIGHEST_PROTOCOL)
                try:
                    self.client.set(self.table_key, buf)

                except (BaseException,):
                    # 表关键字维护超过最大缓存存储，清空所有缓存
                    self.clear_table()
                    self.client.set(self.table_key, buf, noreply=False)
            else:
                dict_field_key = {key: [val, ]}
                buf = pickle.dumps(dict_field_key, pickle.HIGHEST_PROTOCOL)
                self.client.set(self.table_key, buf)

    def _set(self, obj, **kwargs):
        if self.is_mem_cache:
            self._set_table_key(**kwargs)  # 不管是否成功，先设置表查询子项维护项
            buf = pickle.dumps(obj, pickle.HIGHEST_PROTOCOL)
            self.client.set(self.mem_key, buf, expire=g_timeout, noreply=False)  # 有可能不成功，下次还是在数据库中查询
        else:
            dict_table = cache.get(self.table_key)
            if dict_table is None:
                dict_table = {}

            dict_table[self.key] = obj
            cache.set(self.table_key, dict_table, timeout=g_timeout)

    def _get(self):
        ret_val = None
        if self.is_mem_cache:
            val = self.client.get(self.mem_key)
            if val is not None:
                ret_val = pickle.loads(val)

        else:
            val = None
            dict_table = cache.get(self.table_key)
            if (dict_table is not None) and (self.key in dict_table):
                val = dict_table[self.key]

            ret_val = val

        return ret_val

    def query_first(self, lst_order=None, **kwargs):
        if kwargs == {}:
            raise ValueError(u'不能在缓存中全量查询！')

        self.is_single_obj = True
        if kwargs:
            # self.filter_kwargs = kwargs
            self._set_key(kwargs)
        self.obj = self._get()

        if self.obj is None:
            if lst_order is None:
                self.obj = self.models_class.objects.filter(**kwargs).first()
            else:
                if isinstance(lst_order, type(str)):
                    lst_order = [lst_order, ]
                self.obj = self.models_class.objects.filter(**kwargs).order_by(*lst_order).first()

            if self.obj is not None:
                if kwargs:
                    self._set(self.obj, **kwargs)
                return self.obj

        return self.obj

    def query(self, lst_order=None, **kwargs):
        if kwargs == {}:
            raise ValueError(u'不能在缓存中全量查询！')

        self.is_single_obj = False
        # self.filter_kwargs = kwargs
        self._set_key(kwargs)
        self.obj = self._get()

        if self.obj is None:
            if lst_order is None:
                self.obj = list(self.models_class.objects.filter(**kwargs))
            else:
                if isinstance(lst_order, type(str)):
                    lst_order = [lst_order, ]
                self.obj = list(self.models_class.objects.filter(**kwargs).order_by(*lst_order))

            # 最大长度小于30个
            if (self.obj is not None) and (len(self.obj) < 30):
                self._set(self.obj, **kwargs)
                return self.obj

        return self.obj

    def clear(self):
        """
        清空当前查询(数据表带条件的查询）
        :return:
        """
        if self.is_mem_cache:
            # self.client.flush_all()
            if self.mem_key:
                self.client.delete(self.mem_key, noreply=False)
        else:
            cache.delete(self.table_key)

    def clear_all(self):
        """
        清空所有
        :return:
        """
        if self.is_mem_cache:
            # self.client.flush_all(noreply=False)
            self.client.quit()
        else:
            cache.clear()

    def clear_table(self):
        """
        清空表
        :return:
        """
        if self.is_mem_cache:
            # table_key = "%s-" % self.cache_key
            # table_key = bytes(table_key, "utf-8")
            # dict_item = self.client.stats("items")
            # for item_key in dict_item.keys():
            #     if b"number" not in item_key:
            #         continue
            #
            #     key1, key2, key3 = item_key.split(b":")
            #     dict_val = self.client.stats("cachedump", key2, "0")
            #     for key in dict_val.keys():
            #         if key.find(table_key) == 0:
            #             self.client.delete(key, noreply=False)

            buf = self.client.get(self.table_key)

            if buf is not None:
                dict_field_key = pickle.loads(buf)
                for key, lst_val in dict_field_key.items():
                    for val in lst_val:
                        item_key = "%s=%s%s%s" % (self.table_key, key, FIELD_VAL_SEPARATOR, val.replace(" ", ""))
                        self.client.delete(item_key, noreply=False)

                self.client.delete(self.table_key, noreply=False)
        else:
            cache.delete(self.table_key)

    def clear_table_by_name(self, table_name):
        """
        :param table_name:
        :return:
        """
        self.table_key = "%s%s" % (CacheTable.CACHE_KEY, table_name)
        self.clear_table()


def clear_table(model_class):
    CacheTable(model_class).clear_table()


def clear_table_by_name(table_name):
    CacheTable().clear_table_by_name(table_name)


def clear_all():
    try:
        CacheTable().clear_all()
    except (BaseException,):
        pass
