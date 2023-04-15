from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import IngredientViewSet, TagsViewSet

router_v1 = DefaultRouter()
router_v1.register('tags', TagsViewSet, basename='tags')
router_v1.register('ingredient', IngredientViewSet, basename='ingredient')

urlpatterns = [
    path('', include(router_v1.urls)),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
]
