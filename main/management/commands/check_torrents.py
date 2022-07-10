from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

from main.utils.view_utils import dw_update_m_cards, download_torrents


class Command(BaseCommand):
    """
    iforvard - нужно заменить на логин пользователя в системе,
    Если после проверки обновлений требуется загрузка в bashCommand нужно добавить -dw.
    Обновление:
    bashCommand = "python3 manage.py check_torrents iforvard"
    Обновление и загрузка:
    bashCommand = "python3 manage.py check_torrents iforvard -dw"
    """
    help = 'Проверить обновления медиа-карточек'

    def handle(self, *args, **options):
        if options['user']:
            user = User.objects.filter(username=options['user']).first()
            if not user:
                return f'USER "{options["user"]}" - НЕ НАЙДЕН!'
        else:
            return 'Нужно указать USER'

        dw_update_m_cards(user=user)
        print(f'dw_update_m_cards - [OK]')
        if options['download']:
            download_torrents(user=user)
            print(f'download_torrents - [OK]')

    def add_arguments(self, parser):
        parser.add_argument(
            'user',
            nargs='?',
            type=str,
            default=None,
            help='Логин пользователя pyMediaManager - обязательный аргумент'
        )

        parser.add_argument(
            '-dw',
            '--download',
            action='store_true',
            default=False,
            help='При проверки торренты будут переданы в торрент-клиент для загрузки'
        )
