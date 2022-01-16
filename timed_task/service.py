# !/usr/bin/python
# -*- coding=utf-8 -*-
import datetime
import importlib
import json
import logging
import os
import traceback
from concurrent.futures import ThreadPoolExecutor

from django.conf import settings

from timed_task.models import TimedTask
from vadmin import const
from vadmin import step
from vadmin.json_encoder import Encoder

logger = logging.getLogger(__name__)


def run_task_complete(res):
    script, path, begin_time = res.param
    try:
        exception_log = res.exception()
        obj = TimedTask.objects.filter(script=script).first()
        if obj:
            obj.last_run_time = datetime.datetime.now()
            obj.last_exception_log = exception_log
            obj.last_begin_time = begin_time
            obj.last_end_time = obj.last_run_time
            obj.save()

        result = [step.ViewOpera(), step.Msg(text="执行完成！")]
    except BaseException as e:
        s_err_info = traceback.format_exc()
        logger.error(s_err_info)
        result = step.Msg(text="执行错误，错误信息：%s！" % e.args)

    open(path, "w").write(json.dumps(result, ensure_ascii=False, cls=Encoder))


def run_task_sync(request):
    script = request.GET["script"].strip()
    lst_interface = script.split(".")
    o_module = importlib.import_module(".".join(lst_interface[0:-1]))
    fun = getattr(o_module, lst_interface[-1])

    path = os.path.join(settings.MEDIA_ROOT, "%s.txt" % (script.replace(".", "_")))
    if os.path.exists(path):
        os.remove(path)

    begin_time = datetime.datetime.now()
    pool = ThreadPoolExecutor(100)
    f = pool.submit(fun, request)
    # f = pool.submit(fun)
    f.param = [script, path, begin_time]
    f.add_done_callback(run_task_complete)

    url = const.URL_RUN_SCRIPT % ("timed_task.service.run_task_check?path=" + path)
    return step.RequestAsync(url=url)


def run_task_check(request):
    result_file = request.GET["path"]
    if os.path.exists(result_file):
        result = open(result_file, "r").read()
        result = json.loads(result)

        try:
            os.remove(result_file)
        except (BaseException,):
            pass

        return result
