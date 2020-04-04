from apscheduler.schedulers.blocking import BlockingScheduler
import subprocess

sched = BlockingScheduler()

# Интервал можно указать разными параметрами см. https://apscheduler.readthedocs.io/en/latest/modules/triggers/cron.html
@sched.scheduled_job('interval', days=1)
def timed_job():
    # iforvard - нужно заменить на логин пользователя в системе,
    # Если после проверки обновлений требуется загрузка нужно добавить -dw.
    bashCommand = "python3 manage.py check_torrents iforvard"
    subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE)
    print(f'Выполненна команда {bashCommand}')


sched.start()
