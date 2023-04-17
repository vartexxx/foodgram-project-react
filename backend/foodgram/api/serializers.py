from django.db.models import F
from djoser.serializers import UserCreateSerializer, UserSerializer
from drf_extra_fields.fields import Base64ImageField
from recipes.models import (Favorite, Ingredient, Recipes,
                            RecipesIngredientList, Tags)
from rest_framework.serializers import (CharField, IntegerField,
                                        ModelSerializer,
                                        PrimaryKeyRelatedField, ReadOnlyField,
                                        SerializerMethodField)
from users.models import Subscribe, User


class TagsSerializer(ModelSerializer):
    """Сериализатор тегов."""

    class Meta:
        model = Tags
        fields = (
            'id',
            'name',
            'color',
            'slug',
        )


class IngredientSerializer(ModelSerializer):
    """Сериализатор ингредиентов."""

    class Meta:
        model = Ingredient
        fields = (
            'id',
            'name',
            'measurement_unit',
        )


class IngredientsInRecipeSerializer(ModelSerializer):
    """Сериализатор вывода ингредиентов в рецепте"""
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


class IngredientCreateSerializer(ModelSerializer):
    """Сериализатор для создания ингредиента"""
    id = PrimaryKeyRelatedField(
        source='ingredient',
        queryset=Ingredient.objects.all()
    )
    amount = IntegerField()

    class Meta:
        model = RecipesIngredientList
        fields = ('id', 'amount')


class RecipesForFollowerSerializer(ModelSerializer):
    image = Base64ImageField()

    class Meta:
        model = Recipes
        fields = (
            'id',
            'name',
            'image',
            'cooking_time',
        )


class CustomUserSerializer(UserSerializer):
    """Сериализатор для кастомной модели пользователя"""
    is_subscribed = SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
        )

    def get_is_subscribed(self, args):
        """Проверка подписки пользователя на автора"""
        user = self.context.get('request').user
        if user.is_authenticated:
            return Subscribe.objects.filter(user=user, author=args).exists()
        return False


class CustomCreateUserSerializer(UserCreateSerializer):
    """Сериализатор для создания/регистрации пользователя"""

    class Meta:
        model = User
        fields = (
            'id',
            'username',
            'first_name',
            'last_name',
            'password',
            'email',
        )


class RecipesSerializer(ModelSerializer):
    """Сериализатор рецептов."""
    author = CustomUserSerializer(read_only=True)
    image = Base64ImageField()
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

    @staticmethod
    def get_ingredients(arg):
        return IngredientsInRecipeSerializer(
            RecipesIngredientList.objects.filter(recipe=arg),
            many=True,
        ).data

    def get_is_favorited(self, arg):
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        if Favorite.objects.filter(
            user=request.user,
            recipe__id=arg.id
        ).exists():
            return True
        return False

    def get_is_in_shopping_cart(self, arg):
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        return True


class RecipeCreateSerializer(ModelSerializer):
    """Сериализатор добавления рецепта"""
    name = CharField()
    cooking_time = IntegerField()
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
            ingredient_id = ingredient['id']
            amount = ingredient['amount']
            if RecipesIngredientList.objects.filter(
                    recipe=recipe, ingredient=ingredient_id).exists():
                amount += F('amount')
            RecipesIngredientList.objects.update_or_create(
                recipe=recipe, ingredient=ingredient_id,
                defaults={'amount': amount}
            )

    def create(self, validated_data):
        tags = validated_data.pop('tags')
        recipe = Recipes.objects.create(
            image=validated_data.pop('image'),
            author=self.context.get('request').user,
            **validated_data
        )
        self.create_ingredients(validated_data.pop('ingredients'), recipe)
        recipe.tags.set(tags)
        return recipe

    def update(self, instance, validated_data):
        tags = validated_data.pop('tags')
        RecipesIngredientList.objects.filter(
            recipe=instance
        ).delete()
        self.create_ingredients(validated_data.pop('ingredients'), instance)
        instance.tags.set(tags)
        return super().update(instance, validated_data)

    def to_representation(self, instance):
        return RecipesSerializer(
            instance,
            context={'request': self.context.get('request')}
        ).data


class FavoriteSerializer(ModelSerializer):
    """Сериализатор списка избранного"""
    user = PrimaryKeyRelatedField(
        queryset=User.objects.all()
    )
    recipe = PrimaryKeyRelatedField(
        queryset=Recipes.objects.all()
    )

    class Meta:
        model = Favorite
        fields = (
            'user',
            'recipe'
        )

    def to_representation(self, instance):
        return RecipesForFollowerSerializer(
            instance.recipe,
            context={
                'request': self.context.get('request')
            }
        ).data


class SubscribeSerializer(CustomUserSerializer):
    """Сериализатор подписок"""
    recipes = SerializerMethodField()
    recipes_count = SerializerMethodField()

    class Meta(CustomUserSerializer.Meta):
        fields = CustomUserSerializer.Meta.fields + (
            'recipes_count', 'recipes'
        )
        read_only_fields = ('email', 'username')

    def get_recipes(self, arg):
        request = self.context.get('request')
        limit = request.GET.get('recipes_limit')
        recipes = arg.recipes.all()
        if limit:
            recipes = recipes[:int(limit)]
        serializer = RecipesForFollowerSerializer(
            recipes,
            many=True,
            read_only=True
        )
        return serializer.data

    def get_recipes_count(self, arg):
        return arg.recipes.count()
