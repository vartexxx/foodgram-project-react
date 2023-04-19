from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, RegexValidator
from django.db import models

User = get_user_model()


class Tags(models.Model):
    """Класс модели тегов"""

    name = models.CharField(
        max_length=200,
        unique=True,
        verbose_name='Название тега',
        help_text='Введите название тега',
    )
    color = models.CharField(
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
        unique=True,
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


class Recipes(models.Model):
    """Класс модели рецептов"""

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        help_text='Выберите пользователя(автора) рецепта',
        verbose_name='Пользователь(автор) рецепта',
    )
    name = models.CharField(
        max_length=200,
        verbose_name='Название рецепта',
        help_text='Введите название рецепта',
    )
    image = models.FileField(
        upload_to='recipe_img/',
        verbose_name='Фотография блюда',
        help_text='Добавьте фотографию блюда',
    )
    tags = models.ManyToManyField(
        Tags,
        verbose_name='Теги',
        help_text='Выберите теги',
    )
    ingredients = models.ManyToManyField(
        Ingredient,
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

    class Meta:
        ordering = ('-id',)
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        constraints = [models.UniqueConstraint(
            fields=['author', 'name'], name='unique_recipes'
        )]

    def __str__(self) -> str:
        return self.name


class RecipeDefaultModel(models.Model):
    """Абстрактный базовый класс модели рецептов"""

    recipe = models.ForeignKey(
        Recipes,
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
        help_text='Выберите рецепт',
    )

    class Meta:
        abstract = True


class UserDefaultModel(models.Model):
    """Абстрактный базовый класс модели пользователя"""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
        help_text='Выберите пользователя',
    )

    class Meta:
        abstract = True


class RecipesIngredientList(RecipeDefaultModel):
    """Класс модели списка ингредиентов"""

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
        ordering = ('-id',)
        verbose_name = 'Ингредиенты'
        verbose_name_plural = 'Количество ингредиентов'
        constraints = [models.UniqueConstraint(
            fields=['recipe', 'ingredient'], name='unique_recipes_list'
        )]

    def __str__(self) -> str:
        return self.ingredient.name


class Favorite(RecipeDefaultModel, UserDefaultModel):
    """Класс модели подписок(избранного)"""

    class Meta:
        default_related_name = 'favorite'
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранные'
        constraints = [models.UniqueConstraint(
            fields=['user', 'recipe'], name='unique_favorite_list'
        )]

    def __str__(self) -> str:
        return (
            f'Рецепт {self.recipe} находится в избранном у {self.user}'
        )


class ShoppingCart(RecipeDefaultModel, UserDefaultModel):
    """Класс модели корзины"""

    class Meta:
        default_related_name = 'shoppingcart'
        verbose_name = 'Корзину'
        verbose_name_plural = 'Корзина'
        constraints = [models.UniqueConstraint(
            fields=['user', 'recipe'], name='unique_shopping_cart'
        )]

    def __str__(self) -> str:
        return (
            f'Рецепт {self.recipe} в корзине пользователя {self.user}'
        )
