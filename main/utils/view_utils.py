import json

from django.contrib import messages
from django.db.models import Q

from ..models import MediaCard, Settings, TorrentClient, TorrentTracker
from ..plugin_manager import dw_torrent_aio, dpt


def message_or_print(request, commands, text, type_message=messages.SUCCESS):
    if commands:
        print(text)
    else:
        messages.add_message(
            request,
            type_message,
            text,
        )


# @timeout(10)
def download_torrents(request, id_m_card, commands):
    stop_list = []
    tasks = {}
    magnet_urls = []
    m_cards, settings = get_m_card_set(request, get_settings=True)
    cookies = get_cookies(request.user)

    if not settings.t_client:
        return False
    else:
        client = TorrentClient.objects.get(name=settings.t_client, user=request.user)
        host = f'{client.host}:{client.port}'
        login = client.login
        password = client.password

    if id_m_card.isdigit():
        filter_m_cards = Q(id=id_m_card)
    else:
        filter_m_cards = Q(is_new_data=True)

    for m_card in m_cards.filter(filter_m_cards):
        m_card_cookies = cookies.get(m_card.plugin_name)
        if m_card_cookies:
            tasks[m_card.torrent_url] = m_card_cookies
        else:
            # В базе для данного плагина нет cookies:
            # Проверка, Возможна ли загрузка торрент-файла без авторизации
            # Если нет, проверка наличия загрузки по магнет-ссылки
            if not dpt[m_card.plugin_name].params('torrent_dw'):
                if not dpt[m_card.plugin_name].params('magnet_dw'):
                    message_or_print(
                        request,
                        commands,
                        f'Медиа-карточка "{m_card.short_name}" не загружена. Необходима авторизация в планиге "{m_card.plugin_name}", проверьте настройки.',
                        messages.ERROR
                    )
                    stop_list.append(m_card.id)
                    continue
                else:
                    magnet_urls.append(m_card.magnet_url)
            else:
                # Загрузка торрент-файла без авторизации
                tasks[m_card.torrent_url] = {}
    try:
        dw_torrent_aio(
            magnet_urls=magnet_urls,
            tasks=tasks,
            plugin_client=str(settings.t_client),
            host=host,
            login=login,
            password=password,
        )
    except:
        return False, False
    return m_cards, stop_list


def get_cookies(user):
    cookies_plugin = {}
    cookies = TorrentTracker.objects.filter(user=user)
    for cookie in cookies:
        cookies_plugin[cookie.name] = json.loads(cookie.session)
    return cookies_plugin


def get_m_card_set(request, get_settings=False):
    ordering = '-date_upd'
    settings = Settings.objects.get(user=request.user)
    criterion1 = Q(author=request.user)
    if settings.use_shared_cards:
        criterion2 = Q(is_view=True)
        m_card = MediaCard.objects.order_by(ordering).filter(criterion1 | criterion2)
    else:
        m_card = MediaCard.objects.order_by(ordering).filter(criterion1)
    if get_settings:
        return m_card, settings
    return m_card


def uncheck_new_data_m_card(m_cards, request, commands, stop_list=None):
    if stop_list is None:
        stop_list = []
    for m_card in m_cards:
        if m_card.author == request.user:
            if m_card.id in stop_list:
                continue
            m_card.is_new_data = False
            m_card.save()
        else:
            message_or_print(
                request,
                commands,
                f'{m_card.short_name} - остается в списке т.к создана другим автором: {m_card.author}',
                messages.SUCCESS)
