from django.db.models import F
from djoser.serializers import UserCreateSerializer, UserSerializer
from drf_extra_fields.fields import Base64ImageField
from recipes.models import (Favorite, Ingredient, Recipes,
                            RecipesIngredientList, ShoppingCart, Tags)
from rest_framework.generics import UpdateAPIView
from rest_framework.serializers import (CharField, EmailField, IntegerField,
                                        ModelSerializer,
                                        PrimaryKeyRelatedField, ReadOnlyField,
                                        Serializer, SerializerMethodField,
                                        ValidationError)
from users.models import Follow, User


class TagsSerializer(ModelSerializer):
    """Сериализатор для модели тегов"""

    class Meta:
        model = Tags
        fields = '__all__'


class IngredientSerializer(ModelSerializer):
    """Сериализатор для модели ингредиентов"""

    class Meta:
        model = Ingredient
        fields = '__all__'


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
    id = IntegerField()
    amount = IntegerField()

    class Meta:
        model = RecipesIngredientList
        fields = ('id', 'amount')

    def amount_validation(self, arg):
        if arg < 1:
            raise ValidationError(
                'Количество ингредиентов не может быть меньше 1'
            )
        return arg


class RecipesForFollowerSerializer(ModelSerializer):
    image = Base64ImageField()

    class Meta:
        model = Recipes
        fields = (
            'id',
            'name',
            'image',
            'cooking_time'
        )


class CustomUserSerializer(UserSerializer):
    """Сериализатор для кастомной модели пользователя"""
    is_subscribe = SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'id',
            'email',
            'username',
            'first_name',
            'last_name',
            'is_subscribe',
        )

    def get_is_subscribe(self, args):
        """Проверка подписки пользователя на автора"""
        user = self.context.get('request').user
        if user.is_authenticated:
            return Follow.objects.filter(user=user, author=args).exists()
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
    author = CustomUserSerializer()
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
            'image',
            'ingredients',
            'tags',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
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
        if Favorite.objects.filter(user=request.user,
                                   recipe__id=arg.id).exists():
            return True
        return False

    def get_is_in_shopping_cart(self, arg):
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        return True


class RecipeCreateSerializer(ModelSerializer):
    """Сериализатор добавления рецепта"""
    author = CustomUserSerializer()
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
            'author',
            'name',
            'cooking_time',
            'image',
            'ingredients',
            'tags',
            'text',
        )

    @staticmethod
    def create_ingredients(ingredients, recipe):
        for ingredient in ingredients:
            amount = ingredient['amount']
            if RecipesIngredientList.objects.filter(
                recipe=recipe, ingredient=ingredient['id']
            ).exists():
                amount += F('amount')
            RecipesIngredientList.objects.update_or_create(
                recipe=recipe,
                ingredient=ingredient['id'],
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


class FollowSerializer(ModelSerializer):
    """Сериализатор подписок"""
    id = IntegerField(source='author.id')
    email = EmailField(source='author.email')
    username = CharField(source='author.username')
    first_name = CharField(source='author.first_name')
    last_name = CharField(source='author.last_name')
    is_subscribed = SerializerMethodField()
    recipes = SerializerMethodField()
    recipes_count = SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = (
            'id',
            'email',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count',
        )

    def get_recipes(self, arg):
        serializer = RecipesForFollowerSerializer(
            Recipes.objects.filter(author=arg.author),
            many=True
        )
        return serializer.data

    @staticmethod
    def get_recipes_count(arg):
        return arg.recipes.count()
