import asyncio

from magnet2torrent import Magnet2Torrent, FailedToFetchException


async def fetch_that_torrent(magnet_url):
    m2t = Magnet2Torrent(magnet_url, use_additional_trackers=True)
    try:
        torrent = await m2t.retrieve_torrent()
        return torrent
    except FailedToFetchException:
        print("Failed")
        return False, False


def get_torrent_by_magnet(magnet_url):
    filename, torrent_data = asyncio.run(fetch_that_torrent(magnet_url))
    return torrent_data


if __name__ == '__main__':
    url2 = 'magnet:?xt=urn:btih:0B1D71D2FB727019CB1DE91909CF3A6EF3E83DEA&tr=http%3A%2F%2Fbt.t-ru.org%2Fann%3Fmagnet&dn=%D0%9D%D0%BE%D0%B2%D1%8B%D0%B9%20%D0%9F%D0%B0%D0%BF%D0%B0%20%2F%20The%20New%20Pope%20%2F%20%D0%A1%D0%B5%D0%B7%D0%BE%D0%BD%3A%201%20%2F%20%D0%A1%D0%B5%D1%80%D0%B8%D0%B8%3A%201-9%20%D0%B8%D0%B7%209%20(%D0%9F%D0%B0%D0%BE%D0%BB%D0%BE%20%D0%A1%D0%BE%D1%80%D1%80%D0%B5%D0%BD%D1%82%D0%B8%D0%BD%D0%BE)%20%5B2020%2C%20%D0%A1%D0%A8%D0%90%2C%20%D0%94%D1%80%D0%B0%D0%BC%D0%B0%2C%20WEB-DL%201080p%20ivi%5D%20Dub%20(Kravec)%2C%20MVO%20(AMEDIA%20%2F%20Greb%26CGC)%20%2B'
    url = 'magnet:?xt=urn:btih:108F8A6F1F72C30E56F5259CF28ECCEA1FE76812&tr=http%3A%2F%2Fbt4.t-ru.org%2Fann%3Fmagnet'
    print(get_torrent_by_magnet(url2))
