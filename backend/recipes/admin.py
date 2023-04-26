# from django.contrib import admin

# from .models import (Favorite, Ingredient, IngredientAmount, Recipe,
#                      ShoppingCart, Tag)


# @admin.register(Tag)
# class TagsAdmin(admin.ModelAdmin):
#     list_display = (
#         'name',
#         'color',
#         'slug',
#     )
#     search_fields = ('name',)
#     search_help_text = 'Поиск по названию тега'
#     empty_value_display = 'пусто'


# @admin.register(Ingredient)
# class IngredientsAdmin(admin.ModelAdmin):
#     list_display = (
#         'name',
#         'measurement_unit',
#     )
#     search_fields = ('name',)
#     search_help_text = 'Поиск по названию ингредиента'
#     empty_value_display = 'пусто'


# @admin.register(Recipe)
# class RecipesAdmin(admin.ModelAdmin):
#     list_display = (
#         'author',
#         'name',
#         'image',
#         'text',
#         'cooking_time',
#         'added_to_favorites',
#     )
#     search_fields = (
#         'author',
#         'name',
#         'tags',
#     )
#     search_help_text = 'Поиск по автору, названию рецепта и тегу'
#     empty_value_display = 'пусто'

#     @admin.display(description='В избранном у:')
#     def added_to_favorites(self, obj):
#         return (
#             f'Рецепт добавлен в избранное '
#             f'{obj.favorite.count()}'
#         )


# @admin.register(IngredientAmount)
# class IngredientAmountAdmin(admin.ModelAdmin):
#     list_display = (
#         'recipe',
#         'ingredient',
#         'amount',
#     )
#     empty_value_display = 'пусто'


# admin.site.register(Favorite)
# admin.site.register(ShoppingCart)
from django.contrib import admin
from django.utils.safestring import mark_safe

from .models import (Favorite, Ingredient, IngredientAmount, Recipe,
                     ShoppingCart, Tag)


class IngredientAmountInline(admin.StackedInline):
    model = IngredientAmount


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = [
        'name',
        'author',
        'pub_date',
        'cooking_time',
        'added_to_favorites',
    ]
    list_editable = ['author', ]
    search_fields = ['name', ]
    list_filter = ['author', 'name', 'tags', 'pub_date']
    inlines = (IngredientAmountInline, )
    empty_value_display = 'пусто'

    @admin.display(description='В избранном у:')
    def added_to_favorites(self, obj):
        return (
            f'Рецепт добавлен в избранное '
            f'{obj.favorites.count()}'
        )


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ['name', 'measurement_unit']
    search_fields = ['name', ]
    search_help_text = 'Поиск по названию ингредиента'
    list_filter = ['name', ]
    empty_value_display = 'пусто'


@admin.register(IngredientAmount)
class IngredientAmountAdmin(admin.ModelAdmin):
    list_display = ['recipe', 'ingredient', 'amount']
    empty_value_display = 'пусто'


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ['user', 'recipe']
    empty_value_display = 'пусто'


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ['user', 'recipe']
    empty_value_display = 'пусто'


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ['name', 'color', 'slug']
    search_fields = ('name', )
    search_help_text = 'Поиск по названию тега'
    empty_value_display = 'пусто'
