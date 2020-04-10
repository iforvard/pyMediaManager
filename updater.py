import subprocess

# Обновление локального репозитария и heroku
git_pull = subprocess.call(f'git pull', shell=True)
git_push = subprocess.call('git push heroku master', shell=True)
open = subprocess.call('heroku open', shell=True)
