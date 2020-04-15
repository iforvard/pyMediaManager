from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.crypto import get_random_string

from .plugin_manager import dpt, dpc


class BaseModel(models.Model):
    objects = models.Manager()

    class Meta:
        abstract = True


class MediaCard(BaseModel):
    full_name = models.CharField(max_length=1000, verbose_name="Название")
    short_name = models.CharField(
        max_length=200, null=True, blank=True, verbose_name="Сокращение"
    )
    use_short_name = models.BooleanField(
        default=True,
        verbose_name='Использовать поле "Сокращение" для отображения на глвной',
    )
    published = models.DateTimeField(
        auto_now_add=True, db_index=True, verbose_name="Дата добавления"
    )
    comment = models.CharField(
        max_length=100, null=True, blank=True, verbose_name="комментарий/заметка"
    )
    size = models.CharField(max_length=20, verbose_name="Размер", null=True)
    date_upd = models.DateTimeField(
        db_index=True, verbose_name="Дата последнего обновления"
    )
    img_url = models.CharField(max_length=300, verbose_name="URL картинки")
    rubric = models.ForeignKey(
        "Rubric",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        verbose_name="Рубрика",
        to_field="name",
    )
    url = models.CharField(
        max_length=300, null=True, blank=True, verbose_name="url торрена на ресурсе загрузки"
    )
    magnet_url = models.CharField(
        max_length=300, null=True, blank=True, verbose_name="магнет url"
    )
    torrent_url = models.CharField(
        max_length=300, null=True, blank=True, verbose_name="торрент url"
    )
    is_new_data = models.BooleanField(
        default=False, verbose_name="Доступны обновления.",
        help_text='<em class="text-white">При загрузке обновленных карточек будет загружена</em>',
    )
    is_view = models.BooleanField(
        default=False,
        verbose_name="Разрешить просмотр всем пользователям",
    )
    is_edit = models.BooleanField(
        default=False, verbose_name="Разрешить редактирование и удаление всем пользователям."
    )
    plugin_name = models.CharField(
        max_length=300, null=True, blank=True, verbose_name="Добавлено через плагин"
    )
    author = models.ForeignKey(User, on_delete=models.CASCADE, null=True)

    # def get_absolute_url(self):
    #     return "/detail/%s/" % self.pk


class Rubric(BaseModel):
    name = models.CharField(
        max_length=100, db_index=True, verbose_name='Название рубрики', unique=True)

    # order = models.SmallIntegerField(default=0, db_index=True)
    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'Рубрики'
        verbose_name = 'Рубрика'
        ordering = ['name']


class Settings(BaseModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    use_shared_cards = models.BooleanField(
        default=False,
        verbose_name="Показывать и загружать карточки других авторов, у которых разрешен просмотр всем",
    )
    t_client = models.ForeignKey(
        "TorrentClient",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        verbose_name="Торрент клинет",
    )

    uuid = models.CharField(max_length=100, verbose_name="uuid", blank=True)

    def __str__(self):
        return str(self.user)


class TorrentTracker(BaseModel):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, null=True)
    name = models.CharField(
        max_length=300,
        choices=[(name, name) for name in dpt],
        verbose_name="Торрент-трекер",
    )
    session = models.CharField(max_length=500, verbose_name="session", blank=True)
    login = models.CharField(max_length=200, verbose_name="Логин", blank=True)
    password = models.CharField(max_length=200, verbose_name="Пароль", blank=True)

    def __str__(self):
        return f"{self.user}_{self.name}"

    class Meta:
        unique_together = ['user', 'name']


class TorrentClient(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    name = models.CharField(
        max_length=300,
        choices=[(name, name) for name in dpc],
        verbose_name="Торрент клиент",
    )
    host = models.CharField(max_length=300, verbose_name="Хост", blank=True)
    port = models.IntegerField(verbose_name="Порт", default=8080)
    login = models.CharField(max_length=300, verbose_name="Логин", blank=True)
    password = models.CharField(max_length=300, verbose_name="Пароль", blank=True)

    def __str__(self):
        return f"{self.name}"

    class Meta:
        unique_together = ['user', 'name']


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """
    При создании нового пользователя, у него создаются дефолтные настройки.
    """
    if created:
        settings = Settings.objects.create(user=instance)
        settings.uuid = f'{settings.id}:{get_random_string(64)}'


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """
    Сохранение настроек для ногвого пользователя.
    """
    instance.settings.save()
