from django.contrib import admin

from .models import (Favorite, Ingredient, Recipes, RecipesIngredientList,
                     ShoppingCart, Tags)


@admin.register(Tags)
class TagsAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'color',
        'slug',
    )
    search_fields = ('name',)
    search_help_text = 'Поиск по названию тега'
    empty_value_display = 'пусто'


@admin.register(Ingredient)
class IngredientsAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'measurement_unit',
    )
    search_fields = ('name',)
    search_help_text = 'Поиск по названию ингредиента'
    empty_value_display = 'пусто'


@admin.register(Recipes)
class RecipesAdmin(admin.ModelAdmin):
    list_display = (
        'author',
        'name',
        'image',
        'text',
        'cooking_time',
        'added_to_favorites',
    )
    search_fields = (
        'author',
        'name',
        'tags',
    )
    search_help_text = 'Поиск по автору, названию рецепта и тегу'
    empty_value_display = 'пусто'

    @admin.display(description='В избранном у:')
    def added_to_favorites(self, obj):
        return (
            f'Рецепт добавлен в избранное '
            f'{obj.favorite.count()}'
        )


@admin.register(RecipesIngredientList)
class RecipesIngredientListAdmin(admin.ModelAdmin):
    list_display = (
        'recipe',
        'ingredient',
        'amount',
    )
    empty_value_display = 'пусто'


admin.site.register(Favorite)
admin.site.register(ShoppingCart)
