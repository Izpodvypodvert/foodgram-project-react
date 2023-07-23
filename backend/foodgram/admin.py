from django.contrib import admin
from django.utils.html import format_html

from foodgram.models import (Cart, FavoriteRecipe, Ingredient,
                             IngredientRecipe, Recipe, Tag)


class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'color')
    search_fields = ('name', 'color')


class FavoriteRecipeAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe', 'recipe_image')
    search_fields = ('user__username', 'recipe__name')

    def recipe_image(self, obj):
        image_url = obj.recipe.image.url
        image_tag = f"<img src={image_url} width='120' hieght='60' />"
        return format_html(image_tag)


class CartAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe')
    search_fields = ('user__username', 'recipe__name')


class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit',)
    list_filter = ('name',)
    search_fields = ('name',)


class IngredientRecipeInline(admin.TabularInline):
    model = IngredientRecipe
    extra = 3


class RecipeAdmin(admin.ModelAdmin):
    inlines = (IngredientRecipeInline,)
    list_display = ('name', 'author', 'in_favorite_recipes', 'recipe_image')
    search_fields = ('name', 'author__username', 'tags__name')
    list_filter = ('name', 'author__username', 'tags__name')
    fields = (
        ('name', 'author'),
        ('tags', 'cooking_time'),
        ('text',),
        ('image',),
    )

    def in_favorite_recipes(self, obj):
        return obj.favorite.count()

    def recipe_image(self, obj):
        image_tag = f"<img src={obj.image.url} width='120' hieght='60' />"
        return format_html(image_tag)

    recipe_image.short_description = 'Изображение'
    in_favorite_recipes.short_description = 'В избранном'


admin.site.register(Tag, TagAdmin)
admin.site.register(FavoriteRecipe, FavoriteRecipeAdmin)
admin.site.register(Cart, CartAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Recipe, RecipeAdmin)
