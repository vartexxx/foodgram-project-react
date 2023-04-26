from datetime import datetime

from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from recipes.models import (Favorite, Ingredient, IngredientAmount, Recipe,
                            ShoppingCart, Tag)
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from users.serializers import ShortRecipeSerializer

from .filters import IngredientFilter, RecipesFilter
from .paginations import PagePaginationLimit
from .permissions import IsAuthorOrReadOnly
from .serializers import (IngredientSerializer, ReadRecipeSerializer,
                          RecipeCreateSerializer, TagsSerializer)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagsSerializer
    permission_classes = (AllowAny, )
    pagination_class = None


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter
    pagination_class = None


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    permission_classes = (IsAuthorOrReadOnly, )
    filter_backends = (DjangoFilterBackend, )
    filterset_class = RecipesFilter
    pagination_class = PagePaginationLimit

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return ReadRecipeSerializer
        return RecipeCreateSerializer

    @action(
        detail=True,
        methods=('POST', 'DELETE',),
        permission_classes=(IsAuthenticated, )
    )
    def favorite(self, request, pk=None):
        recipe = get_object_or_404(Recipe, id=pk)
        if request.method == 'POST':
            return self.add_obj(Favorite, recipe, request.user)
        return self.delete_obj(Favorite, recipe, request.user)

    @action(detail=True,
            methods=('POST', 'DELETE'),
            permission_classes=(IsAuthenticated,)
            )
    def shopping_cart(self, request, pk=None):
        recipe = get_object_or_404(Recipe, id=pk)
        if request.method == 'POST':
            return self.add_obj(ShoppingCart, recipe, request.user)
        return self.delete_obj(ShoppingCart, recipe, request.user)

    def add_obj(self, model, recipe, user):
        if model.objects.filter(user=user, recipe=recipe).exists():
            return Response(status=status.HTTP_400_BAD_REQUEST)
        model.objects.create(user=user, recipe=recipe)
        serializer = ShortRecipeSerializer(recipe)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete_obj(self, model, recipe, user):
        obj = model.objects.filter(user=user, recipe=recipe)
        if obj.exists():
            obj.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_400_BAD_REQUEST)

    @action(
        detail=False,
        permission_classes=[IsAuthenticated],
    )
    def download_shopping_cart(self, request):
        shopping_cart = ShoppingCart.objects.filter(
            user=self.request.user
        )
        cart_list = IngredientAmount.objects.filter(
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
                f'{ingredient.name}, {amount}, {ingredient.measurement_unit}\n'
            )
        response = HttpResponse(list_text, content_type="text/plain")
        response['Content-Disposition'] = (
            'attachment; filename=shopping_list.txt'
        )
        return response
