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


def get_torrent_by_magnet(magnet_url):
    filename, torrent_data = asyncio.run(fetch_that_torrent(magnet_url))
    print(filename)
    return [torrent_data]


if __name__ == '__main__':
    url2 = 'magnet:?xt=urn:btih:0CC4F994665E9CA6CBFD9DD794C60BE684FF2175&tr=http%3A%2F%2Fbt.t-ru.org%2Fann%3Fmagnet&dn=%D0%A0%D0%B8%D0%BA%D0%BE%D1%88%D0%B5%D1%82%20%2F%20%D0%A1%D0%B5%D1%80%D0%B8%D0%B8%3A%201-16%20%D0%B8%D0%B7%2016%20(%D0%94%D0%B5%D0%BD%D0%B8%D1%81%20%D0%9A%D0%B0%D1%80%D1%8B%D1%88%D0%B5%D0%B2%2C%20%D0%92%D1%8F%D1%87%D0%B5%D1%81%D0%BB%D0%B0%D0%B2%20%D0%9A%D0%B8%D1%80%D0%B8%D0%BB%D0%BB%D0%BE%D0%B2)%20%5B2020%2C%20%D0%B4%D0%B5%D1%82%D0%B5%D0%BA%D1%82%D0%B8%D0%B2%2C%20%D0%BA%D1%80%D0%B8%D0%BC%D0%B8%D0%BD%D0%B0%D0%BB%2C%20%D0%B1%D0%BE%D0%B5%D0%B2%D0%B8%D0%BA%2C%20SATRip-AVC%5D'
    url = 'magnet:?xt=urn:btih:108F8A6F1F72C30E56F5259CF28ECCEA1FE76812&tr=http%3A%2F%2Fbt4.t-ru.org%2Fann%3Fmagnet'
    print(get_torrent_by_magnet(url2))
