import traceback


def register(name=None, param=None,
             run_mode=None, cycle_mode=None, cycle_time=None,
             interval_begin_time=None, interval_time=None,
             max_run_number=None, max_log_number=None, enable=True):
    """
    name:任务名称
    param:定时任务参数
    run_mode:执行模式, ((1, '周期执行'), (2, '间隔执行'))
    cycle_mode:周期执行模式，(('year', '每年'), ('month', '每月'), ('week', '每周'), ('day', '每日'))
    cycle_time:周期执行时间
                        "每年：10-01 08:00:00"
                        "每月：01 08:00:00"
                        "每周：0 08:00:00 0-6:周一到周日"
                        "每天：08:00:00"

    interval_begin_time:间隔执行开始时间
    interval_time:间隔时间 单位：秒 可以使用计算模式，例如一小时：60 * 60 一天：24 * 60 * 60
    """
    from django.db.utils import ProgrammingError, OperationalError

    def fun(f):
        try:
            from timed_task.models import TimedTask
            script = "%s.%s" % (f.__module__, f.__name__)
            obj = TimedTask.objects.filter(script=script, param=param).first()
            if obj:
                # obj.name = name or script
                # obj.script = script
                # obj.param = param
                # obj.run_mode = run_mode or 1
                # obj.cycle_mode = cycle_mode
                # obj.cycle_time = cycle_time
                # obj.interval_begin_time = interval_begin_time
                # obj.interval_time = interval_time
                # obj.max_run_number = max_run_number
                # obj.max_log_number = max_log_number or 5
                # obj.del_flag = False
                # obj.save()
                pass
            else:
                TimedTask.objects.create(name=name or script, script=script,
                                         param=param, run_mode=run_mode or 1,
                                         cycle_mode=cycle_mode, cycle_time=cycle_time,
                                         interval_begin_time=interval_begin_time, interval_time=interval_time,
                                         max_run_number=max_run_number, max_log_number=max_log_number or 5,
                                         enable=enable)

        except ProgrammingError as e:
            pass

        except OperationalError as e:
            pass

        except (BaseException,):
            print(traceback.format_exc())
            # raise
            pass

        return f

    return fun


def add_task(name=None, script=None, param=None,
             run_mode=None, cycle_mode=None, cycle_time=None,
             interval_begin_time=None, interval_time=None,
             max_run_number=None, max_log_number=None,
             enable=None):
    from timed_task.models import TimedTask
    obj = TimedTask.objects.filter(script=script, param=param).first()
    if name is None:
        name = script

    if obj:
        obj.name = name or script
        obj.script = script
        obj.param = param
        obj.run_mode = run_mode or 1
        obj.cycle_mode = cycle_mode
        obj.cycle_time = cycle_time
        obj.interval_begin_time = interval_begin_time
        obj.interval_time = interval_time
        obj.max_run_number = max_run_number
        obj.max_log_number = max_log_number or 5
        obj.del_flag = False
        obj.enable = enable or obj.enable
        obj.save()
        pass
    else:
        TimedTask.objects.create(name=name or script, script=script,
                                 param=param, run_mode=run_mode or 1,
                                 cycle_mode=cycle_mode, cycle_time=cycle_time,
                                 interval_begin_time=interval_begin_time, interval_time=interval_time,
                                 max_run_number=max_run_number, max_log_number=max_log_number or 5,
                                 enable=enable or True)
