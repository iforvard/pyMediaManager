import os
import subprocess

from apscheduler.schedulers.blocking import BlockingScheduler

sched_time_sec = os.environ.get('SCHED_TIME_SEC', 1)
sched_time_min = os.environ.get('SCHED_TIME_MIN', 1)
sched_time_hour = os.environ.get('SCHED_TIME_HOUR', 2)
sched = BlockingScheduler()


# Интервал можно указать с разными параметрами:
# https://apscheduler.readthedocs.io/en/latest/modules/triggers/cron.html
# https://apscheduler.readthedocs.io/en/stable/modules/triggers/interval.html
@sched.scheduled_job(
    'interval',
    seconds=sched_time_sec,
    minutes=sched_time_min,
    hours=sched_time_hour,
)
def timed_job():
    # iforvard - нужно заменить на логин пользователя в системе,
    # Если после проверки обновлений требуется загрузка в bashCommand нужно добавить -dw.
    bashCommand = "python3 manage.py check_torrents iforvard"
    subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE)
    print(f'Выполненна команда {bashCommand}')


sched.start()
