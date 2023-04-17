from django.db import IntegrityError
from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from recipes.models import Ingredient, Recipes, Tags
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import (AllowAny, IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response
from rest_framework.serializers import ValidationError
from users.models import Subscribe, User

from .filters import IngredientFilter
from .pagination import PagePaginationLimit
from .serializers import (CustomUserSerializer, IngredientSerializer,
                          RecipeCreateSerializer, RecipesSerializer,
                          SubscribeSerializer, TagsSerializer)


class UsersViewSet(UserViewSet):
    """
    Вьюсет модели пользователей.
    """
    queryset = User.objects.all()
    serializer_class = CustomUserSerializer
    pagination_class = PagePaginationLimit
    permission_classes = (AllowAny, )

    @action(
        methods=['GET'],
        detail=False,
        permission_classes=(IsAuthenticated,)
    )
    def subscriptions(self, request):
        user = request.user
        queryset = Subscribe.objects.filter(user=user)
        page = self.paginate_queryset(queryset)
        serializer = SubscribeSerializer(
            page, many=True, context={'request': request}
        )
        return self.get_paginated_response(serializer.data)

    @action(
        methods=['POST', 'DELETE'],
        detail=True,
        permission_classes=[IsAuthenticated]
    )
    def subscribe(self, request, id):
        """Подписка на автора."""
        author = get_object_or_404(User, id=id)
        user = get_object_or_404(User, username=request.user.username)
        if request.method == 'POST':
            if user.id == author.id:
                return Response(
                    {'errors': 'Невозможно подписаться на самого себя.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            try:
                serializer = SubscribeSerializer(
                    Subscribe.objects.create(user=user, author=author),
                    context={'request': request},
                    many=True,
                )
                return Response(
                    serializer.data, status=status.HTTP_201_CREATED
                )
            except IntegrityError:
                return Response(
                    {'errors': 'Вы уже подписаны.'}
                )
        if Subscribe.objects.filter(
                user=request.user,
                author=author
        ).exists():
            Subscribe.objects.filter(
                user=request.user,
                author=author
            ).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(
            {'errors': 'Нет подписки'},
            status=status.HTTP_400_BAD_REQUEST,
        )


class TagsViewSet(viewsets.ReadOnlyModelViewSet):
    """Вьюсет тегов."""
    queryset = Tags.objects.all()
    serializer_class = TagsSerializer
    permission_classes = (AllowAny,)


class IngredientsViewSet(mixins.ListModelMixin,
                         mixins.RetrieveModelMixin,
                         viewsets.GenericViewSet):
    """Вьюсет ингредиентов."""
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (AllowAny,)
    filterset_class = IngredientFilter
    search_fields = (r'^name', )


class RecipeViewSet(viewsets.ModelViewSet):
    """Вьюсет рецептов."""
    queryset = Recipes.objects.all()
    permission_classes = (IsAuthenticatedOrReadOnly, )
    filter_backends = (IngredientFilter, )
    pagination_class = PagePaginationLimit

    def get_serializer_class(self):
        """Функция выбора сериализатора рецепта."""
        if self.request.method == 'GET':
            return RecipesSerializer
        return RecipeCreateSerializer

    def add_or_delete(self, field):
        """Функция добавления/удаления для поля field."""
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
        """Функция избранного."""
        return self.add_or_delete(
            request.user.favorite
        )

    @action(
        detail=True,
        methods=['POST', 'DELETE'],
        permission_classes=[IsAuthenticated],
    )
    def shopping_cart(self, request, pk=None):
        """Функция корзины."""
        return self.add_or_delete(
            request.user.shopping_cart
        )

    @action(
        methods=['GET'],
        detail=False,
        permission_classes=[IsAuthenticated],
    )
    def download_shopping_cart(self, request):
        """Функция загрузки документа из корзины."""
        pass
