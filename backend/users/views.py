from api.paginations import PagePaginationLimit
from django.contrib.auth import get_user_model
from djoser.views import UserViewSet
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.serializers import ValidationError

from .models import Subscribe
from .serializers import SubscribeSerializer

User = get_user_model()


class CustomUserViewSet(UserViewSet):
    pagination_class = PagePaginationLimit

    @action(
        detail=False,
        methods=['GET'],
    )
    def subscriptions(self, request):
        queryset = request.user.subscribers.all()
        pages = self.paginate_queryset(queryset)
        serializer = SubscribeSerializer(
            pages,
            many=True,
            context={'request': request}
        )
        return self.get_paginated_response(serializer.data)

    @action(
        detail=True,
        methods=('POST', 'DELETE'),
        permission_classes=(IsAuthenticated, )
    )
    def subscribe(self, request, id=None):
        user = self.request.user
        author = get_object_or_404(User, id=id)
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
            queryset = Subscribe.objects.create(
                user=user,
                author=author
            )
            serializer = SubscribeSerializer(
                queryset,
                context={'request': request}
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        if user == author:
            raise ValidationError(
                'Подписка не была оформлена, либо уже удалена.'
            )
        subscribe = Subscribe.objects.filter(
            user=user,
            author=author
        )
        if subscribe.exists():
            subscribe.delete()
            return Response(
                {'successfully': 'Вы успешно отписались.'},
                status=status.HTTP_204_NO_CONTENT
            )
        return Response({'errors': 'Вы уже отписаны.'},
                        status=status.HTTP_400_BAD_REQUEST)
