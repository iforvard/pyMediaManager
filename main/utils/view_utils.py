import json

from django.contrib import messages
from django.db.models import Q
from django.utils.crypto import get_random_string

from ..models import MediaCard, Settings, TorrentClient, TorrentTracker
from ..plugin_manager import dw_torrent_aio, dpt, get_m_cards_to_urls


def message_or_print(request, commands, text,  type_message=messages.SUCCESS):
    if commands:
        print(text)
    else:
        messages.add_message(
            request,
            type_message,
            text,
        )


def sort_dw_tasks_m_cards(m_cards, user, id_m_card):
    """
    Сортировка m_cards для загрузки в соотвестви с требованиями плагина.
    return:
    stop_list_url - Эти m_cards загрузить нельзя!
    В базе нет нужного cookies, а загрузка без авторизации или по magnet-сылки не доступна.
    urls - Словарь url и его cookies. Если возможна загрузка без авторизации cookies будет пустой.
    magnet_urls - Загрузка возможна напрямую без прокси и cookies
    """
    stop_list_url = []
    urls = {}
    magnet_urls = []
    cookies = get_cookies(user)

    if id_m_card.isdigit():
        filter_m_cards = Q(id=id_m_card)
    else:
        filter_m_cards = Q(is_new_data=True)

    for m_card in m_cards.filter(filter_m_cards):
        m_card_cookies = cookies.get(m_card.plugin_name)
        if m_card_cookies:
            urls[m_card.torrent_url] = m_card_cookies
        else:
            # В базе для данного плагина нет cookies:
            # Проверка, Возможна ли загрузка торрент-файла без авторизации
            # Если нет, проверка наличия загрузки по магнет-ссылки
            if not dpt[m_card.plugin_name].params('torrent_dw'):
                if not dpt[m_card.plugin_name].params('magnet_dw'):
                    stop_list_url.append(m_card.id)
                    continue
                else:
                    magnet_urls.append(m_card.magnet_url)
            else:
                # Загрузка торрент-файла без авторизации
                urls[m_card.torrent_url] = {}

    return stop_list_url, urls, magnet_urls


# @timeout(10)
def download_torrents(request, id_m_card):
    m_cards, settings = get_m_card_set(request, get_settings=True)
    stop_list_url, urls, magnet_urls = sort_dw_tasks_m_cards(m_cards, request.user, id_m_card)

    if not settings.t_client:
        return False, False
    else:
        client = TorrentClient.objects.get(name=settings.t_client, user=request.user)
        host = f'{client.host}:{client.port}'
        login = client.login
        password = client.password

    try:
        dw_torrent_aio(
            magnet_urls=magnet_urls,
            tasks=urls,
            plugin_client=str(settings.t_client),
            host=host,
            login=login,
            password=password,
        )
    except:
        return False, False
    return m_cards, stop_list_url


def get_cookies(user):
    cookies_plugin = {}
    cookies = TorrentTracker.objects.filter(user=user)
    for cookie in cookies:
        cookies_plugin[cookie.name] = json.loads(cookie.session)
    return cookies_plugin


def get_m_card_set(request=None, get_settings=False, user=None):
    if not user:
        user = request.user
    ordering = '-date_upd'
    settings = Settings.objects.get(user__username=user)
    criterion1 = Q(author__username=user)
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


def create_new_uid(request):
    unique_id = get_random_string(length=64)
    user_set = Settings.objects.get(user=request.user)
    user_set.uuid = f'{user_set.id}:{unique_id}'
    user_set.save()


def dw_update_m_cards(request, m_cards=None):
    if not m_cards:
        m_cards = get_m_card_set(request)
    torrents = [m_card.url for m_card in m_cards]
    cookies = get_cookies(request.user)
    upd_m_cards = get_m_cards_to_urls(torrents, cookies)

    for m_card in m_cards:
        if upd_m_cards[m_card.url]['date_upd'] > m_card.date_upd:
            m_card.date_upd = upd_m_cards[m_card.url]['date_upd']
            m_card.full_name = upd_m_cards[m_card.url]['full_name']
            m_card.magnet_url = upd_m_cards[m_card.url]['magnet_url']
            m_card.size = upd_m_cards[m_card.url]['size']
            m_card.is_new_data = True
            m_card.save()

    return m_cards


def get_user_by_uid(uid):
    if len(uid.split(':')) == 2:
        user_id = uid.split(':')[0]
        users = Settings.objects.filter(uuid=uid, user__id=user_id)
        if users.count() == 1:
            user = users.first()
            return user.user
