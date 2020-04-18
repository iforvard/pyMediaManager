import asyncio

from magnet2torrent import Magnet2Torrent, FailedToFetchException


class M2T(Magnet2Torrent):
    def _parse_url(self):
        infohash, trackers, name = super(M2T, self)._parse_url()
        try:
            name = name.decode()
        except AttributeError:
            pass
        return infohash, trackers, name


async def fetch_that_torrent(magnet_url):
    m2t = M2T(magnet_url, use_additional_trackers=True)
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
    url2 = 'magnet:?xt=urn:btih:CDF061D07C52B180C365598D22BFD42BB24FCEFD&tr=http%3A%2F%2Fbt4.t-ru.org%2Fann%3Fmagnet'
    url = 'magnet:?xt=urn:btih:108F8A6F1F72C30E56F5259CF28ECCEA1FE76812&tr=http%3A%2F%2Fbt4.t-ru.org%2Fann%3Fmagnet'
    print(get_torrent_by_magnet(url2))
