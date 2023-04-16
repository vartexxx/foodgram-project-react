from django.contrib.auth import get_user_model
from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from recipes.models import Ingredient, Recipes, RecipesIngredientList, Tags
from rest_framework import generics, mixins, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.filters import BaseFilterBackend
from rest_framework.permissions import (AllowAny, IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response
from rest_framework.serializers import ValidationError
from users.models import Follow, User

from .filters import IngredientFilter
from .pagination import PagePaginationLimit
from .serializers import (CustomCreateUserSerializer, CustomUserSerializer,
                          FollowSerializer, IngredientSerializer,
                          RecipeCreateSerializer, RecipesSerializer,
                          TagsSerializer)


class UsersViewSet(UserViewSet):
    """
    Вьюсет модели пользователей.
    """
    queryset = User.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = (AllowAny,)

    @action(
        methods=['POST', 'DELETE'],
        detail=True,
    )
    def subscribe(self, request, id):
        author = get_object_or_404(User, id=id)
        user = get_object_or_404(User, username=request.user.username)
        if request.method == 'POST':
            if user.id == author.id:
                raise ValidationError('Невозможно подписаться на самого себя')
            serializer = FollowSerializer(
                Follow.objects.create(user=user, author=author),
                context={'request': request},
                many=True,
            )
            return Response(
                serializer.data, status=status.HTTP_201_CREATED
            )

        if request.method == 'DELETE':
            if Follow.objects.filter(
                    user=request.user, author=author
            ).exists():
                Follow.objects.filter(
                    user=request.user, author=author
                ).delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response(
                {'errors': 'Нет подписки'},
                status=status.HTTP_400_BAD_REQUEST,
            )


class FollowListViewSet(viewsets.ReadOnlyModelViewSet):
    """Список подписок пользователя"""
    queryset = User.objects.all()
    serializer_class = FollowSerializer
    pagination_class = PagePaginationLimit
    filter_backends = (BaseFilterBackend, )
    permission_classes = (IsAuthenticated, )
    search_fields = ('follow_list')

    def get_queryset(self):
        return User.objects.filter(
            User.objects.filter(follow_list=self.request.user)
        )


class TagsViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tags.objects.all()
    serializer_class = TagsSerializer
    permission_classes = (AllowAny,)


class IngredientsViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (AllowAny,)
    filter_backends = (IngredientFilter, )
    search_fields = ('name', )


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipes.objects.all()
    permission_classes = (IsAuthenticatedOrReadOnly, )
    filter_backends = (IngredientFilter, )
    pagination_class = PagePaginationLimit

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return RecipesSerializer
        return RecipeCreateSerializer

    def add_or_delete(self, field):
        recipe = self.get_object()
        if self.request.method == 'DELETE':
            field.get(recipe_id=recipe.id).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        if field.filter(recipe=recipe).exists():
            raise ValidationError('Рецепт уже есть')
        field.create(recipe=recipe)
        return Response(
            RecipeCreateSerializer(instance=recipe).data,
            status=status.HTTP_201_CREATED
        )

    @action(
        detail=True,
        methods=['POST', 'DELETE'],
        permission_classes=[IsAuthenticated],
    )
    def favorite(self, request, pk=None):
        return self.add_or_delete(
            request.user.favorite
        )

    @action(
        detail=True,
        methods=['POST', 'DELETE'],
        permission_classes=[IsAuthenticated],
    )
    def shopping_cart(self, request, pk=None):
        return self.add_or_delete(
            request.user.shopping_cart
        )

    @action(
        methods=['GET'],
        detail=False,
        permission_classes=[IsAuthenticated],
    )
    def download_shopping_cart(self, request):
        user = request.user
        file_name = 'shopping_list.txt'
        if not user.shopping_cart.exists():
            return Response(status=status.HTTP_400_BAD_REQUEST)
        ingredients = RecipesIngredientList.objects.filter(
            unique_recipes_list=user
        ).values(
            'ingredients__name',
            'ingredients__measurement_unit',
        ).annotate(
            value=Sum('amount')
        ).order_by('ingredients__name')
        response = HttpResponse(
            content_type='text/plain',
            charset='utf-8',
        )
        response['Content-Disposition'] = f'attachment; filename={file_name}'
        response.write('Список продуктов к покупке:\n')
        for ingredient in ingredients:
            response.write(
                f'- {ingredient["ingredients__name"]} '
                f'- {ingredient["value"]} '
                f'{ingredient["ingredients__measurement_unit"]}\n'
            )
        return response
