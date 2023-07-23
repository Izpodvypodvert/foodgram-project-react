from django.core.exceptions import ValidationError
from foodgram.models import Ingredient, Tag


def password_validator(request):
    new_password = request.data.get('new_password')
    current_password = request.data.get('current_password')
    user = request.user

    if not user.check_password(current_password):
        raise ValidationError('Неправильный пароль.')
    if new_password == current_password:
        raise ValidationError('Новый пароль должен отличаться от текущего.')

    return new_password


def ingredients_validator(ingredients):
    """Проверяет корректность указанных ингредиентов."""
    ingredient_ids = []
    ingredient_amount = []

    if not ingredients:
        raise ValidationError('Не указаны ингредиенты')

    for ingredient in ingredients:
        try:
            amount = int(ingredient['amount'])
        except ValueError:
            raise ValidationError(
                'Количество ингредиента - должно быть числовым значением!')
        except KeyError:
            raise ValidationError('Некорректный ингредиент')

        if amount <= 1:
            raise ValidationError('Неправильное количество ингредиента')

        ingredient_ids.append(ingredient['id'])
        ingredient_amount.append(amount)

    ings_in_db = Ingredient.objects.filter(
        pk__in=ingredient_ids)

    if not ings_in_db.exists():
        raise ValidationError('Некорректные ингредиенты')

    valid_ingredients = {}
    for id, ing, amount in zip(ingredient_ids, ings_in_db, ingredient_amount):
        valid_ingredients[id] = (ing, amount)

    return valid_ingredients


def tags_validator(tag_ids):
    """Проверяет корректность указанных тегов."""
    if not tag_ids:
        raise ValidationError('Не указаны теги')
    valid_tags = Tag.objects.filter(id__in=tag_ids)
    if len(tag_ids) != len(valid_tags):
        raise ValidationError('Указан некорректный тег')
    return valid_tags
