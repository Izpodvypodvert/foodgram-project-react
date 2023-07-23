from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend

from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response

from api.filters import IngredientFilter, RecipeFilter
from api.paginators import LimitPagination
from api.permissions import (IsAdminOrReadOnly, IsAuthorOrAdminOrReadOnly,
                             IsUserNotBanned)
from api.serializers import (CartSerializer, FavoriteSerializer,
                             IngredientSerializer, RecipeSerializer,
                             SubscribeSerializer, TagSerializer,
                             UserSerializer, UserSubscribeSerializer)
from api.validators import password_validator
from api.utils import (add_recipe, create_shoping_list,
                       delete_recipe)
from foodgram.models import Cart, FavoriteRecipe, Ingredient, Recipe, Tag
from users.models import Subscription, User


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (IsAdminOrReadOnly, IsUserNotBanned)


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter
    permission_classes = (IsAdminOrReadOnly, IsUserNotBanned)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAdminOrReadOnly, IsUserNotBanned)
    pagination_class = LimitPagination

    @action(detail=False, methods=['get'],
            permission_classes=(IsAuthenticated, IsUserNotBanned))
    def me(self, request):
        """Получить текущего пользователя."""
        serializer = UserSerializer(request.user)
        return Response(serializer.data,
                        status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'],
            permission_classes=(IsAuthenticated, IsUserNotBanned))
    def set_password(self, request):
        """Изменение пароля текущего пользователя."""
        new_password = password_validator(request)
        new_data = {'password': new_password}
        serializer = UserSerializer(
            request.user, data=new_data, partial=True)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
        return Response({'detail': 'Пароль успешно изменен!'},
                        status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, permission_classes=(IsAuthenticated, IsUserNotBanned))
    def subscribe(self, request, pk):
        """Подписка на автора рецепта."""

    @subscribe.mapping.post
    def create_subscribe(self, request, pk):
        """Создает подписку на автора рецепта."""
        author = get_object_or_404(User, id=pk)
        serializer = SubscribeSerializer(
            data={'subscriber': request.user.pk, 'author': author.pk},
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @subscribe.mapping.delete
    def delete_subscribe(self, request, pk):
        """Удаляет подписку на автора рецепта."""
        author = get_object_or_404(User, id=pk)
        if not Subscription.objects.filter(subscriber=request.user,
                                           author=author).exists():
            return Response(
                {'errors': 'Вы не подписаны на этого пользователя'},
                status=status.HTTP_400_BAD_REQUEST
            )
        Subscription.objects.get(subscriber=request.user.id,
                                 author=pk).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(methods=("get",), detail=False,
            permission_classes=(IsAuthenticated, IsUserNotBanned))
    def subscriptions(self, request):
        """Список подписок пользоваетеля."""
        pages = self.paginate_queryset(
            User.objects.filter(authors__subscriber=self.request.user)
        )
        serializer = UserSubscribeSerializer(pages, many=True)
        return self.get_paginated_response(serializer.data)

    def get_permissions(self):
        if self.request.method == 'POST':
            return AllowAny(),
        return super().get_permissions()


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.select_related("author")
    serializer_class = RecipeSerializer
    permission_classes = (IsAuthorOrAdminOrReadOnly, IsUserNotBanned)
    pagination_class = LimitPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    @action(detail=True, permission_classes=(IsAuthenticated, IsUserNotBanned))
    def favorite(self, request, pk):
        """Избранные рецепты."""

    @favorite.mapping.post
    def recipe_to_favorites(self, request, pk):
        """Добавляет рецепт в избранное."""
        recipe = get_object_or_404(Recipe, id=pk)
        return add_recipe(request, recipe, FavoriteSerializer)

    @favorite.mapping.delete
    def remove_recipe_from_favorites(self, request, pk):
        """Удаляет рецепт из избранного."""
        recipe = get_object_or_404(Recipe, id=pk)
        return delete_recipe(request, FavoriteRecipe, recipe)

    @action(detail=True, permission_classes=(IsAuthenticated, IsUserNotBanned))
    def shopping_cart(self, request, pk):
        """Рецепты в списке покупок."""

    @shopping_cart.mapping.post
    def recipe_to_cart(self, request, pk):
        """Добавляет рецепт в список покупок."""
        recipe = get_object_or_404(Recipe, id=pk)
        return add_recipe(request, recipe, CartSerializer)

    @shopping_cart.mapping.delete
    def remove_recipe_from_cart(self, request, pk):
        """Удаляет рецепт из списка покупок."""
        recipe = get_object_or_404(Recipe, id=pk)
        return delete_recipe(request, Cart, recipe)

    @action(methods=("get",), detail=False,
            permission_classes=(IsAuthenticated, IsUserNotBanned))
    def download_shopping_cart(self, request):
        """Отправка файла со списком покупок."""
        return create_shoping_list(request.user)
