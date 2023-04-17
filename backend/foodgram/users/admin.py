from django.contrib import admin
from django.contrib.auth import get_user_model

from .models import Subscribe

User = get_user_model()


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'username',
        'first_name',
        'last_name',
        'email',
    )
    search_fields = (
        'email',
        'username'
    )
    empty_value_display = 'пусто'


@admin.register(Subscribe)
class FollowAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'author'
    )
    empty_value_display = 'пусто'
