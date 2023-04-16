from django.urls import include, path
from djoser.views import TokenCreateView, TokenDestroyView
from rest_framework.routers import DefaultRouter

from .views import (FollowListViewSet, IngredientsViewSet, RecipeViewSet,
                    TagsViewSet, UsersViewSet)

app_name = 'api'

router_v1 = DefaultRouter()
router_v1.register(r'tags', TagsViewSet, basename='tags')
router_v1.register(r'ingredients', IngredientsViewSet, basename='ingredients')
router_v1.register(r'recipes', RecipeViewSet, basename='recipes')
router_v1.register(r'users', UsersViewSet, basename='users')
router_v1.register(
    r'users/subscriptions',
    FollowListViewSet,
    basename='subscriptions',
)

urlpatterns = [
    path('', include(router_v1.urls)),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
    path(
        'auth/token/login/',
        TokenCreateView.as_view(),
        name='login'
    ),
    path(
        'auth/token/logout/',
        TokenDestroyView.as_view(),
        name='logout'
    ),
]
