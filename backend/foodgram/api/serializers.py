from djoser.serializers import UserCreateSerializer, UserSerializer
from recipes.models import (Favorite, Ingredient, Recipes,
                            RecipesIngredientList, ShoppingCart, Tags)
from rest_framework.serializers import ModelSerializer
from users.models import Follow, User


class TagsSerializer(ModelSerializer):

    class Meta:
        model = Tags
        fields = ('__all__')


class IngredientSerializer(ModelSerializer):

    class Meta:
        model = Ingredient
        fields = ('__all__')


class CustomUserSerializer(UserSerializer):

    class Meta:
        model = User
        fields = (
            'username',
            'first_name',
            'last_name',
            'password',
            'email',
        )


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
