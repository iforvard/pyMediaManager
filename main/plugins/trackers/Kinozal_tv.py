import requests
from bs4 import BeautifulSoup
from dateparser import parse
from pytz import utc


def params(key):
    plugin_params = {
        # Разрешение для работы без авторизации
        'parsing': True,
        'torrent_dw': False,
        # Наличие возможность скачать по магнет-ссылки
        'magnet_dw': False,
        # This name must match the name of the plugin file. Kinozal_tv.py => 'name': 'Kinozal_tv'
        # You cannot use a period in a name.
        'name': 'Kinozal_tv',
        'url_prefix': 'http://kinozal.tv/details.php?id='
    }
    return plugin_params[key]


def parser(page):
    url_dl = 'http://dl.kinozal.tv/download.php?id='
    url_topic = 'http://kinozal.tv/details.php?id='
    soup = BeautifulSoup(page, 'lxml')
    title = soup.find('li', {'class': 'img'}).a
    id_torrent = title['href'].split('=')[-1]
    img_url = title.img['src']
    if 'poster' in img_url:
        img_url = f'http://kinozal.tv{img_url}'
    full_name = title['title']
    tech_details = soup.find('ul', {'class': 'men w200'}).find_all("span", {'class': 'floatright green n'})
    size = tech_details[0].text
    if len(tech_details) == 3:
        # Проверка наличия даты изменения темы
        date_torrent = tech_details[2].text
    else:
        date_torrent = tech_details[1].text
    date_torrent = parse(date_torrent)
    date_torrent = utc.localize(date_torrent)

    media_cads = {
        'short_name': str(full_name).split(' /')[0],
        'full_name': full_name,
        'size': size.split('(')[0],
        'date_upd': date_torrent,
        'img_url': img_url,
        'magnet_url': '',
        'torrent_url': f'{url_dl}{id_torrent}',
        'url': f'{url_topic}{id_torrent}',
        'plugin_name': params('name')
    }
    return media_cads


def login(login_user, password_user):
    data = {
        'username': login_user,
        'password': password_user,
    }
    url_login = 'http://kinozal.tv/takelogin.php'
    with requests.Session() as session:
        session.post(
            url_login,
            data=data,
        )
        cookies = session.cookies.get_dict()
        if 'pass' in cookies and 'uid' in cookies:
            return cookies


if __name__ == '__main__':
    print(params('name'))