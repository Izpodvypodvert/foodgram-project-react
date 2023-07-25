import base64

from django.contrib.auth.hashers import make_password
from django.core.files.base import ContentFile

from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from api.utils import create_recipe_ingredients, ReadOnlyFieldsMixin
from api.validators import ingredients_validator, tags_validator
from foodgram.models import (Cart, FavoriteRecipe, Ingredient,
                             Recipe, Tag, IngredientRecipe)
from users.models import Subscription, User


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор для модели User."""

    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('id', 'email', 'username', 'password',
                  'first_name', 'last_name', 'is_subscribed')
        read_only_fields = ('is_subscribed',)

    def validate_password(self, value):
        """Преобразует обычный текстовый пароль в хэш,
          который подходит для хранения в базе данных"""

        return make_password(value)

    def create(self, validated_data):
        role = validated_data.get('role', 'user')
        users = {'user': {'is_staff': 0, 'is_superuser': 0},
                 'admin': {'is_staff': 1, 'is_superuser': 0},
                 }
        return User.objects.create(is_staff=users[role]['is_staff'],
                                   is_superuser=users[role]['is_superuser'],
                                   **validated_data)

    def get_is_subscribed(self, author_recipe) -> bool:
        """Определяет подписан ли пользователь на автора рецепта."""

        request = self.context.get('request')
        if not request:
            return False
        return (request.user.is_authenticated
                and Subscription.objects.filter(
                    subscriber=request.user, author=author_recipe
                ).exists())


class TagSerializer(ReadOnlyFieldsMixin, serializers.ModelSerializer):
    """Сериализатор для модели Tag."""

    class Meta:
        model = Tag
        fields = '__all__'


class ShortRecipeSerializer(ReadOnlyFieldsMixin, serializers.ModelSerializer):
    """Сериализатор для модели Recipe
    c укороченным набор полей"""

    class Meta:
        model = Recipe
        fields = 'id', 'name', 'image', 'cooking_time'


class UserSubscribeSerializer(ReadOnlyFieldsMixin, UserSerializer):
    """Сериализатор для вывода авторов на которых подписан  пользователь."""

    recipes = ShortRecipeSerializer(many=True, read_only=True)
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'id',
            'email',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count',
        )

    def get_recipes_count(self, author_recipe) -> int:
        """Отображает общее количество рецептов у каждого автора."""

        return author_recipe.recipes.count()


class IngredientSerializer(ReadOnlyFieldsMixin, serializers.ModelSerializer):
    """Сериализатор для ингредиентов."""

    class Meta:
        model = Ingredient
        fields = '__all__'


class Base64ImageField(serializers.ImageField):
    """Декодирует изображение из base64."""

    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]

            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)

        return super().to_internal_value(data)


class IngredientInRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор ингредиентов для работы с рецептами."""

    id = serializers.IntegerField(source='ingredient.id')
    name = serializers.CharField(source='ingredient.name')
    measurement_unit = serializers.CharField(
        source='ingredient.measurement_unit')

    class Meta:
        model = IngredientRecipe
        fields = ('id', 'name', 'measurement_unit', 'amount')
        read_only_fields = ('id', 'name', 'measurement_unit')


class RecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для рецептов."""

    tags = TagSerializer(many=True, read_only=True)
    author = UserSerializer(read_only=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    image = Base64ImageField(required=False)
    ingredients = IngredientInRecipeSerializer(many=True, read_only=True,
                                               source='recipe')

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time',
        )
        read_only_fields = (
            'is_favorite',
            'is_shopping_cart',
        )

    def get_is_in_shopping_cart(self, recipe):
        """Проверяет находится ли рецепт в списке  покупок."""

        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return request.user.cart.filter(recipe=recipe).exists()
        return False

    def get_is_favorited(self, recipe):
        """Проверяет находится ли рецепт в избранном."""

        request = self.context.get('request')
        if (request and hasattr(request, 'user')
                and request.user.is_authenticated):
            return request.user.favorite_recipes.filter(recipe=recipe).exists()
        return False

    def validate(self, data):
        """Проверяет теги, ингредиенты и нормализует данные."""

        author = self.context.get('request').user
        tag_ids = self.initial_data.get('tags')
        ingredients = self.initial_data.get('ingredients')
        tags = tags_validator(tag_ids)
        ingredients = ingredients_validator(ingredients)
        data.update({'author': author,
                     'ingredients': ingredients, 'tags': tags})
        return data

    def create(self, validated_data):
        """Создаёт рецепт."""

        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        create_recipe_ingredients(recipe, ingredients)
        recipe.tags.set(tags)
        return recipe

    def update(self, recipe, validated_data):
        """Обновляет рецепт."""

        tags = validated_data.pop('tags')
        recipe.tags.clear()
        recipe.tags.set(tags)
        ingredients = validated_data.pop('ingredients')
        recipe.ingredients.clear()
        create_recipe_ingredients(recipe, ingredients)
        super().update(recipe, validated_data)
        recipe.save()
        return recipe


class FavoriteSerializer(serializers.ModelSerializer):
    """Сериализатор для работы с избранными рецептами."""

    class Meta:
        model = FavoriteRecipe
        fields = '__all__'
        validators = [
            UniqueTogetherValidator(queryset=FavoriteRecipe.objects.all(),
                                    fields=('user', 'recipe'),
                                    message='Рецепт уже добавлен в избранное')
        ]

    def to_representation(self, favorite_recipe):
        request = self.context.get('request')
        serializer = ShortRecipeSerializer(
            favorite_recipe.recipe,
            context={'request': request})
        return serializer.data


class CartSerializer(serializers.ModelSerializer):
    """Сериализатор для работы со списком покупок."""

    class Meta:
        model = Cart
        fields = '__all__'
        validators = [
            UniqueTogetherValidator(
                queryset=Cart.objects.all(),
                fields=('user', 'recipe'),
                message='Рецепт уже добавлен в список покупок')
        ]

    def to_representation(self, cart):
        request = self.context.get('request')
        serializer = ShortRecipeSerializer(cart.recipe,
                                           context={'request': request})
        return serializer.data


class SubscribeSerializer(serializers.ModelSerializer):
    """Сериализатор для подписки или отписки от авторов рецептов."""

    class Meta:
        model = Subscription
        fields = '__all__'
        validators = [
            UniqueTogetherValidator(
                queryset=Subscription.objects.all(),
                fields=('subscriber', 'author'),
                message='Вы уже подписаны на этого автора'
            )
        ]

    def validate(self, data):
        request = self.context.get('request')
        if request.user == data.get('author'):
            raise serializers.ValidationError(
                'Нельзя подписаться на самого себя!')
        return data

    def to_representation(self, subscription):
        request = self.context.get('request')
        serializer = UserSubscribeSerializer(
            subscription.author,
            context={'request': request})
        return serializer.data
