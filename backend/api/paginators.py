from rest_framework.pagination import PageNumberPagination


class LimitPagination(PageNumberPagination):
    """Пагинатор для вывода запрошенного количества страниц."""

    page_size_query_param = "limit"
    page_size = 6
