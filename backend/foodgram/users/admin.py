from django.contrib import admin
from django.contrib.auth import get_user_model

from .models import Follow

User = get_user_model()


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'username',
        'first_name',
        'last_name',
        'password',
        'email',
    )
    search_fields = (
        'email',
        'username'
    )
    empty_value_display = 'пусто'


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'author'
    )
    empty_value_display = 'пусто'
