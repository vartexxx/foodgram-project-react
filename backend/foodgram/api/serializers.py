from djoser.serializers import UserCreateSerializer, UserSerializer
from recipes.models import (Favorite, Ingredient, Recipes,
                            RecipesIngredientList, ShoppingCart, Tags)
from rest_framework.generics import UpdateAPIView
from rest_framework.serializers import (CharField, ModelSerializer, Serializer,
                                        SerializerMethodField, ValidationError)
from users.models import Follow, User


class TagsSerializer(ModelSerializer):

    class Meta:
        model = Tags
        fields = '__all__'


class IngredientSerializer(ModelSerializer):

    class Meta:
        model = Ingredient
        fields = '__all__'


class CustomUserSerializer(UserSerializer):
    is_subscribe = SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'username',
            'first_name',
            'last_name',
            'email',
            'is_subscribe',
        )

    def get_subscribe(self, args):
        user = self.context.get('request').user
        if user.is_authenticated:
            return Follow.objects.filter(user=user, following=args).exists()
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
