from rest_framework.test import APITestCase
from users.models import Subscribe, User


class UrlsTestCase(APITestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.user = User.objects.create(
            username='vlad',
            first_name='vladislav',
            last_name='burlaka',
            password='1111111',
            email='vlad@yandex.ru'
        )
        cls.user2 = User.objects.create(
            username='vlad2',
            first_name='vladislav2',
            last_name='burlaka2',
            password='11111112',
            email='vlad2@yandex.ru'
        )
        cls.subscribe = Subscribe.objects.create(
            user=cls.user,
            author=cls.user2
        )

    def test_models_have_correct_object_names(self):
        """Корректно работает метод __str__ моделей User, Subscribe."""
        self.assertEqual(str(self.user), self.user.username)
        self.assertEqual(
            str(self.subscribe),
            f'{self.subscribe.user} подписан на {self.subscribe.author}'
        )

    def test_verbose_name_user(self):
        """Корректно прописаны verbose_name для модели User"""
        field_verboses = {
            'username': 'Логин',
            'first_name': 'Имя',
            'last_name': 'Фамилия',
            'password': 'Пароль',
            'email': 'Емайл',
        }
        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(
                    User._meta.get_field(field).verbose_name,
                    expected_value
                )

    def test_verbose_name_subscribe(self):
        """Корректно прописаны verbose_name для модели Subscribe"""
        field_verboses = {
            'user': 'Подписчик',
            'author': 'Автор контента',
        }
        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(
                    Subscribe._meta.get_field(field).verbose_name,
                    expected_value
                )

    def test_help_text_user(self):
        """Корректно прописаны help_text для User"""
        field_help_texts = {
            'username': 'Введите логин',
            'first_name': 'Введите имя',
            'last_name': 'Введите фамилию',
            'password': 'Введите пароль',
            'email': 'Введите электронную почту',
        }
        for field, expected_value in field_help_texts.items():
            with self.subTest(field=field):
                self.assertEqual(
                    User._meta.get_field(field).help_text,
                    expected_value
                )

    def test_help_text_subscribe(self):
        """Корректно прописаны help_text для Subscribe"""
        field_help_texts = {
            'user': 'Выберите подписчика',
            'author': 'Выберите автора контента',
        }
        for field, expected_value in field_help_texts.items():
            with self.subTest(field=field):
                self.assertEqual(
                    Subscribe._meta.get_field(field).help_text,
                    expected_value
                )
