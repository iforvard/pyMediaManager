import requests
from bs4 import BeautifulSoup
from dateparser import parse


def params(key):
    plugin_params = {
        # Разрешение для работы без авторизации
        'parsing': True,
        'torrent_dw': False,
        # Наличие возможность скачать по магнет-ссылки
        'magnet_dw': False,
        # This name must match the name of the plugin file. Lostfilm_tv.py => 'name': 'Lostfilm_tv'
        # You cannot use a period in a name.
        'name': 'Lostfilm_tv',
        'url_prefix': 'https://www.lostfilm.tv/series/'
    }
    return plugin_params[key]


def parser(page):
    url_topic = 'https://www.lostfilm.tv'
    soup = BeautifulSoup(page, 'lxml')
    last_row = 0

    url = soup.find("div", class_="menu-pane").a['href']
    full_name = soup.find('title').text.split('.')[0]

    future_row = soup.find('tr', {'class': 'not-available'})
    if future_row:
        last_row = 1
    tables = soup.find('table').find_all('tr')
    date_raw = tables[last_row].find("td", class_="delta").text
    date_torrent = date_raw.replace('Ru: ', '').split('Eng')[0]
    print(date_torrent)
    date_torrent = parse(
        date_torrent,
        date_formats=['%d.%m.%Y'],
        settings={'TIMEZONE': 'UTC', 'RETURN_AS_TIMEZONE_AWARE': True})
    series_id = soup.select('[data-episode]')[0]['data-code'].split('-')
    img_url = f'http://static.lostfilm.tv/Images/{series_id[0]}/Posters/shmoster_s{series_id[1]}.jpg'
    media_cads = {
        'short_name': full_name,
        'full_name': full_name,
        'size': '0',
        'date_upd': date_torrent,
        'img_url': img_url,
        'magnet_url': '',
        'torrent_url': '',
        'url': f'{url_topic}{url}',
        'plugin_name': params('name')
    }
    return media_cads


def login(login_user, password_user):
    # Только парсер без загрузки торрента
    return {}


if __name__ == '__main__':
    url = 'https://www.lostfilm.tv/series/Better_Call_Saul'
    r = requests.get(url)
    print(parser(r.text))
