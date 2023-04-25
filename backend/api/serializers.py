from django.db.transaction import atomic
from django.shortcuts import get_object_or_404
from djoser.serializers import UserCreateSerializer, UserSerializer
from drf_extra_fields.fields import Base64ImageField
from recipes.models import (Favorite, Ingredient, Recipes,
                            RecipesIngredientList, ShoppingCart, Tags)
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.serializers import (IntegerField, ModelSerializer,
                                        PrimaryKeyRelatedField, ReadOnlyField,
                                        SerializerMethodField)
from users.models import Subscribe, User


class TagsSerializer(ModelSerializer):

    class Meta:
        model = Tags
        fields = (
            'id',
            'name',
            'color',
            'slug',
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
    name = ReadOnlyField(source='ingredient.name')
    id = ReadOnlyField(source='ingredient.id')
    measurement_unit = ReadOnlyField(source='ingredient.measurement_unit')

    class Meta:
        model = RecipesIngredientList
        fields = (
            'id',
            'name',
            'measurement_unit',
            'amount',
        )

    def get_measurement_unit(self, ingredient_in_recipe):
        return ingredient_in_recipe.ingredient.measurement_unit

    def get_name(self, ingredient_in_recipe):
        return ingredient_in_recipe.ingredient.name


class IngredientCreateSerializer(ModelSerializer):
    id = PrimaryKeyRelatedField(
        source='ingredient',
        queryset=Ingredient.objects.all()
    )
    amount = IntegerField()

    class Meta:
        model = RecipesIngredientList
        fields = ('id', 'amount')


class RecipesForFollowerSerializer(ModelSerializer):

    class Meta:
        model = Recipes
        fields = (
            'id',
            'name',
            'image',
            'cooking_time',
        )


class CustomUserSerializer(UserSerializer):
    is_subscribed = SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = (
            'id',
            'username',
            'first_name',
            'last_name',
            'email',
            'is_subscribed',
        )

    def get_is_subscribed(self, author):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return Subscribe.objects.filter(user=user, author=author).exists()


class CustomCreateUserSerializer(UserCreateSerializer):

    class Meta:
        model = User
        fields = (
            'email', 'username', 'first_name',
            'last_name', 'password')


class RecipesSerializer(ModelSerializer):
    author = CustomUserSerializer(read_only=True)
    ingredients = SerializerMethodField()
    tags = TagsSerializer(many=True)
    is_favorited = SerializerMethodField()
    is_in_shopping_cart = SerializerMethodField()

    class Meta:
        model = Recipes
        fields = (
            'id',
            'author',
            'ingredients',
            'tags',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time',
        )

    def get_ingredients(self, obj):
        queryset = RecipesIngredientList.objects.filter(recipe=obj)
        return IngredientsInRecipeSerializer(queryset, many=True).data

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        if Favorite.objects.filter(
            user=request.user,
            recipe_id=obj.id
        ).exists():
            return True
        return False

    def get_is_in_shopping_cart(self, recipe):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return user.shopping_cart.filter(recipe=recipe).exists()


class RecipeCreateSerializer(ModelSerializer):
    author = CustomUserSerializer(read_only=True)
    image = Base64ImageField()
    ingredients = IngredientCreateSerializer(many=True)
    tags = PrimaryKeyRelatedField(
        queryset=Tags.objects.all(),
        many=True
    )

    class Meta:
        model = Recipes
        fields = (
            'id',
            'author',
            'name',
            'cooking_time',
            'image',
            'ingredients',
            'tags',
            'text',
        )

    @staticmethod
    def create_ingredients(data, recipe):
        for ingredient in data:
            ingredient = get_object_or_404(Ingredient, pk=ingredient['id'])
            RecipesIngredientList.objects.create(
                recipe=recipe,
                ingredient=ingredient['id'],
                amount=ingredient['amount']
            )

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

    @atomic
    def create(self, validated_data):
        ingredients_data = validated_data.pop('ingredients')
        tags_data = validated_data.pop('tags')
        recipe = Recipes.objects.create(
            author=self.context.get('request').user,
            **validated_data
        )
        bulk_data = [
            RecipesIngredientList(
                recipe=recipe,
                ingredient=ingredient_data['ingredient'],
                amount=ingredient_data['amount'])
            for ingredient_data in ingredients_data
        ]
        recipe.tags.set(tags_data)
        RecipesIngredientList.objects.bulk_create(bulk_data)
        return recipe

    @atomic
    def update(self, instance, validated_data):
        tags = validated_data.pop('tags', None)
        if tags is not None:
            instance.tags.set(tags)
        ingredients = validated_data.pop('ingredients', None)
        if ingredients is not None:
            instance.ingredients.clear()
        amount_set = RecipesIngredientList.objects.filter(
            recipe__id=instance.id)
        amount_set.delete()
        bulk_data = (
            RecipesIngredientList(
                recipe=instance,
                ingredient=ingredient_data['ingredient'],
                amount=ingredient_data['amount'])
            for ingredient_data in ingredients
        )
        RecipesIngredientList.objects.bulk_create(bulk_data)
        return super().update(instance, validated_data)

    def to_representation(self, instance):
        return RecipesSerializer(
            instance,
            context={'request': self.context.get('request')}
        ).data


class SubscribeSerializer(CustomUserSerializer):
    recipes = SerializerMethodField(method_name='get_recipes_count')
    recipes_count = SerializerMethodField(method_name='get_recipes')

    class Meta(CustomUserSerializer.Meta):
        fields = CustomUserSerializer.Meta.fields + (
            'recipes_count', 'recipes'
        )
        read_only_fields = ('email', 'username')

    def validate(self, data):
        author = self.instance
        user = self.context.get('request').user
        if Subscribe.objects.filter(author=author, user=user).exists():
            raise ValidationError(
                detail='Подписка уже оформлена.',
                code=status.HTTP_400_BAD_REQUEST
            )
        if user == author:
            raise ValidationError(
                detail='Подписка на самого себя запрещена.',
                code=status.HTTP_400_BAD_REQUEST
            )
        return data

    def get_recipes(self, obj):
        request = self.context.get('request')
        recipes_limit = request.GET.get('recipes_limit')
        recipes = Recipes.objects.filter(author=obj.author)
        if recipes_limit:
            recipes = recipes[:int(recipes_limit)]
        serializer = RecipesForFollowerSerializer(recipes, many=True)
        return serializer.data

    def get_recipes_count(self, obj):
        return obj.recipes.count()
