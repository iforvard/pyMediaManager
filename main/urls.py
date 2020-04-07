from django.urls import path

from .views import IndexMediaCardView, add_torrent, MediaCardDetailView, MediaCardUpdateView, \
    MediaCardDeleteView, check_m_cards, RubricCreateView, SettingsUpdateView, \
    TorrentClientCreateView, TorrentTrackerCreateView, ProfileSettingsView, TorrentTrackerUpdateView, \
    TorrentClientUpdateView, RubricUpdateView, RubricDeleteView, home_page, skip_m_cards, download_m_cards, \
    TorrentTrackerDeleteView, TorrentClientDeleteView, index_m_cards_lists, search_by_m_cards, export_m_cards

app_name = 'main'
urlpatterns = [
    path('profile/<slug:username>/', ProfileSettingsView.as_view(), name='profile'),
    path('settings/<slug:username>/', SettingsUpdateView.as_view(), name='settings'),
    path('add/torrent', add_torrent, name='add_torrent'),
    path('add/rubric', RubricCreateView.as_view(), name='add_rubric'),
    path('add/torrent_tracker', TorrentTrackerCreateView.as_view(), name='add_torrent_tracker'),
    path('add/torrent_client', TorrentClientCreateView.as_view(), name='add_torrent_client'),
    path('delete/<int:pk>/', MediaCardDeleteView.as_view(), name='delete'),
    path('delete/torrent_tracker/<int:pk>/', TorrentTrackerDeleteView.as_view(), name='delete_torrent_tracker'),
    path('delete/torrent_client/<int:pk>/', TorrentClientDeleteView.as_view(), name='delete_torrent_client'),
    path('delete/rubric/<int:pk>/', RubricDeleteView.as_view(), name='rubric_delete'),
    path('update/<int:pk>/', MediaCardUpdateView.as_view(), name='update'),
    path('update/rubric/<int:pk>/', RubricUpdateView.as_view(), name='rubric_update'),
    path('update/torrent_tracker/<slug:name>/', TorrentTrackerUpdateView.as_view(), name='upd_torrent_tracker'),
    path('update/torrent_client/<slug:name>/', TorrentClientUpdateView.as_view(), name='upd_torrent_client'),
    path('detail/<int:pk>/', MediaCardDetailView.as_view(), name='detail'),
    # path('dw/<str:torrent_id>/', get_torrent_file, name='dw'),
    path('check/<str:key>/', check_m_cards, name='check'),
    path('homepage/', home_page, name='homepage'),
    path('skip_m_cards/<str:id_m_card>', skip_m_cards, name='skip_m_cards'),
    path('download_m_cards/<str:id_m_card>', download_m_cards, name='download_m_cards'),
    path('search', search_by_m_cards, name='search'),
    path('lists', index_m_cards_lists, name='index_m_cards_lists'),
    path('export_m_cards', export_m_cards, name='export_m_cards'),
    path('', IndexMediaCardView.as_view(), name='index'),
]
