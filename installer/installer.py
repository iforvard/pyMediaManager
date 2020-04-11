import subprocess
from subprocess import PIPE, STDOUT
from sys import platform
import os
import time
import random


# subprocess.check_output('heroku login', input='y', encoding='utf-8', shell=True)
# r = subprocess.check_output('git --version', shell=True, encoding='utf-8',)
def get_secret_key():
    return ''.join(
        random.SystemRandom().choice('abcdefghijklmnopqrstuvwxyz0123456789') for i in range(50))


def check_requirements():
    git_ver = subprocess.call('git --version', shell=True)
    heroku_ver = subprocess.call('heroku --version', shell=True)
    clear_console()
    if git_ver:
        print('Установите git себе на компьютер. https://git-scm.com/downloads', end='\n\n')
    if heroku_ver:
        print('Необходимо зарегистрироваться на Heroku и установить Heroku CLI.')
        print('https://devcenter.heroku.com/articles/heroku-cli#download-and-install', end='\n\n')
    if not git_ver and not heroku_ver:
        return True


def clear_console():
    if platform == 'win32':
        os.system('cls')
    else:
        os.system('clear')


if not check_requirements():
    input('Для повторной проверки перезапустите программу')
    exit(0)
clone_repository = subprocess.call('git clone https://github.com/iforvard/pyMediaManager.git', shell=True)
os.chdir('pyMediaManager')

ps = subprocess.Popen('heroku login', shell=True, stdin=PIPE, stdout=PIPE)
output, _ = ps.communicate(b'y')
create_app_status = 1
while create_app_status:
    print('Введите любое имя приложения на английском или оставьте пустым и система создаст его автоматически.')
    name_app = input('После ввода нажмите "Enter"\n')
    ps = subprocess.call(f'heroku create {name_app} --region eu', shell=True)
    if not ps:
        create_app_status = False
        break
    print(f'Имя {name_app} - Занято!')

git_push = subprocess.call('git push heroku master', shell=True)
migrate = subprocess.call('heroku run python manage.py migrate', shell=True)
print('Создаем администратора (супер-юзера)')
createsuperuser = subprocess.call('heroku run python manage.py createsuperuser', shell=True)
off_DEBUG = subprocess.call('heroku config:set DJANGO_DEBUG=', shell=True)

add_SECRET_KEY = subprocess.call(f'heroku config:set DJANGO_SECRET_KEY={get_secret_key()}', shell=True)
while add_SECRET_KEY:
    add_SECRET_KEY = subprocess.call(f'heroku config:set DJANGO_SECRET_KEY={get_secret_key()}', shell=True)
    time.sleep(1)
open = subprocess.call('heroku open', shell=True)
