from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Класс кастомного пользователя"""
    email = models.EmailField(
        max_length=254,
        verbose_name='Адрес электронной почты',
        unique=True,
    )
    username = models.CharField(
        verbose_name='Имя пользователя',
        max_length=150,
        unique=True,
    )
    first_name = models.CharField(
        verbose_name='Имя',
        max_length=150,
        blank=True,
        null=True,
    )
    last_name = models.CharField(
        verbose_name='Фамилия',
        max_length=150,
        blank=True,
        null=True,
    )
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    class Meta:
        ordering = ('username',)
        verbose_name = 'Пользователя'
        verbose_name_plural = 'Пользователи'

    def __str__(self) -> str:
        return self.username


class Subscribe(models.Model):
    """Класс модели подписок"""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscriber',
        verbose_name='Подписчик',
        help_text='Выберите подписчика',
    )
    author = models.ForeignKey(
        User,
        related_name='subscribing',
        on_delete=models.CASCADE,
        verbose_name='Автор контента',
        help_text='Выберите автора контента',
    )

    class Meta:
        verbose_name = 'Подписчика'
        verbose_name_plural = 'Подписки'
        ordering = ('-id',)
        constraints = [models.UniqueConstraint(
            fields=['user', 'author'], name='unique_subscription'
        )]
