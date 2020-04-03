from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.test import RequestFactory
from main.views import check_m_cards


class Command(BaseCommand):
    help = 'Провенить обновления медиа-карточек'

    def handle(self, *args, **options):
        request = RequestFactory().get('/')
        if options['user']:
            user = User.objects.filter(username=options['user']).first()
            if user:
                request.user = user
            else:
                return f'USER "{options["user"]}" - НЕ НАЙДЕН!'
        else:
            return 'Нужно указать USER'
        request.commands = True
        response = check_m_cards(request, 'check')
        if options['download']:
            response = check_m_cards(request, 'download')

    def add_arguments(self, parser):
        parser.add_argument(
            'user',
            nargs='?',
            type=str,
            default=None,
            help='Логин пользователя pyMediaManager - обазательный аргумент'
        )

        parser.add_argument(
            '-dw',
            '--download',
            action='store_true',
            default=False,
            help='При проверки торренты будут переданы в торрент-клиент для загрузки'
        )
