import asyncio

from magnet2torrent import Magnet2Torrent, FailedToFetchException


class M2T(Magnet2Torrent):
    @property
    def name(self):
        return (
            self._parse_url()[2].decode()
                .strip(".")
                .replace("/", "")
                .replace("\\", "")
                .replace(":", "")
        )


async def fetch_that_torrent(magnet_url):
    m2t = M2T(magnet_url, use_additional_trackers=True)
    try:
        torrent = await m2t.retrieve_torrent()
        return torrent
    except FailedToFetchException:
        print("Failed")


def get_torrent_by_magnet(magnet_url):
    filename, torrent_data = asyncio.run(fetch_that_torrent(magnet_url))
    return [torrent_data]


if __name__ == '__main__':
    url = 'magnet:?xt=urn:btih:9A73039A6B17F27FFE33D5387E79F5A6137645F5&tr=http%3A%2F%2Fbt3.t-ru.org%2Fann%3Fmagnet'
    get_torrent_by_magnet(url)
