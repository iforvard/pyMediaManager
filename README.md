# pyMediaManager.
pyMediaManager - менеджер торрент клиентов и трекеров.  
Django-приложение(web-сайт) написанное на python. Отслеживает темы(kinozal.tv, rutracker) и отправляет обновленные торренты через api qbittorrent и uTorrent.*
В pyMediaManager есть возможность проверки и загрузки как вручную(через веб-сайт) так и автоматически с любым интервалом, см. cron-файл `clock.py`

*в pyMediaManager реализована система плагинов, что дает возможность дополнить список как торрент трекеров для проверки так и торрент клиентов для загрузки.  
** Загрузка и проверка реализована через асинхронную библиотеку [aiohttp], что позволяет практически мгновенно проверять и загружать большое количество страниц с торрентами и торрент-файлов.  

Проверить работу можете на https://pymediamanager.herokuapp.com:  
логин - `demo-user`
пароль - `demo-password`  

[Видео-демонстрация]
# Установка на [Heroku]:  
_Предварительно необходимо зарегистрироваться на [Heroku] и установить [Heroku CLI]._  
_Установите git себе на компьютер (Вы можете найти версию для своей платформы [здесь])._

# Windows-installer.
Авто-установка через [Windows installer]  
1. Скачайте и запустите установщик в папке где планируете хранить копию вашего сайта.
2. В процессе установки программа запросит ввести имя для программы и логин/пароль для администратора.

# Ручная установка.
1. Откройте командную строку (или терминал) и выполните в нём следующую команду:  
`git clone https://github.com/iforvard/pyMediaManager.git`  
Это создаст подпапку (с содержанием вашего репозитория и именем вашего репозитория) внутри папки, в котрой выполнялась команда.
2. Перейдите в эту папку:  
`cd pyMediaManager`  
3. Входим в Heroku CLI:  
`heroku login`  
4. Создаем приложение:  
Взамен 'pymediamanager' Вам нужно указать любое имя или оставить пустым и система создаст его автоматически. Это требуется для создания доменного имени,  прим. [pymediamanager.herokuapp.com]   
`heroku create pymediamanager --region eu`  
5. Затем мы можем подтолкнуть наше приложение в репозиторий heroku как показано ниже. Это позволит загрузить приложение, упаковать его в dyno, запустить collectstatic, и запустить сам сайт.  
`git push heroku master`
6. Создаем базу данных  
`heroku run python manage.py migrate`
7. Создаем администратора (супер-юзера)  
`heroku run python manage.py createsuperuser`
8. Добавлям в список хостов адресс приложения:  
'pymediamanager' - замените на имя вашего приложения  
`heroku config:set DJANGO_CLOUD_HOST=pymediamanager.herokuapp.com`
9. Теперь можно проверить работу сайта  
`heroku open`

# Дополнительные настройки для безопастности
1.  Секретный ключ должен быть действительно секретным! Один из способов генерации:  
1.1  heroku run python manage.py shell  
1.2  from django.core.management.utils import get_random_secret_key  
1.3  get_random_secret_key()  
1.4  exit()  
1.5 Полученный ключ длинной 50 символов нужно добавить в систему:  
SECRET_KEY - замените на полученный ранее ключ  
`heroku config:set DJANGO_SECRET_KEY="SECRET_KEY"`  
2. Для отключения режима отладки передаем значение без параметров:  
`heroku config:set DJANGO_DEBUG=`  
3. Клиент Heroku предоставляет несколько инструментов для отладки:  
`heroku logs`  # Show current logs  
`heroku logs --tail` # Show current logs and keep updating with any new results  
`heroku config:set DEBUG_COLLECTSTATIC=1` # Add additional logging for collectstatic (this tool is run automatically during a build)  
`heroku ps`   #Display dyno status  
4. Запуск автоматической проверки и загрузки:
Предварительно изучите файл `clock.py`  
`heroku ps:scale clock=1`
  
[heroku]: https://www.heroku.com
[здесь]: https://git-scm.com/downloads
[Heroku CLI]: https://devcenter.heroku.com/articles/getting-started-with-python#set-up
[aiohttp]: https://aiohttp.readthedocs.io/en/stable/
[Видео-демонстрация]: https://www.youtube.com/watch?v=milw1dDt9dk
[pymediamanager.herokuapp.com]: https://pymediamanager.herokuapp.com
[Windows installer]: https://github.com/iforvard/pyMediaManager/blob/master/installer/installer.exe