from django.contrib import admin
from .models import MediaCard, Rubric, Settings, TorrentTracker, TorrentClient


class MediaCardAdmin(admin.ModelAdmin):
    list_display = ([m_card.name for m_card in MediaCard._meta.get_fields()])
    list_display_links = ('full_name', 'comment')
    search_fields = ('full_name', 'comment')


class TorrentClientAdmin(admin.ModelAdmin):
    list_display = ('name', 'user')
    list_display_links = ('name', 'user')


admin.site.register(MediaCard, MediaCardAdmin)
admin.site.register(Rubric)
admin.site.register(Settings)
admin.site.register(TorrentTracker)
admin.site.register(TorrentClient, TorrentClientAdmin)
