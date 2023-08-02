# сайт Foodgram, «Продуктовый помощник».

### Автор проекта: **Александр Каштанов.**

### https://foodgram.freedynamicdns.org/

### Логин администратора:

`admin2023`

### Пароль администратора:

`admin2023`

## Онлайн-сервис и API для него. На этом сервисе пользователи могут публиковать рецепты, подписываться на публикации других пользователей, добавлять понравившиеся рецепты в список «Избранное», а перед походом в магазин скачивать сводный список продуктов, необходимых для приготовления одного или нескольких выбранных блюд.

### Добавлена возможность искать необходимые рецепты:

![Скрин](https://github.com/Izpodvypodvert/foodgram-project-react/blob/master/search.png)

### Как запустить проект локально в контейнерах:

Клонировать репозиторий и перейти в директорию infra:

`git@github.com:Izpodvypodvert/foodgram-project-react.git`
`cd foodgram-project-react/infra`

Запустить docker-compose:

```
docker compose up --build

```

Собрать статику:

```
docker compose exec backend python manage.py collectstatic --no-input

```

Скопировать статику для nginx:

```
docker compose exec backend cp -r /app/collected_static/. /app/backend_static/static/
```

Выполнить миграции:

```
docker compose exec backend python manage.py migrate --no-input

```

Создать суперпользователя:

```
docker compose exec backend python manage.py createsuperuser

```

Проект будет работать по ссылке:

```
http://localhost/
```

Документация api проекта:

```
http://localhost/api/docs/
```

Примеры запросов к api:

-   `/api/recipes/` GET-запрос – получение списка всех рецептов.
-   `/api/recipes/` POST-запрос – добавление нового рецепта
    Тело запроса:

```
{
"ingredients": [
    {
    "id": 1123,
    "amount": 10
    }
],
"tags": [
    1,
    2
    ],
"image": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABAgMAAABieywaAAAACVBMVEUAAAD///9fX1/S0ecCAAAACXBIWXMAAA7EAAAOxAGVKw4bAAAACklEQVQImWNoAAAAggCByxOyYQAAAABJRU5ErkJggg==",
"name": "cesar",
"text": "text",
"cooking_time": 25
}
```

-   `/api/recipes/download_shopping_cart/` GET-запрос – cкачать список покупок.
