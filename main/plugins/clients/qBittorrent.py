from qbittorrent import Client

from ...pmm_exception import *


def params(key):
    plugin_params = {
        'auth_required': False,
        # This name must match the name of the plugin file. qBittorrent.py => 'name': 'qBittorrent'
        'name': 'qBittorrent',
    }
    return plugin_params[key]


def dw_torrent(torrents, magnet_urls, host, login, password):
    qb = Client(f'http://{host}/')
    qb.login(login, password)
    if qb._is_authenticated:
        qb.download_from_file(torrents)
        qb.download_from_link(magnet_urls)
    else:
        raise NotTorrentClient
