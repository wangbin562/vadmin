# !/usr/bin/python
# -*- coding=utf-8 -*-
import datetime
import importlib
import logging
import os
import traceback
import zipfile

import shell
from django.conf import settings

from timed_task import task

logger = logging.getLogger(__name__)


@task.register(name="备份数据库", cycle_mode="day", cycle_time="01:00:00")
def backup_db(request=None):
    try:
        backup_count = 10
        path = os.path.join(settings.MEDIA_ROOT, "backup")  # 根目录，如果空间不够可以修改此目录
        if not os.path.exists(path):
            os.makedirs(path)

        files = []
        for file_name in os.listdir(path):
            path_name = os.path.join(path, file_name)
            if os.path.isfile(path_name) and file_name.find("backup_db") == 0:
                files.append(file_name)

        if len(files) >= backup_count:
            files.sort()
            path_name = os.path.join(path, files[0])
            try:
                os.remove(path_name)
            except (BaseException,):
                s_err_info = traceback.format_exc()
                logger.error(s_err_info)

        now = datetime.datetime.now()
        file_sql = "backup_db_%s.sql" % now.strftime('%Y%m%d%H%M%S')
        path_name = os.path.join(path, file_sql)

        export = False
        try:
            cmd = "mysqldump -u'%s' -h%s -p'%s' %s > %s" % \
                  (settings.DB_USER, settings.HOST, settings.DB_PWD, settings.DB_NAME, path_name)
            r = shell.shell(cmd)
            errors = r.errors()
            if errors:
                logger.error("\r\n".join(errors))
            else:
                export = True

        except (BaseException,):
            logger.error(traceback.format_exc())

        if not export:
            try:
                cmd = "python3 manage.py dumpdata -o %s" % path_name
                r = shell.shell(cmd)
                errors = r.errors()
                if errors:
                    logger.error("\r\n".join(errors))
                else:
                    export = True
            except (BaseException,):
                logger.error(traceback.format_exc())

        if not export:
            lst_sql = []
            for app in settings.INSTALLED_APPS:
                try:
                    module = importlib.import_module("%s.models" % app)
                except (BaseException,):
                    continue

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

                        for obj in model.objects.all():
                            obj.db_2_sql(lst_sql)

                    except (BaseException,):
                        logger.info(traceback.format_exc())

            open(path_name, "w").write("\r\n".join(lst_sql))

        zip_path = os.path.join(path, "backup_db_%s.zip" % now.strftime('%Y%m%d%H%M%S'))
        z = zipfile.ZipFile(zip_path, mode="w", compression=zipfile.ZIP_DEFLATED)
        z.write(path_name, file_sql)
        z.close()
        os.remove(path_name)

    except (BaseException,):
        s_err_info = traceback.format_exc()
        # print(s_err_info)
        logger.error(s_err_info)
