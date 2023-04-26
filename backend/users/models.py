from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser
from django.db.models import (CASCADE, CharField, EmailField, ForeignKey,
                              Model, UniqueConstraint)

User = get_user_model


class User(AbstractUser):
    """Класс кастомного пользователя"""

    email = EmailField(
        max_length=254,
        verbose_name='Адрес электронной почты',
        help_text='Введите адрес электронной почты',
        unique=True,
    )
    first_name = CharField(
        verbose_name='Имя',
        help_text='Введите свое имя',
        max_length=150,
    )
    last_name = CharField(
        verbose_name='Фамилия',
        help_text='Введите свою фамилию',
        max_length=150,
    )

    USERNAME_FIELD = 'email'

    REQUIRED_FIELDS = [
        'username',
        'first_name',
        'last_name',
    ]

    class Meta:
        ordering = ('username',)
        verbose_name = 'Пользователя'
        verbose_name_plural = 'Пользователи'

    def __str__(self) -> str:
        return self.username


class Subscribe(Model):
    """Класс модели подписок"""

    user = ForeignKey(
        User,
        on_delete=CASCADE,
        related_name='subscribers',
        verbose_name='Подписчик',
        help_text='Выберите подписчика',
    )
    author = ForeignKey(
        User, on_delete=CASCADE,
        related_name='subscribing',
        verbose_name='Автор контента',
        help_text='Выберите автора контента',
    )

    class Meta:
        verbose_name = 'Подписчика'
        verbose_name_plural = 'Подписки'
        ordering = ('-author_id',)
        constraints = [
            UniqueConstraint(
                fields=['user', 'author'],
                name='unique_subscribe',
            )
        ]
