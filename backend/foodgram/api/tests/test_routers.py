from django.urls import reverse
from rest_framework.test import APITestCase

ID = 1

urls = [
    ['/api/tags/', 'tags-list', []],
    [f'/api/tags/{ID}/', 'tags-detail', [ID]],
    ['/api/recipes/', 'recipes-list', []],
    [f'/api/recipes/{ID}/', 'recipes-detail', [ID]],
    ['/api/ingredients/', 'ingredients-list', []],
    [f'/api/ingredients/{ID}/', 'ingredients-detail', [ID]],
    ['/api/users/', 'users-list', []],
    ['/api/users/me/', 'users-me', []],
    ['/api/users/subscriptions/', 'users-subscriptions', []],
    [f'/api/users/{ID}/', 'users-detail', [ID]],
    ['/api/auth/token/login/', 'login', []],
    ['/api/auth/token/logout/', 'logout', []],
]


class RoutesTest(APITestCase):

    def test_urls_routes(self):
        """Проверка ожидаемых маршрутов URL"""
        for url, route, args in urls:
            self.assertEqual(
                url,
                reverse((f'api:{route}'), args=args)
            )
