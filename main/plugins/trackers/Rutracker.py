import requests
from bs4 import BeautifulSoup
from dateparser import parse
from pytz import utc


def params(key):
    plugin_params = {
        'auth_required': False,
        # This name must match the name of the plugin file. Rutracker.py => 'name': 'Rutracker'
        'name': 'Rutracker',
        'url_prefix': 'https://rutracker.org/forum/viewtopic.php?t='
    }
    return plugin_params[key]


async def login_(session, login_user, password_user):
    url_login = 'https://rutracker.org/forum/login.php'
    data = {
        "login_username": login_user,
        "login_password": password_user,
        "login": 'вход',
    }
    async with session.post(url_login, data=data) as response:
        if response.status == 200:
            response = await response.text()
            if login_user in response:
                cookies = {}
                for cookie in session.cookie_jar:
                    cookies[cookie.key] = cookie.value
                return cookies


def parser(page):
    size = None
    url_dl = 'https://rutracker.org/forum/dl.php?t='
    soup = BeautifulSoup(page, 'lxml')
    date_torrent = soup.find('span', {'class': 'posted_since hide-for-print'}).string
    date_torrent = date_torrent.replace(')', '').replace(')', '')
    if 'ред' not in date_torrent:
        date_torrent = soup.find('a', {'class': 'p-link small'}).string
    else:
        date_torrent = date_torrent.split('ред. ')[-1]
    date_torrent = parse(date_torrent)
    date_torrent = utc.localize(date_torrent)

    name_media_content = soup.find('meta', {'name': 'description'})['content']

    link = soup.find('ul', {'class': 'inlined middot-separated'})
    for index, ul in enumerate(link):
        if index == 3:
            size = ul.string.replace('\xa0', ' ')
    if not size:
        size = soup.find('span', {'id': 'tor-size-humn'}).string.replace('\xa0', ' ')
    magnet_url = soup.find('a', {'class': 'magnet-link'})['href']
    img = soup.find('var', {'class': 'postImg postImgAligned img-right'})['title']
    torrent_url = soup.find('link', {'rel': 'canonical'})['href']
    id_torrent = torrent_url.split('=')[-1]

    media_cads = {
        'short_name': str(name_media_content).split(' /')[0],
        'full_name': name_media_content,
        'size': size,
        'date_upd': date_torrent,
        'img_url': img,
        'magnet_url': magnet_url,
        'torrent_url': f'{url_dl}{id_torrent}',
        'url': torrent_url,
        'plugin_name': params('name')
    }
    return media_cads


def login(login_user, password_user):
    data = {
        'login_username': login_user,
        'login_password': password_user,
        'login': 'вход',
    }
    url_login = 'https://rutracker.org/forum/login.php'
    with requests.Session() as session:
        session.post(
            url_login,
            data=data,
        )
        cookies = session.cookies.get_dict()
        if 'bb_session' in cookies:
            return cookies
