from django_filters.rest_framework import FilterSet, filters

from foodgram.models import Ingredient, Recipe, Tag


class RecipeFilter(FilterSet):
    """Фильтр для рецептов."""

    name = filters.CharFilter(lookup_expr='icontains')
    is_in_shopping_cart = filters.BooleanFilter(
        method='get_is_in_shopping_cart'
    )
    is_favorited = filters.BooleanFilter(
        method='get_is_favorited'
    )
    tags = filters.ModelMultipleChoiceFilter(
        queryset=Tag.objects.all(),
        field_name='tags__slug',
        to_field_name='slug',
    )

    class Meta:
        model = Recipe
        fields = ('author', 'tags', 'is_favorited',
                  'is_in_shopping_cart', 'name')

    def get_is_favorited(self, queryset, name, value):
        user = self.request.user
        if value and user.is_authenticated:
            return queryset.filter(favorite__user=user)
        return queryset

    def get_is_in_shopping_cart(self, queryset, name, value):
        user = self.request.user
        if value and user.is_authenticated:
            return queryset.filter(cart_recipes__user=user)
        return queryset


class IngredientFilter(FilterSet):
    """Фильтр для ингридиентов."""

    name = filters.CharFilter(lookup_expr='icontains')

    class Meta:
        model = Ingredient
        fields = ('name',)
