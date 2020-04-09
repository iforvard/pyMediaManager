import importlib
import pkgutil
import asyncio
import aiohttp
from .plugins import trackers
from .plugins import clients
from wrapt_timeout_decorator import *


def iter_namespace(ns_pkg):
    # Specifying the second argument (prefix) to iter_modules makes the
    # returned name an absolute name instead of a relative one. This allows
    # import_module to work without having to do additional modification to
    # the name.
    return pkgutil.iter_modules(ns_pkg.__path__, ns_pkg.__name__ + ".")


discovered_plugins_trackers = dpt = {
    name.split('.')[-1]: importlib.import_module(name)
    for finder, name, ispkg
    in iter_namespace(trackers)
}
discovered_plugins_clients = dpc = {
    name.split('.')[-1]: importlib.import_module(name)
    for finder, name, ispkg
    in iter_namespace(clients)
}


def get_task_to_urls(urls, cookies):
    tasks = {}
    for url in urls:
        for plugin_tracker in dpt:
            if dpt[plugin_tracker].params('url_prefix') in url:
                if plugin_tracker in tasks:
                    tasks[plugin_tracker]['urls'].append(url)
                    continue
                else:
                    tasks[plugin_tracker] = {
                        'urls': [url],
                        'cookies': cookies.get(plugin_tracker, {}),
                        'name': plugin_tracker
                    }
                    continue
    if tasks:
        return tasks


async def get_torrent_file(cookies, url):
    async with aiohttp.ClientSession(trust_env=True, cookies=cookies) as session:
        async with session.get(url) as response:
            print(response.status)
            return await response.read()


async def get_page_text(cookies, url, name):
    async with aiohttp.ClientSession(trust_env=True, cookies=cookies) as session:
        async with session.get(url) as response:
            print(response.status)
            resp = await response.text()
            return {'page': resp, 'name': name, 'url': url}


async def async_manager_torrent(tasks_list):
    tasks = []
    for url, cookies in tasks_list.items():
        task = asyncio.create_task(get_torrent_file(url=url, cookies=cookies))
        tasks.append(task)
    return await asyncio.gather(*tasks)


async def async_manager_page(tasks_list):
    tasks = []
    for plugin in tasks_list.values():
        for url in plugin['urls']:
            task = asyncio.create_task(get_page_text(plugin['cookies'], url, plugin['name']))
            tasks.append(task)

    return await asyncio.gather(*tasks)


def get_m_cards_to_urls(urls, cookies):
    tasks = get_task_to_urls(urls, cookies)
    if tasks:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        pages = loop.run_until_complete(async_manager_page(tasks))
        pages = {
            page['url']: dpt[page['name']].parser(page['page'])
            for page in pages
        }
        return pages


@timeout(6)
def dw_torrent_aio(magnet_urls, tasks, plugin_client, host, login, password):
    print((magnet_urls, tasks, plugin_client, host, login, password))
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    torrents = loop.run_until_complete(async_manager_torrent(tasks))
    # torrents = asyncio.run(async_manager_torrent(tasks))
    dpc[plugin_client].dw_torrent(torrents, magnet_urls, host, login, password)
