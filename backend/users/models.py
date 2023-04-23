from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Класс кастомного пользователя"""

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = [
        'username',
        'first_name',
        'last_name',
    ]
    email = models.EmailField(
        verbose_name='Емайл',
        help_text='Введите электронную почту',
        max_length=254,
        unique=True,
    )

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
        ordering = ('-id', )
        constraints = [models.UniqueConstraint(
            fields=['user', 'author'], name='unique_subscription'
        )]

    def __str__(self) -> str:
        return f'{self.user} подписан на {self.author}'
