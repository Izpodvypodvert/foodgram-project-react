from django.db import models

from users.models import User


class Ingredient(models.Model):
    name = models.CharField(
        'Название ингредиента',
        help_text='Введите название ингредиента',
        max_length=64)
    measurement_unit = models.CharField(
        'Единица измерения',
        help_text='Введите единицу измерения',
        max_length=20)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Ингредиент"
        verbose_name_plural = "Ингредиенты"


class Tag(models.Model):
    name = models.CharField(
        'Тэг',
        help_text='Введите название тэга',
        max_length=64,
        unique=True)
    color = models.CharField(
        'Цвет тэга',
        max_length=7,
        unique=True)
    slug = models.SlugField(
        'Слаг тэга',
        unique=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Тэг"
        verbose_name_plural = "Тэги"


class Recipe(models.Model):
    name = models.CharField(
        'Название рецепта',
        help_text='Введите название рецепта',
        max_length=64)
    text = models.TextField(
        'Описание рецепта',
        help_text='Введите описание рецепта')
    pub_date = models.DateTimeField(
        'Дата публикации',
        auto_now_add=True
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор рецепта'
    )
    image = models.ImageField(
        upload_to='recipes/images/',
        null=True,
        default=None
    )
    ingredients = models.ManyToManyField(
        Ingredient, through='IngredientRecipe')
    tags = models.ManyToManyField(
        Tag,
        verbose_name='Тэги',
        related_name="recipes",
    )
    cooking_time = models.PositiveIntegerField()

    def __str__(self):
        return self.name[:15]

    class Meta:
        ordering = ['-pub_date']
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'


class IngredientRecipe(models.Model):
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name="ingredient"
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name="recipe"
    )
    amount = models.PositiveIntegerField(
        verbose_name="Количество",
        default=1
    )

    def __str__(self):
        return f'{self.ingredient} {self.recipe}'

    class Meta:
        verbose_name = "Интгридиент в рецепте"
        verbose_name_plural = "Интгридиенты в рецепте"


class FavoriteRecipe(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favorite_recipes',
        verbose_name='Подписчик'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favorite',
        verbose_name='Рецепт'
    )

    class Meta:
        verbose_name = "Избранный рецепт"
        verbose_name_plural = "Избранные рецепты"
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_favorite_user_recipe'
            )
        ]


class Cart(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='cart',
        verbose_name='Владелец корзины'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='Рецепты в списке покупок',
        related_name='cart_recipes'
    )

    class Meta:
        verbose_name = "Cписок покупок"
        verbose_name_plural = "Списки покупок"
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_cart_user_recipe'
            )
        ]
