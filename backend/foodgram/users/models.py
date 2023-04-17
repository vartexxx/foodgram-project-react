from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models


class User(AbstractUser):
    """Класс кастомного пользователя"""

    username = models.CharField(
        verbose_name='Логин',
        help_text='Введите логин',
        max_length=150,
        unique=True,
        validators=[RegexValidator(
            regex=r'^[\w.@+-]+$',
            message='Логин содержит недопустимые символы',
        )]
    )
    first_name = models.CharField(
        verbose_name='Имя',
        help_text='Введите имя',
        max_length=150,
        blank=True,
    )
    last_name = models.CharField(
        verbose_name='Фамилия',
        help_text='Введите фамилию',
        max_length=150,
        blank=True
    )
    password = models.CharField(
        verbose_name='Пароль',
        help_text='введите пароль',
        max_length=150,
    )
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
        ordering = ['-id']
        constraints = [models.UniqueConstraint(
            fields=['user', 'author'], name='unique_subscription'
        )]

    def __str__(self) -> str:
        return f'{self.user} подписан на {self.author}'
