# !/usr/bin/python
# -*- coding=utf-8 -*-
import json
import traceback


def register(desc="", method="GET", param_desc=None, result_desc=None):
    """
    desc:接口说明
    method:POST或GET
    # "paramType":"form或path",
    param_desc:[{"name":"参数名称", "desc":"参数说明", "type":"参数类型str、int、bool、float、password、file、date、time、datetime",
    "default":"默认值","required":"True或False", "param_type":""}]
    result_desc:返回值说明，字符串或字符串数组
    """
    from django.db.utils import ProgrammingError, OperationalError

    def fun(f):
        try:
            from vadmin_standard.models import Api
            param = None
            if param_desc:
                param = json.dumps(param_desc, ensure_ascii=False)

            result = None
            if result_desc:
                if isinstance(result_desc, (tuple, list)):
                    result = json.dumps(result_desc, ensure_ascii=False)
                else:
                    result = json.dumps([result_desc], ensure_ascii=False)

            obj = Api.objects.filter(module=f.__module__, name=f.__name__).first()
            if obj:
                obj.desc = desc
                obj.method = method.upper()
                obj.param = param
                obj.result = result
                obj.del_flag = False
                obj.save()
            else:
                Api.objects.create(module=f.__module__, name=f.__name__,
                                   desc=desc, method=method.upper(), param=param, result=result)

        except ProgrammingError as e:
            pass
        except OperationalError as e:
            pass
        except (BaseException,):
            print(traceback.format_exc())

        return f

    return fun
