from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, RegexValidator
from django.db import models

User = get_user_model()


class Tag(models.Model):
    """Класс модели тегов"""

    name = models.CharField(
        max_length=200,
        unique=True,
        verbose_name='Название тега',
        help_text='Введите название тега',
    )
    color = models.TextField(
        max_length=7,
        verbose_name='Цвет тега',
        help_text='Введите цвет тега',
        unique=True,
    )
    slug = models.SlugField(
        max_length=200,
        validators=[RegexValidator(
            regex=r'^[-a-zA-Z0-9_]+$',
            message='Уникальный идентификатор введен неккоректно',
        )],
        verbose_name='Уникальный идентификатор',
        help_text='Введите уникальный идентификатор',
        unique=True
    )

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self) -> str:
        return self.name


class Ingredient(models.Model):
    """Класс модели ингредиентов"""

    name = models.CharField(
        max_length=200,
        verbose_name='Название ингредиента',
        help_text='Введите ингредиент',
    )
    measurement_unit = models.CharField(
        max_length=200,
        verbose_name='Единица измерения',
        help_text='Введите единицу измерения',
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        constraints = [models.UniqueConstraint(
            fields=['name', 'measurement_unit'],
            name='unique_measurement'
        )]

    def __str__(self) -> str:
        return self.name


class Recipe(models.Model):
    """Класс модели рецептов"""

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        help_text='Выберите пользователя(автора) рецепта',
        verbose_name='Пользователь(автор) рецепта',
    )
    name = models.CharField(
        max_length=200,
        verbose_name='Название рецепта',
        help_text='Введите название рецепта',
    )
    image = models.ImageField(
        upload_to='recipe_img/',
        verbose_name='Фотография блюда',
        help_text='Добавьте фотографию блюда',
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name='Теги',
        help_text='Выберите теги',
        related_name='recipes',
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='IngredientAmount',
        verbose_name='Ингредиенты',
        help_text='Выберите ингредиенты',
    )
    text = models.TextField(
        verbose_name='Текст рецепта',
        help_text='Введите текст рецепта',
    )
    cooking_time = models.PositiveIntegerField(
        verbose_name='Время приготовления в минутах',
        help_text='Введите время приготовления в минутах',
        validators=[MinValueValidator(
            1,
            message='Время приготовления блюда не может быть меньше 1 минуты',
        )]
    )
    pub_date = models.DateField(
        auto_now_add=True,
        verbose_name='Дата публикации'
    )

    class Meta:
        ordering = ['pub_date']
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self) -> str:
        return self.name


class IngredientAmount(models.Model):
    """Класс модели списка ингредиентов"""

    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='recipe_ingredient',
        verbose_name='Рецепт',
        help_text='Выберите рецепт',
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name='Ингредиент',
        help_text='Выберие ингредиент',
    )
    amount = models.PositiveIntegerField(
        verbose_name='Количество ингредиентов',
        help_text='Введите количество ингредиентов',
        validators=[MinValueValidator(
            1,
            message='Ингредиентов должно быть не меньше 1'
        )]
    )

    class Meta:
        ordering = ('id', )
        verbose_name = 'Ингредиенты для рецепта'
        verbose_name_plural = 'Ингредиенты для рецептов'

    def __str__(self) -> str:
        return self.ingredient.name


class Favorite(models.Model):
    """Класс модели подписок(избранного)"""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name='Пользователь',
        help_text='Выберите пользователя',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name='Рецепт',
        help_text='Выберите рецепт',
    )

    class Meta:
        ordering = ('id', )
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранные'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'], name='unique_favorites_recipe'
            )
        ]

    def __str__(self) -> str:
        return (
            f'Рецепт {self.recipe} находится в избранном у {self.user}'
        )


class ShoppingCart(models.Model):
    """Класс модели корзины"""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='shopping_cart',
        verbose_name='Пользователь',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='shopping_cart',
        verbose_name='Рецепт',
    )

    class Meta:
        ordering = ('id', )
        verbose_name = 'Корзину'
        verbose_name_plural = 'Корзина'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'], name='unique_shopping_cart'
            )
        ]

    def __str__(self) -> str:
        return (
            f'Рецепт {self.recipe} в корзине пользователя {self.user}'
        )
