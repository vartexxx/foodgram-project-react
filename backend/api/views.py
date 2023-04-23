from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from recipes.models import (Favorite, Ingredient, Recipes,
                            RecipesIngredientList, ShoppingCart, Tags)
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.serializers import ValidationError
from users.models import Subscribe, User

from .filters import IngredientFilter, RecipesFilter
from .pagination import PagePaginationLimit
from .permissions import IsAdminOrReadOnly, IsAuthorOrReadOnly
from .serializers import (CustomUserSerializer, IngredientSerializer,
                          RecipeCreateSerializer, RecipesForFollowerSerializer,
                          RecipesSerializer, SubscribeSerializer,
                          TagsSerializer)


class UsersViewSet(UserViewSet):
    queryset = User.objects.all()
    serializer_class = CustomUserSerializer
    pagination_class = PagePaginationLimit

    @action(
        methods=['GET'],
        detail=False,
        permission_classes=(IsAuthenticated, )
    )
    def subscriptions(self, request):
        user = request.user
        queryset = User.objects.filter(subscribing__user=user)
        page = self.paginate_queryset(queryset)
        serializer = SubscribeSerializer(
            page, many=True, context={'request': request}
        )
        return self.get_paginated_response(serializer.data)

    @action(
        methods=['POST', 'DELETE'],
        detail=True,
        permission_classes=(IsAuthenticated, )
    )
    def subscribe(self, request, id=None):
        user = self.request.user
        author = get_object_or_404(User, pk=id)

        if self.request.method == 'POST':
            if user == author:
                raise ValidationError(
                    'Подписка на самого себя запрещена.'
                )
            if Subscribe.objects.filter(
                user=user,
                author=author
            ).exists():
                raise ValidationError('Подписка уже оформлена.')

            Subscribe.objects.create(user=user, author=author)
            serializer = self.get_serializer(author)

            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if self.request.method == 'DELETE':
            if not Subscribe.objects.filter(
                user=user,
                author=author
            ).exists():
                raise ValidationError(
                    'Подписка не была оформлена, либо уже удалена.'
                )

            subscription = get_object_or_404(
                Subscribe,
                user=user,
                author=author
            )
            subscription.delete()

            return Response(status=status.HTTP_204_NO_CONTENT)

        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    @action(
        methods=['GET'],
        detail=False,
        permission_classes=(IsAuthenticated, )
    )
    def me(self, request):
        return Response(
            self.get_serializer(request.user).data,
            status=status.HTTP_200_OK
        )


class TagsViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tags.objects.all()
    serializer_class = TagsSerializer
    permission_classes = (IsAdminOrReadOnly, )
    pagination_class = None


class IngredientsViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (IsAdminOrReadOnly, )
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter
    pagination_class = None


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipes.objects.all()
    permission_classes = (IsAuthorOrReadOnly | IsAdminOrReadOnly, )
    filter_backends = (DjangoFilterBackend, )
    filterset_class = RecipesFilter
    pagination_class = PagePaginationLimit

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return RecipesSerializer
        return RecipeCreateSerializer

    @action(detail=True, methods=['POST', 'DELETE'],
            permission_classes=(IsAuthenticated, ))
    def favorite(self, request, pk):
        recipe = get_object_or_404(Recipes, pk=pk)
        if self.request.method == 'POST':
            if Favorite.objects.filter(
                user=request.user,
                recipe=recipe
            ).exists():
                return Response(
                    {'errors': 'Рецепт уже в избранно.'},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            Favorite.objects.get_or_create(user=request.user, recipe=recipe)
            data = RecipesForFollowerSerializer(recipe).data
            return Response(data, status=status.HTTP_201_CREATED)
        if self.request.method == 'DELETE':
            if Favorite.objects.filter(
                user=request.user,
                recipe=recipe
            ).exists():
                get_object_or_404(
                    Favorite,
                    user=request.user,
                    recipe=recipe
                ).delete()
                return Response(
                    'Рецепт удален из избранного.',
                    status=status.HTTP_204_NO_CONTENT
                )
            return Response(
                'Данного рецепта нет в избранном.',
                status=status.HTTP_400_BAD_REQUEST
            )
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    @action(
        detail=True,
        methods=['POST', 'DELETE'],
        permission_classes=(IsAuthenticated, )
    )
    def shopping_cart(self, request, pk):
        recipe = get_object_or_404(Recipes, pk=pk)
        if self.request.method == 'POST':
            if ShoppingCart.objects.filter(
                user=request.user,
                recipe=recipe
            ).exists():
                return Response(
                    {'errors': 'Рецепт уже в списке покупок.'},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            ShoppingCart.objects.get_or_create(
                user=request.user,
                recipe=recipe
            )
            data = RecipesForFollowerSerializer(recipe).data
            return Response(data, status=status.HTTP_201_CREATED)
        if self.request.method == 'DELETE':
            if ShoppingCart.objects.filter(
                user=request.user,
                recipe=recipe
            ).exists():
                get_object_or_404(
                    ShoppingCart,
                    user=request.user,
                    recipe=recipe
                ).delete()
                return Response(
                    'Рецепт удален из списка покупок',
                    status=status.HTTP_204_NO_CONTENT
                )
            return Response(
                'Данного рецепта нет в списке покупок',
                status=status.HTTP_400_BAD_REQUEST
            )
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    @action(
        methods=['GET'],
        detail=False,
        permission_classes=(IsAuthenticated, )
    )
    def download_shopping_cart(self, request):
        shopping_cart = ShoppingCart.objects.filter(
            user=self.request.user
        )
        cart_list = RecipesIngredientList.objects.filter(
            recipe__in=[item.recipe.id for item in shopping_cart]
        ).values(
            'ingredient'
        ).annotate(
            amount=Sum('amount')
        )
        list_text = []
        for item in cart_list:
            ingredient = Ingredient.objects.get(pk=item['ingredient'])
            amount = item['amount']
            list_text += (
                f'{ingredient.name}, {amount}, {ingredient.measurement_unit}'
            )
        response = HttpResponse(list_text, content_type="text/plain")
        response['Content-Disposition'] = (
            'attachment; filename=shopping_list.txt'
        )
        return response
