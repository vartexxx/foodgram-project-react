# Generated by Django 4.1.7 on 2023-04-14 04:20

import django.core.validators
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('recipes', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tags',
            name='color',
            field=models.CharField(help_text='Введите цвет тега', max_length=7, unique=True, verbose_name='Цвет тега'),
        ),
        migrations.AlterField(
            model_name='tags',
            name='slug',
            field=models.SlugField(help_text='Введите уникальный идентификатор', max_length=200, unique=True, validators=[django.core.validators.RegexValidator(message='Уникальный идентификатор введен неккоректно', regex='^[-a-zA-Z0-9_]+$')], verbose_name='Уникальный идентификатор'),
        ),
        migrations.RenameModel(
            old_name='Ingredients',
            new_name='Ingredient',
        ),
        migrations.CreateModel(
            name='ShoppingCart',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('recipe', models.ForeignKey(help_text='Введите рецепт', on_delete=django.db.models.deletion.CASCADE, to='recipes.recipes', verbose_name='Рецепт')),
                ('user', models.ForeignKey(help_text='Введите автора', on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Автор')),
            ],
            options={
                'verbose_name': 'Корзина',
                'verbose_name_plural': 'Корзина',
                'default_related_name': 'shoppingcart',
            },
        ),
        migrations.CreateModel(
            name='RecipesIngredientList',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.PositiveIntegerField(help_text='Выберите количество ингредиентов', validators=[django.core.validators.MinValueValidator(1, message='Ингредиентов должно быть не меньше 1')], verbose_name='Количество ингредиентов')),
                ('ingredient', models.ForeignKey(help_text='Выберие ингредиент', on_delete=django.db.models.deletion.CASCADE, to='recipes.ingredient', verbose_name='Ингредиент')),
                ('recipe', models.ForeignKey(help_text='Введите рецепт', on_delete=django.db.models.deletion.CASCADE, to='recipes.recipes', verbose_name='Рецепт')),
            ],
            options={
                'verbose_name': 'Ингредиент',
                'verbose_name_plural': 'Количество ингредиентов',
                'ordering': ('-id',),
                'default_related_name': 'recipes_amount',
            },
        ),
        migrations.CreateModel(
            name='Favorite',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('recipe', models.ForeignKey(help_text='Введите рецепт', on_delete=django.db.models.deletion.CASCADE, to='recipes.recipes', verbose_name='Рецепт')),
                ('user', models.ForeignKey(help_text='Введите автора', on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Автор')),
            ],
            options={
                'verbose_name': 'Избранное',
                'verbose_name_plural': 'Избранные',
                'default_related_name': 'favorite',
            },
        ),
        migrations.AddConstraint(
            model_name='shoppingcart',
            constraint=models.UniqueConstraint(fields=('user', 'recipe'), name='unique_shopping_cart'),
        ),
        migrations.AddConstraint(
            model_name='recipesingredientlist',
            constraint=models.UniqueConstraint(fields=('recipe', 'ingredient'), name='unique_recipes_list'),
        ),
        migrations.AddConstraint(
            model_name='favorite',
            constraint=models.UniqueConstraint(fields=('user', 'recipe'), name='unique_favorite_list'),
        ),
    ]
