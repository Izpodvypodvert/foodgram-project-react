from fpdf import FPDF

from django.db.models import Sum
from django.shortcuts import HttpResponse

from rest_framework import status
from rest_framework.response import Response

from foodgram.models import IngredientRecipe


def create_recipe_ingredients(recipe, ingredients):
    """Создаёт объект IngredientRecipe
    связывающий объекты Recipe и Ingredient."""
    recipe_ingredients = []

    for ingredient, amount in ingredients.values():
        recipe_ingredients.append(IngredientRecipe(recipe=recipe,
                                                   ingredient=ingredient,
                                                   amount=amount))
    IngredientRecipe.objects.bulk_create(recipe_ingredients)


def add_page_to_pdf(pdf):
    """Добавляет страницу в pdf файл."""
    pdf.add_page()
    pdf.image('/app/api/pdf/background.jpg', x=0, y=0, w=210, h=297)
    return pdf


def set_pdf_text(pdf, new_size=15, text='', r=0, g=0, b=0, border=False, w=190,
                 h=20):
    """Настраивает отображение текста в pdf файле."""
    pdf.set_font('NotoSerif', size=new_size)
    pdf.set_text_color(r, g, b)
    pdf.cell(w, h, txt=text,
             ln=1, align='C', border=border)
    pdf.set_text_color(0, 0, 0)
    pdf.set_font('NotoSerif', size=15)
    return pdf


def generate_pdf_file(ingredients):
    """Генерирует pdf файл."""
    pdf = FPDF()
    pdf = add_page_to_pdf(pdf)
    font = 'NotoSerif-Italic-VariableFont_wdth,wght.ttf'
    pdf.add_font('NotoSerif', style='',
                 fname=f'/app/api/pdf/{font}',
                 uni=True)

    pdf = set_pdf_text(
        pdf, 25, text='СПИСОК ПОКУПОК', r=255, g=24, b=89)
    pdf = set_pdf_text(
        pdf, 15, text='Составлен продуктовым помощником foodgram.com', r=255,
        g=24, b=89)
    recipe_images = {}
    pdf.cell(190, 40, txt='', ln=1, align='C')
    ingredient_counter = 0
    for ingredient in ingredients:
        if ingredient_counter == 14:
            pdf = add_page_to_pdf(pdf)
            pdf.cell(190, 80, txt='', ln=1, align='C')
            ingredient_counter = 0
        recipe_name = ingredient['recipe__name']
        image = ingredient['recipe__image']
        recipe_id = ingredient['recipe__id']

        if image not in recipe_images.values():
            recipe_images[recipe_name] = [image, recipe_id]

        name = ingredient['ingredient__name']
        unit = ingredient['ingredient__measurement_unit']
        amount = ingredient['ingredient_amount']
        pdf.cell(190, 10, txt=f'{name} - {amount}, {unit}',
                 ln=1, align='C')
        ingredient_counter += 1
    pdf = add_page_to_pdf(pdf)
    pdf = set_pdf_text(
        pdf, 22, text='Из этих ингредиентов можно приготовить:', r=255, g=24,
        b=89)
    pdf.cell(190, 40, txt='', ln=1, align='C')
    recipes_counter = 0
    for recipe_name, data in recipe_images.items():

        if recipes_counter == 2:
            pdf = add_page_to_pdf(pdf)
            pdf.cell(190, 60, txt='', ln=1, align='C')
            recipes_counter = 0
        image, recipe_id = data
        recipe_link = f'http://localhost/recipes/{recipe_id}'

        pdf = set_pdf_text(
            pdf, 22, text=recipe_name, r=42, g=71, b=203)

        pdf.cell(190, 10, txt='Посмотреть рецепт на сайте -->',
                 ln=1, align='C', link=recipe_link)
        pdf.image(f'/app/media/{image}', w=50, h=50, x=85,
                  type='', link=recipe_link)
        recipes_counter += 1

    pdf.output(name='Список покупок.pdf')
    pdf = pdf.output(dest='S').encode('latin-1')
    return pdf


def create_shoping_list(user):
    """Формирует список ингредиентов для покупки."""
    ingredients = IngredientRecipe.objects.filter(
        recipe__cart_recipes__user=user
    ).values(
        'ingredient__name', 'ingredient__measurement_unit',
        'recipe__image', 'recipe__name', 'recipe__id'
    ).annotate(ingredient_amount=Sum('amount'))
    pdf = generate_pdf_file(ingredients)
    response = HttpResponse(pdf,
                            content_type='application/pdf')
    response[
        'Content-Disposition'] = 'attachment; filename="Список покупок.pdf"'
    return response


def add_recipe(request, recipe, serializer_name):
    """Добавляет рецепт в список покупок или избранное."""
    serializer = serializer_name(
        data={'recipe': recipe.id,
              'user': request.user.id},
        context={'request': request})
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response(serializer.data, status=status.HTTP_201_CREATED)


def delete_recipe(request, model, recipe):
    """Удаляет рецепт из списка покупок или из избранного."""
    if not model.objects.filter(recipe=recipe, user=request.user).exists():
        return Response({'errors': 'Рецепт отсутствует.'},
                        status=status.HTTP_400_BAD_REQUEST)
    model.objects.filter(recipe=recipe, user=request.user).delete()
    return Response(status=status.HTTP_204_NO_CONTENT)
