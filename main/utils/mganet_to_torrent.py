import asyncio

from magnet2torrent import Magnet2Torrent, FailedToFetchException


async def fetch_that_torrent(magnet_url):
    m2t = Magnet2Torrent(magnet_url, use_additional_trackers=True)
    try:
        filename, torrent_data = await m2t.retrieve_torrent()
        print(torrent_data)
        print(filename)
        return torrent_data, filename
    except FailedToFetchException:
        print("Failed")


def get_torrent_by_magnet(magnet_url):
    torrent_data, filename = asyncio.run(fetch_that_torrent(magnet_url))
    return [torrent_data]


if __name__ == '__main__':
    url = 'magnet:?xt=urn:btih:9A73039A6B17F27FFE33D5387E79F5A6137645F5&tr=http%3A%2F%2Fbt3.t-ru.org%2Fann%3Fmagnet&dn=%D0%9B%D1%83%D1%87%D1%88%D0%B5%20%D0%B7%D0%B2%D0%BE%D0%BD%D0%B8%D1%82%D0%B5%20%D0%A1%D0%BE%D0%BB%D1%83%20%2F%20Better%20Call%20Saul%20%2F%20%D0%A1%D0%B5%D0%B7%D0%BE%D0%BD%3A%205%20%2F%20%D0%A1%D0%B5%D1%80%D0%B8%D0%B8%3A%201-9%20%D0%B8%D0%B7%2010%20(%D0%92%D0%B8%D0%BD%D1%81%20%D0%93%D0%B8%D0%BB%D0%BB%D0%B8%D0%B3%D0%B0%D0%BD%2C%20%D0%A2%D0%BE%D0%BC%D0%B0%D1%81%20%D0%A8%D0%BD%D0%B0%D1%83%D0%B7%2C%20%D0%9F%D0%B8%D1%82%D0%B5%D1%80%20%D0%93%D1%83%D0%BB%D0%B4)%20%5B2020%2C%20%D0%A1%D0%A8%D0%90%2C%20%D0%94%D1%80%D0%B0%D0%BC%D0%B0%2C%20%D0%BA%D1%80%D0%B8%D0%BC%D0%B8%D0%BD%D0%B0%D0%BB%2C%20WEBRip%201080p'
    get_torrent_by_magnet(url)