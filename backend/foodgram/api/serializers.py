from django.shortcuts import get_object_or_404
from djoser.serializers import UserCreateSerializer, UserSerializer
from drf_extra_fields.fields import Base64ImageField
from recipes.models import (Favorite, Ingredient, Recipes,
                            RecipesIngredientList, ShoppingCart, Tags)
from rest_framework.serializers import (CharField, IntegerField,
                                        ModelSerializer,
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
    """Сериализатор для кастомной модели пользователя"""
    is_subscribed = SerializerMethodField()

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

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        if user.is_authenticated:
            return Subscribe.objects.filter(user=user, author=obj).exists()
        return False


class CustomCreateUserSerializer(UserCreateSerializer):

    class Meta:
        model = User
        fields = (
            'username',
            'first_name',
            'last_name',
            'password',
            'email',
        )

    def create(self, validated_data):
        user = User(
            email=validated_data['email'],
            username=validated_data['username'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name']
        )
        user.set_password(validated_data['password'])
        user.save()
        return user


class RecipesSerializer(ModelSerializer):
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
    def get_ingredients(obj):
        return IngredientsInRecipeSerializer(
            RecipesIngredientList.objects.filter(recipe=obj),
            many=True,
        ).data

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

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        return ShoppingCart.objects.filter(
            user=request.user,
            recipe_id=obj.id
        ).exists()


class RecipeCreateSerializer(ModelSerializer):
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
    def create_ingredients(data, recipe):
        for ingredient in data:
            amount = ingredient['amount']
            ingredient = get_object_or_404(Ingredient, pk=ingredient['id'])
            RecipesIngredientList.objects.create(
                recipe=recipe,
                ingredient=ingredient,
                amount=amount
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

    def update(self, obj, validated_data):
        tags = validated_data.pop('tags')
        RecipesIngredientList.objects.filter(
            recipe=obj
        ).delete()
        self.create_ingredients(validated_data.pop('ingredients'), obj)
        obj.tags.set(tags)
        return super().update(obj, validated_data)

    def to_representation(self, instance):
        return RecipesSerializer(
            instance,
            context={'request': self.context.get('request')}
        ).data


class FavoriteSerializer(ModelSerializer):
    user = PrimaryKeyRelatedField(
        queryset=User.objects.all()
    )
    recipes = PrimaryKeyRelatedField(
        queryset=Recipes.objects.all()
    )

    class Meta:
        model = Favorite
        fields = (
            'user',
            'recipes',
        )

    def to_representation(self, obj):
        return RecipesForFollowerSerializer(
            obj.recipe,
            context={
                'request': self.context.get('request')
            }
        ).data


class SubscribeSerializer(CustomUserSerializer):
    recipes = SerializerMethodField(method_name='get_recipes')
    recipes_count = SerializerMethodField(method_name='get_recipes_count')

    class Meta:
        model = User
        fields = (
            'id',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count',
        )

    def get_recipes(self, obj):
        request = self.context.get('request')
        recipes_limit = request.GET.get('recipes_limit')
        recipes = Recipes.objects.filter(author=obj.author)
        if recipes_limit:
            recipes = recipes[:int(recipes_limit)]
        serializer = RecipesForFollowerSerializer(recipes, many=True)
        return serializer.data

    def get_recipes_count(self, obj):
        return Recipes.objects.filter(author=obj.author).count()

    def get_is_subscribed(self, obj):
        return Subscribe.objects.filter(
            user=obj.user,
            author=obj.author
        ).exists()
