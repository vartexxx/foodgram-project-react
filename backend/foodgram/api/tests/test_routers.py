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
]


class RoutesTest(APITestCase):

    def test_urls_routes(self):
        """Проверка ожидаемых маршрутов URL"""
        for url, route, args in urls:
            self.assertEqual(
                url,
                reverse((f'api:{route}'), args=args)
            )
