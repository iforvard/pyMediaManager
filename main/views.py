import json

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.shortcuts import render, redirect
from django.urls import reverse_lazy, reverse
from django.views.generic.detail import DetailView
from django.views.generic.edit import UpdateView, DeleteView, CreateView
from django.views.generic.list import ListView
from django import forms

from homepagenews.homepagenews_editor import get_news_list_github
from .models import MediaCard, Rubric, Settings, TorrentClient, TorrentTracker
from .plugin_manager import dpt, get_m_cards_to_urls
from .utils.view_utils import message_or_print, download_torrents, get_cookies, uncheck_new_data_m_card, \
    get_m_card_set


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
def index_m_cards_lists(request):
    m_cards = get_m_card_set(request)
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
def download_m_cards(request, id_m_card=None):
    commands = request.GET.get('commands', False)
    m_cards = download_torrents(request, id_m_card)

    if m_cards:
        message_or_print(
            request,
            commands,
            'Торрент-файл(ы) успешно отправлен(ы) в торрент-клиент',
            messages.SUCCESS
        )
        if id_m_card.isdigit():
            uncheck_new_data_m_card(m_cards.filter(pk=id_m_card), request, commands)
        else:
            uncheck_new_data_m_card(m_cards, request, commands)
    else:
        message_or_print(
            request,
            commands,
            'Ошибка загрузки! Не удалось подключиться торрент-клиенту либо в настройках указан не верный профиль.',
            messages.ERROR
        )
    context = {'data': m_cards, 'check': True}
    return render(request, 'main/check.html', context)


@login_required
def check_m_cards(request, key):
    m_cards, settings = get_m_card_set(request, get_settings=True)
    if key == 'check':
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


class RubricDeleteView(LoginRequiredMixin, DeleteView):
    context_object_name = 'Rubric'
    template_name = 'main/delete_rubric.html'
    model = Rubric
    fields = ('name',)

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

# TO-DO proxy-torrent-download
# def get_torrent_file(request, torrent_id):
#     url = rutracker.url_dl + torrent_id
#
#     loop = asyncio.new_event_loop()
#     asyncio.set_event_loop(loop)
#     my_data = loop.run_until_complete(rutracker.get_data_tracker_main([url], torrent=True))
#
#     response = HttpResponse(*my_data, content_type='application/x-bittorrent')
#     response['Content-Disposition'] = 'attachment; filename="foo.torrent"'
#     return response
