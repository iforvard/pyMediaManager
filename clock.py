import os
import subprocess
from datetime import datetime, timedelta

from apscheduler.schedulers.blocking import BlockingScheduler

sched_time_sec = os.environ.get('SCHED_TIME_SEC', 1)
sched_time_min = float(os.environ.get('SCHED_TIME_MIN', 180))
sched_time_hour = float(os.environ.get('SCHED_TIME_HOUR', 3))
sched = BlockingScheduler()


# Интервал можно указать с разными параметрами:
# https://apscheduler.readthedocs.io/en/latest/modules/triggers/cron.html
# https://apscheduler.readthedocs.io/en/stable/modules/triggers/interval.html
@sched.scheduled_job(
    'interval',
    # seconds=sched_time_sec,
    # minutes=sched_time_min,
    hours=sched_time_hour,
)
def timed_job():
    # iforvard - нужно заменить на логин пользователя в системе,
    # Если после проверки обновлений требуется загрузка в bashCommand нужно добавить -dw.
    bashCommand = "python3 manage.py check_torrents iforvard"
    subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE)
    print(f'Выполненна команда {bashCommand}')
    sched_next_time = datetime.now() + timedelta(hours=sched_time_hour)
    print(f'Следущуая итерация через {sched_time_hour} час(а), в {sched_next_time}')


sched.start()
