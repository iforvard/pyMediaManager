import asyncio
import csv
import io
import json
from datetime import datetime

from django import forms
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.syndication.views import Feed
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from django.http import HttpResponse, HttpResponseNotFound
from django.shortcuts import render, redirect
from django.urls import reverse_lazy, reverse
from django.utils.feedgenerator import DefaultFeed
from django.views.generic.detail import DetailView
from django.views.generic.edit import UpdateView, DeleteView, CreateView
from django.views.generic.list import ListView

from homepagenews.homepagenews_editor import get_news_list_github
from .models import MediaCard, Rubric, Settings, TorrentClient, TorrentTracker
from .plugin_manager import dpt, get_m_cards_to_urls, async_manager_torrent
from .utils.mganet_to_torrent import get_torrent_by_magnet
from .utils.view_utils import message_or_print, download_torrents, get_cookies, uncheck_new_data_m_card, \
    get_m_card_set, create_new_uid, dw_update_m_cards, get_user_by_uid, sort_dw_tasks_m_cards


def home_page(request):
    try:
        news_list, main_head = get_news_list_github()
        context = {'news_list': news_list, 'main_head': main_head}
    except:
        context = {'news_list': [{'head': 'Welcome!', 'body': 'Welcome! to pyMediaManager'}],
                   'main_head': '<b>pyMediaManager</b> - менеджер торрент клиентов и трекеров'
                   }
    return render(request, 'main/homepage.html', context)


@login_required
def get_new_uid(request):
    create_new_uid(request)
    return redirect(f'{reverse("main:profile", args=(request.user,))}?uuid')


@login_required
def search_by_m_cards(request):
    search_query = request.GET.get('q', '')
    m_cards = get_m_card_set(request)

    if search_query:
        m_cards = m_cards.filter(
            Q(rubric__name__icontains=search_query) |
            Q(full_name__icontains=search_query) |
            Q(short_name__icontains=search_query) |
            Q(comment__icontains=search_query) |
            Q(plugin_name__icontains=search_query)
        )
        search_query = f'Найдено записей {m_cards.count()}. Результат поиска по запросу: "{search_query}".'
    else:
        search_query = f'Найдено записей {m_cards.count()}. Запрос пустой, отображены все записи.'
    message_or_print(
        request,
        False,
        search_query,
    )
    context = {'data': m_cards, 'check': True, 'lists': True}
    return render(request, 'main/check.html', context)


@login_required
def skip_m_cards(request, id_m_card):
    m_cards = get_m_card_set(request)

    if id_m_card.isdigit():
        skip_m_cards = m_cards.filter(id=id_m_card)
        uncheck_new_data_m_card(skip_m_cards, request, commands=False)
    elif id_m_card == 'all':
        uncheck_new_data_m_card(m_cards, request, commands=False)

    context = {'data': m_cards, 'check': True}
    return render(request, 'main/check.html', context)


@login_required
def download_m_cards(request, id_m_card='all'):
    commands = request.GET.get('commands', False)
    m_cards, stop_list = download_torrents(request, id_m_card)

    if stop_list:
        for m_card in stop_list:
            message_or_print(
                request,
                commands,
                f'Медиа-карточка "{m_card.short_name}" не загружена. Необходима авторизация в планиге "{m_card.plugin_name}", проверьте настройки.',
                messages.ERROR
            )

    if m_cards:
        message_or_print(
            request,
            commands,
            'Торрент-файл(ы) успешно отправлен(ы) в торрент-клиент',
            messages.SUCCESS
        )
        if id_m_card.isdigit():
            uncheck_new_data_m_card(m_cards.filter(pk=id_m_card), request, commands, stop_list=stop_list)
        else:
            uncheck_new_data_m_card(m_cards, request, commands, stop_list=stop_list)
    else:
        message_or_print(
            request,
            commands,
            'Ошибка загрузки! Не удалось подключиться торрент-клиенту либо в настройках указан не верный профиль.',
            messages.ERROR
        )
        m_cards = []
    context = {'data': m_cards, 'check': True, 'key': 'reed'}
    return render(request, 'main/check.html', context)


@login_required
def check_m_cards(request, key):
    if key == 'check':
        m_cards = dw_update_m_cards(user=request.user)
    else:
        m_cards = get_m_card_set(request)

    context = {'data': m_cards, 'key': key, 'check': True}
    return render(request, 'main/check.html', context)


@login_required
def add_torrent(request):
    id_torrent = request.GET.get('id_torrent', '')
    m_card = get_m_cards_to_urls([id_torrent], get_cookies(request.user))
    if m_card:
        m_card = m_card[id_torrent]
        media_card = MediaCard.objects.create(
            full_name=m_card['full_name'],
            short_name=m_card['short_name'],
            size=m_card['size'],
            date_upd=m_card['date_upd'],
            img_url=m_card['img_url'],
            magnet_url=m_card['magnet_url'],
            torrent_url=m_card['torrent_url'],
            url=m_card['url'],
            plugin_name=m_card['plugin_name'],
            author=request.user,
        )
        return redirect('main:detail', pk=media_card.pk)
    messages.add_message(
        request, messages.ERROR,
        f'Плагины не смогли распознать ссылку. Список подключенных плагинов: {", ".join([plugin for plugin in dpt])}'
    )
    return redirect('main:index')


class IndexMediaCardView(LoginRequiredMixin, ListView):
    template_name = 'main/index.html'
    context_object_name = 'MediaCards'
    model = MediaCard
    paginate_by = 10

    def get_paginate_by(self, queryset):
        new_paginate = self.request.GET.get("paginate_by")
        if new_paginate and new_paginate.isdigit():
            self.request.session['paginate_glob'] = new_paginate
            return new_paginate
        if 'paginate_glob' in self.request.session:
            return self.request.session['paginate_glob']

        return self.paginate_by

    def get_queryset(self):
        return get_m_card_set(self.request)


class MediaCardDetailView(LoginRequiredMixin, DetailView):
    model = MediaCard
    template_name = 'main/detail.html'
    context_object_name = 'm_card'


class MediaCardUpdateView(UserPassesTestMixin, UpdateView):
    model = MediaCard
    template_name = 'main/update.html'
    fields = ('full_name', 'short_name', 'use_short_name', 'rubric', 'comment', 'size', 'date_upd',
              'img_url', 'torrent_url', 'magnet_url', 'url', 'plugin_name', 'is_new_data', 'is_view')
    success_url = '/detail/{id}'

    def test_func(self):
        return self.request.user == self.get_object().author

    def handle_no_permission(self):
        messages.add_message(
            self.request, messages.ERROR,
            f'Редактировать и удалять может только автор - {self.get_object().author}.'
        )
        return redirect('main:detail', pk=self.get_object().pk)


class ProfileSettingsView(ListView):
    template_name = 'main/settings_base.html'
    model = Settings
    context_object_name = 'Settings'
    slug_field = 'user__username'
    slug_url_kwarg = 'username'

    def get_queryset(self):
        return Settings.objects.get(user=self.request.user)

    def get_context_data(self, *args, **kwargs):
        context = super(ProfileSettingsView, self).get_context_data(*args, **kwargs)
        context['TorrentTrackers'] = TorrentTracker.objects.filter(user=self.request.user)
        context['TorrentClients'] = TorrentClient.objects.filter(user=self.request.user)
        context['Rubrics'] = Rubric.objects.all()
        context['settings'] = True
        return context

    def get_user_ip(self):
        x_forwarded_for = self.request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = self.request.META.get('REMOTE_ADDR')
        return ip


class SettingsUpdateView(UserPassesTestMixin, SuccessMessageMixin, UpdateView):
    model = Settings
    template_name = 'main/settings.html'
    fields = ('use_shared_cards', 't_client')
    slug_field = 'user__username'
    slug_url_kwarg = 'username'
    success_message = 'Изменения сохранены'

    def get_form(self, *args, **kwargs):
        form = super(SettingsUpdateView, self).get_form(*args, **kwargs)
        form.fields['t_client'].queryset = TorrentClient.objects.filter(user=self.request.user)
        return form

    def get_success_url(self, **kwargs):
        return reverse_lazy("main:profile", args=(self.object.user,))

    def test_func(self):
        return self.request.user == self.get_object().user

    def get_client_ip(self):
        x_forwarded_for = self.request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = self.request.META.get('REMOTE_ADDR')
        return ip


class MediaCardDeleteView(UserPassesTestMixin, DeleteView):
    context_object_name = 'm_card'
    model = MediaCard
    template_name = 'main/delete.html'
    success_url = '/'

    def test_func(self):
        return self.request.user == self.get_object().author

    def handle_no_permission(self):
        messages.add_message(
            self.request, messages.ERROR,
            f'Редактировать и удалять может только автор - {self.get_object().author}.'
        )
        return redirect('main:detail', pk=self.get_object().pk)


class RubricCreateView(LoginRequiredMixin, CreateView):
    template_name = 'main/create_rubric.html'
    model = Rubric
    fields = ('name',)

    def get_success_url(self, **kwargs):
        return f'{reverse("main:profile", args=(self.request.user,))}#rubrics'


class RubricUpdateView(LoginRequiredMixin, UpdateView):
    template_name = 'main/create_rubric.html'
    model = Rubric
    fields = ('name',)

    def get_success_url(self, **kwargs):
        return f'{reverse("main:profile", args=(self.request.user,))}#rubrics'


class RubricDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    context_object_name = 'Rubric'
    template_name = 'main/delete_rubric.html'
    model = Rubric
    fields = ('name',)

    def test_func(self):
        return self.get_object().name not in ("Архив", "Archive")

    def handle_no_permission(self):
        messages.add_message(
            self.request, messages.ERROR,
            f'Нельзя удалить теги "Архив" и "Archive"'
        )
        return redirect('main:profile', username=self.request.user)

    def get_success_url(self, **kwargs):
        return f'{reverse("main:profile", args=(self.request.user,))}#rubrics'


class TorrentTrackerDeleteView(LoginRequiredMixin, DeleteView):
    context_object_name = 'Rubric'
    template_name = 'main/delete_torrent_tracker.html'
    model = TorrentTracker
    fields = ('name',)

    def get_success_url(self, **kwargs):
        return f'{reverse("main:profile", args=(self.request.user,))}#rubrics'


class TorrentClientDeleteView(LoginRequiredMixin, DeleteView):
    context_object_name = 'Rubric'
    template_name = 'main/delete_torrent_client.html'
    model = TorrentClient
    fields = ('name',)

    def get_success_url(self, **kwargs):
        return f'{reverse("main:profile", args=(self.request.user,))}#rubrics'


class TorrentTrackerUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    template_name = 'main/create_torrent_tracker.html'
    fields = ('login', 'password')
    model = TorrentTracker
    slug_field = 'name'
    slug_url_kwarg = 'name'
    success_message = 'Изменения сохранены'

    def get_form(self, form_class=None):
        form = super(TorrentTrackerUpdateView, self).get_form(form_class)
        form.fields['password'].widget = forms.PasswordInput()
        return form

    def get_queryset(self):
        return TorrentTracker.objects.filter(user=self.request.user)

    def test_func(self):
        return self.request.user == self.get_object().user

    def get_success_url(self, **kwargs):
        return reverse_lazy("main:profile", args=(self.object.user,))

    def form_valid(self, form):
        obj = form.save(commit=False)
        session = json.dumps(dpt[obj.name].login(obj.login, obj.password))
        if session != 'null':
            obj.session = session
        else:
            form.add_error('login', f'Не удалось подключиться к "{obj.name}" с указанным логином и паролем.')
            return self.form_invalid(form)
        obj.save()
        messages.add_message(
            self.request, messages.SUCCESS,
            f'Профиль для Торрент-трекера - "{obj.name}" успешно изменен.'
        )
        return redirect('main:profile', username=self.request.user)


class TorrentClientUpdateView(UserPassesTestMixin, SuccessMessageMixin, UpdateView):
    template_name = 'main/create_torrent_tracker.html'
    fields = ('host', 'port', 'login', 'password')
    model = TorrentClient
    slug_field = 'name'
    slug_url_kwarg = 'name'
    success_message = 'Изменения сохранены'

    def get_form(self, form_class=None):
        form = super(TorrentClientUpdateView, self).get_form(form_class)
        form.fields['password'].widget = forms.PasswordInput()
        return form

    def get_queryset(self):
        return TorrentClient.objects.filter(user=self.request.user)

    def get_success_url(self, **kwargs):
        return reverse_lazy("main:profile", args=(self.object.user,))

    def test_func(self):
        return self.request.user == self.get_object().user


class TorrentTrackerCreateView(LoginRequiredMixin, CreateView):
    template_name = 'main/create_torrent_tracker.html'
    fields = ('name', 'login', 'password')
    model = TorrentTracker

    def get_form(self, form_class=None):
        form = super(TorrentTrackerCreateView, self).get_form(form_class)
        form.fields['password'].widget = forms.PasswordInput()
        return form

    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.user = self.request.user
        qs = TorrentTracker.objects.filter(user=obj.user, name=obj.name)
        if qs.exists():
            form.add_error('name', f'Профиль c "{obj.name}" уже был добавлен ранее.')
            return self.form_invalid(form)
        session = json.dumps(dpt[obj.name].login(obj.login, obj.password))
        if session != 'null':
            obj.session = session
        else:
            form.add_error('name', f'Не удалось подключиться к "{obj.name}" с указанным логином и паролем.')
            return self.form_invalid(form)
        obj.save()
        messages.add_message(
            self.request, messages.SUCCESS,
            f'Профиль для Торрент-трекера - "{obj.name}" успешно добавлен.'
        )
        return redirect('main:profile', username=self.request.user)


class TorrentClientCreateView(LoginRequiredMixin, CreateView):
    template_name = 'main/create_torrent_tracker.html'
    model = TorrentClient
    fields = ('name', 'host', 'port', 'login', 'password')

    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.user = self.request.user
        qs = TorrentClient.objects.filter(user=obj.user, name=obj.name)
        if qs.exists():
            form.add_error('name', f'Профиль c "{obj.name}" уже был добавлен ранее.')
            return self.form_invalid(form)
        obj.save()
        messages.add_message(
            self.request, messages.SUCCESS,
            f'Профиль для Торрент-клиента - "{obj.name}" успешно добавлен.'
        )
        return redirect('main:profile', username=self.request.user)

    def get_form(self, form_class=None):
        form = super(TorrentClientCreateView, self).get_form(form_class)
        form.fields['password'].widget = forms.PasswordInput()
        return form


@login_required
def export_m_cards(request):
    m_cards = get_m_card_set(request)
    # Create the HttpResponse object with the appropriate CSV header.
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="m_cards_{request.user}.csv"'

    writer = csv.writer(response)
    # writer.writerow(['First row', 'Foo', 'Bar', 'Baz'])
    for m_card in m_cards:
        writer.writerow([
            m_card.full_name,
            m_card.short_name,
            m_card.size,
            m_card.date_upd,
            m_card.img_url,
            m_card.url,
            m_card.magnet_url,
            m_card.torrent_url,
            m_card.comment,
            m_card.plugin_name,
        ])

    return response


@login_required
def import_m_cards(request):
    m_cards_csv = request.FILES.get('m_cards', '')
    if m_cards_csv.name.endswith('.csv'):
        m_cards = m_cards_csv.read().decode()
        io_string = io.StringIO(m_cards)
        comment = f'csv_import_{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}'
        media_cards_objects = []
        for m_card in csv.reader(io_string):
            media_card = MediaCard.objects.create(
                full_name=m_card[0],
                short_name=m_card[1],
                size=m_card[2],
                date_upd=m_card[3],
                img_url=m_card[4],
                url=m_card[5],
                magnet_url=m_card[6],
                torrent_url=m_card[7],
                comment=f'{comment}. {m_card[8]}',
                plugin_name=m_card[9],
                author=request.user,
            )
            media_cards_objects.append(media_card)
        message_or_print(
            request,
            False,
            f'Импорт завершен, к записям добавлен комментарий - "{comment}"',
        )
    else:
        message_or_print(
            request,
            False,
            'Не верный формат файла! Для получения образца воспользуйтесь экспортом.',
            messages.ERROR
        )
        return redirect(f'{reverse("main:profile", args=(request.user,))}#id_torrent')

    context = {'data': media_cards_objects, 'check': True, 'lists': True}
    return render(request, 'main/check.html', context)


class CorrectMimeTypeFeed(DefaultFeed):
    content_type = 'application/xml; charset=utf-8'


class MCardsUPDFeed(Feed):
    title = "Pymediamanager"
    link = ''
    description = "MediaCards UPD"
    feed_type = CorrectMimeTypeFeed

    def get_object(self, request, uid):
        user = get_user_by_uid(uid)
        self.uid = uid
        return user

    def items(self, user):
        m_cards = []
        if user:
            m_cards = dw_update_m_cards(user=user).filter(is_new_data=True)
        return m_cards

    def item_title(self, item):
        return f'[{item.plugin_name}] | {item.short_name} | {item.date_upd.strftime("%d.%m.%Y %H:%M:%S")}'

    def item_description(self, item):
        return item.full_name

    def item_pubdate(self, item):
        """
        Takes an item, as returned by items(), and returns the item's
        pubdate.
        """
        return item.date_upd

    def item_guid(self, item):
        """
        Takes an item, as return by items(), and returns the item's ID.
        """
        return f'{item.pk}/{item.date_upd.strftime("%d.%m.%Y %H:%M:%S")}'

    def item_updateddate(self):
        """
        Takes an item, as returned by items(), and returns the item's
        updateddate.
        """
        return datetime.now()

    def item_link(self, item):
        return reverse('main:get_torrent', args=[item.pk, self.uid])


def get_torrent_file(request, m_card_id, uid):
    """
    proxy-torrent-download

    """
    user = get_user_by_uid(uid)
    t_file = None
    if user:
        m_cards = MediaCard.objects.filter(id=m_card_id)
        m_card = m_cards.first()
        if m_card.author == user or m_card.is_view:
            stop_list_url, urls, magnet_urls = sort_dw_tasks_m_cards(m_cards, user, m_card_id)
            if urls:
                t_file = asyncio.run(async_manager_torrent(urls))[0]
            elif magnet_urls:
                t_file = get_torrent_by_magnet(*magnet_urls)

        if t_file:
            response = HttpResponse(t_file, content_type='application/x-bittorrent')
            response['Content-Disposition'] = f'attachment; filename="{m_card.id}.torrent"'
            # m_card.is_new_data = False
            # m_card.save()
            return response
    return HttpResponseNotFound()
