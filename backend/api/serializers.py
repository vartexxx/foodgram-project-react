from django.db.transaction import atomic
from drf_extra_fields.fields import Base64ImageField
from recipes.models import Ingredient, IngredientAmount, Recipe, Tag
from rest_framework.exceptions import ValidationError
from rest_framework.serializers import (ModelSerializer,
                                        PrimaryKeyRelatedField, ReadOnlyField,
                                        SerializerMethodField,
                                        SlugRelatedField)
from users.serializers import CustomUserSerializer


class TagsSerializer(ModelSerializer):

    class Meta:
        model = Tag
        fields = (
            'id',
            'name',
            'color',
            'slug'
        )


class IngredientSerializer(ModelSerializer):

    class Meta:
        model = Ingredient
        fields = (
            'id',
            'name',
            'measurement_unit',
        )


class IngredientsInRecipeSerializer(ModelSerializer):
    id = ReadOnlyField(source='ingredient.id')
    name = ReadOnlyField(source='ingredient.name')
    measurement_unit = ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = IngredientAmount
        fields = (
            'id',
            'name',
            'measurement_unit',
            'amount'
        )

    def get_measurement_unit(self, ingredient_in_recipe):
        return ingredient_in_recipe.ingredient.measurement_unit

    def get_name(self, ingredient_in_recipe):
        return ingredient_in_recipe.ingredient.name


class IngredientCreateSerializer(ModelSerializer):
    id = PrimaryKeyRelatedField(queryset=Ingredient.objects.all())

    class Meta:
        model = IngredientAmount
        fields = (
            'id',
            'amount'
        )


class RecipeCreateSerializer(ModelSerializer):
    ingredients = IngredientCreateSerializer(many=True)
    tags = SlugRelatedField(
        queryset=Tag.objects.all(),
        slug_field='id',
        many=True
    )
    image = Base64ImageField()

    class Meta:
        model = Recipe
        exclude = ('author', )

    @staticmethod
    def validation(data):
        cooking_time = data['cooking_time']
        ingredients = data['ingredients']
        tags = data['tags']
        if not tags:
            raise ValidationError(
                'Должен быть хотя бы один тег.'
            )
        if not ingredients:
            raise ValidationError(
                'Должен быть хотя бы один ингредиент.'
            )
        if int(cooking_time) <= 0:
            raise ValidationError(
                'Время приготовления не может быть меньше 0.'
            )
        ingredients_list = [ingredient['id'] for ingredient in ingredients]
        for value in ingredients_list:
            if ingredients_list.count(value) > 1:
                raise ValidationError(
                    'Ингредиенты не должны повторяться.'
                )
        tags_list = [tag for tag in tags]
        for value in tags_list:
            if tags_list.count(value) > 1:
                raise ValidationError(
                    'Теги не должны повторяться.'
                )

    def create_ingredients(self, recipe, ingredients):
        IngredientAmount.objects.bulk_create(
            [IngredientAmount(
                recipe=recipe,
                ingredient=ingredient.get('id'),
                amount=ingredient.get('amount')
            ) for ingredient in ingredients]
        )

    @atomic
    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        self.create_ingredients(recipe, ingredients)
        return recipe

    @atomic
    def update(self, instance, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        instance = super().update(instance, validated_data)
        instance.tags.clear()
        instance.tags.set(tags)
        instance.ingredients.clear()
        self.create_ingredients(instance, ingredients)
        instance.save
        return instance

    def to_representation(self, instance):
        return ReadRecipeSerializer(
            instance,
            context={'request': self.context.get('request')}
        ).data


class ReadRecipeSerializer(ModelSerializer):
    author = CustomUserSerializer()
    ingredients = IngredientsInRecipeSerializer(
        many=True,
        source='recipe_ingredient'
    )
    tags = TagsSerializer(many=True)
    image = Base64ImageField()
    is_favorited = SerializerMethodField()
    is_in_shopping_cart = SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'author',
            'image',
            'text',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'tags',
            'cooking_time',
            'pub_date'
        )

    def get_is_favorited(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return user.favorites.filter(recipe=obj).exists()

    def get_is_in_shopping_cart(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return user.shopping_cart.filter(recipe=obj).exists()
