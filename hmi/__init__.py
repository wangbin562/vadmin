# !/usr/bin/python
# -*- coding=utf-8 -*-
# pylint: disable=C0111

from platform import platform
if "mac" in platform():
    import pymysql

    pymysql.install_as_MySQLdb()
# import MySQLdb
