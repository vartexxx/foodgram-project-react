from rest_framework.test import APITestCase
from users.models import User

from ..models import (Favorite, Ingredient, Recipes, RecipesIngredientList,
                      ShoppingCart, Tags)


class UrlsTestCase(APITestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.user = User.objects.create(
            username='vlad',
            first_name='vladislav',
            last_name='burlaka',
            password='1111111',
            email='vlad@yandex.ru'
        )
        cls.tags = Tags.objects.create(
            name='tags_name',
            color='#999999',
            slug='tags_slug',
        )
        cls.ingredient = Ingredient.objects.create(
            name='ingredient_name',
            measurement_unit='measurement_unit_test',
        )
        cls.recipes = Recipes.objects.create(
            author=cls.user,
            name='recipes_name',
            image='image',
            text='text',
            cooking_time=120,
        )
        cls.amount = RecipesIngredientList.objects.create(
            recipe=cls.recipes,
            ingredient=cls.ingredient,
            amount=30,
        )
        cls.favorite = Favorite.objects.create(
            recipe=cls.recipes,
            user=cls.user,
        )
        cls.shopping_cart = ShoppingCart.objects.create(
            recipe=cls.recipes,
            user=cls.user,
        )

    def test_models_have_correct_object_names(self):
        """
        Корректно работает метод __str__ моделей
        Favorite, Ingredient, Recipes, RecipesIngredientList, ShoppingCart
        Tags.
        """
        self.assertEqual(str(self.tags), self.tags.name)
        self.assertEqual(str(self.ingredient), self.ingredient.name)
        self.assertEqual(str(self.recipes), self.recipes.name)
        self.assertEqual(str(self.amount), self.amount.ingredient.name)
        self.assertEqual(
            str(self.favorite),
            f'Рецепт {self.favorite.recipe} '
            f'находится в избранном у {self.favorite.user}'
        )
        self.assertEqual(
            str(self.shopping_cart),
            f'Рецепт {self.shopping_cart.recipe} в '
            f'корзине пользователя {self.shopping_cart.user}'
        )

    def test_models_many_to_many_objects(self):
        """
        Тестирование связей ManyToMany в моделях.
        """
        self.recipes.tags.set([self.tags])
        self.recipes.ingredients.set([self.ingredient])
        object_in_db = Recipes.objects.get(id=self.recipes.id)
        self.assertEqual(set(object_in_db.tags.all()), {self.tags})
        self.assertEqual(
            set(object_in_db.ingredients.all()),
            {self.ingredient}
        )

    def test_verbose_name_tags(self):
        """Корректно прописаны verbose_name для модели Tags"""
        field_verboses = {
            'name': 'Название тега',
            'color': 'Цвет тега',
            'slug': 'Уникальный идентификатор',
        }
        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(
                    Tags._meta.get_field(field).verbose_name,
                    expected_value
                )

    def test_verbose_name_ingredient(self):
        """Корректно прописаны verbose_name для модели Ingredient"""
        field_verboses = {
            'name': 'Название ингредиента',
            'measurement_unit': 'Единица измерения',
        }
        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(
                    Ingredient._meta.get_field(field).verbose_name,
                    expected_value
                )

    def test_verbose_name_recipes(self):
        """Корректно прописаны verbose_name для модели Recipes"""
        field_verboses = {
            'author': 'Пользователь(автор) рецепта',
            'name': 'Название рецепта',
            'image': 'Фотография блюда',
            'tags': 'Теги',
            'ingredients': 'Ингредиенты',
            'text': 'Текст рецепта',
            'cooking_time': 'Время приготовления в минутах',
        }
        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(
                    Recipes._meta.get_field(field).verbose_name,
                    expected_value
                )

    def test_verbose_name_recipes_ingredient_list(self):
        """Корректно прописаны verbose_name для модели RecipesIngredientList"""
        field_verboses = {
            'recipe': 'Рецепт',
            'ingredient': 'Ингредиент',
            'amount': 'Количество ингредиентов',
        }
        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(
                    RecipesIngredientList._meta.get_field(field).verbose_name,
                    expected_value
                )

    def test_verbose_name_favorite(self):
        """Корректно прописаны verbose_name для модели Favorite"""
        field_verboses = {
            'recipe': 'Рецепт',
            'user': 'Пользователь',
        }
        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(
                    Favorite._meta.get_field(field).verbose_name,
                    expected_value
                )

    def test_verbose_name_shopping_cart(self):
        """Корректно прописаны verbose_name для модели ShoppingCart"""
        field_verboses = {
            'recipe': 'Рецепт',
            'user': 'Пользователь',
        }
        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(
                    ShoppingCart._meta.get_field(field).verbose_name,
                    expected_value
                )

    def test_help_text_tags(self):
        """Корректно прописаны help_text для Tags"""
        field_help_texts = {
            'name': 'Введите название тега',
            'color': 'Введите цвет тега',
            'slug': 'Введите уникальный идентификатор',
        }
        for field, expected_value in field_help_texts.items():
            with self.subTest(field=field):
                self.assertEqual(
                    Tags._meta.get_field(field).help_text,
                    expected_value
                )

    def test_help_text_ingredient(self):
        """Корректно прописаны help_text для Ingredient"""
        field_help_texts = {
            'name': 'Введите ингредиент',
            'measurement_unit': 'Введите единицу измерения',
        }
        for field, expected_value in field_help_texts.items():
            with self.subTest(field=field):
                self.assertEqual(
                    Ingredient._meta.get_field(field).help_text,
                    expected_value
                )

    def test_help_text_recipes(self):
        """Корректно прописаны help_text для Recipes"""
        field_help_texts = {
            'author': 'Выберите пользователя(автора) рецепта',
            'name': 'Введите название рецепта',
            'image': 'Добавьте фотографию блюда',
            'tags': 'Выберите теги',
            'ingredients': 'Выберите ингредиенты',
            'text': 'Введите текст рецепта',
            'cooking_time': 'Введите время приготовления в минутах',
        }
        for field, expected_value in field_help_texts.items():
            with self.subTest(field=field):
                self.assertEqual(
                    Recipes._meta.get_field(field).help_text,
                    expected_value
                )

    def test_help_text_recipes_ingredient_list(self):
        """Корректно прописаны help_text для RecipesIngredientList"""
        field_help_texts = {
            'recipe': 'Выберите рецепт',
            'ingredient': 'Выберие ингредиент',
            'amount': 'Введите количество ингредиентов',
        }
        for field, expected_value in field_help_texts.items():
            with self.subTest(field=field):
                self.assertEqual(
                    RecipesIngredientList._meta.get_field(field).help_text,
                    expected_value
                )

    def test_help_text_favorite(self):
        """Корректно прописаны help_text для Favorite"""
        field_help_texts = {
            'recipe': 'Выберите рецепт',
            'user': 'Выберите пользователя',
        }
        for field, expected_value in field_help_texts.items():
            with self.subTest(field=field):
                self.assertEqual(
                    Favorite._meta.get_field(field).help_text,
                    expected_value
                )

    def test_help_text_shopping_cart(self):
        """Корректно прописаны help_text для ShoppingCart"""
        field_help_texts = {
            'recipe': 'Выберите рецепт',
            'user': 'Выберите пользователя',
        }
        for field, expected_value in field_help_texts.items():
            with self.subTest(field=field):
                self.assertEqual(
                    ShoppingCart._meta.get_field(field).help_text,
                    expected_value
                )
