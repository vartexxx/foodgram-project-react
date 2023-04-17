from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase
from users.models import User

ID = 1
TAGS = reverse('api:tags-list')
INGREDIENTS = reverse('api:ingredients-list')
RECIPES = reverse('api:recipes-list')

OK = status.HTTP_200_OK


class UrlsTestCase(APITestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.header_info = {'content-type': 'application/json'}
        cls.user = User.objects.create(
            username='vlad',
            first_name='vladislav',
            last_name='burlaka',
            password='1111111',
            email='vlad@yandex.ru'
        )

    def setUp(self) -> None:
        self.guest = APIClient()
        self.authorized = APIClient()
        self.authorized.force_login(self.user)

    def test_urls_correct_status_code(self):
        """
        Проверка корректности доступа к URL различного уровня,
        без внесения изменений в базу данных.
        """
        urls = [
            [RECIPES, self.guest, OK],
            [RECIPES, self.authorized, OK],
            [TAGS, self.guest, OK],
            [TAGS, self.authorized, OK],
            [INGREDIENTS, self.guest, OK],
            [INGREDIENTS, self.authorized, OK],
        ]
        for url, client, info in urls:
            with self.subTest(url=url, client=client):
                self.assertEqual(client.get(url).status_code, info)
