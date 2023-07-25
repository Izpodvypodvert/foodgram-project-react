from django.contrib.auth.models import AbstractUser
from django.db import models

ADMIN = 'admin'
BANNED = 'banned'
USER = 'user'

ROLES_CHOICES = [
    (ADMIN, ADMIN),
    (USER, USER),
    (BANNED, BANNED),
]


class User(AbstractUser):
    email = models.EmailField('Электронная почта',
                              unique=True,
                              max_length=254,
                              error_messages={
                                  'unique': (
                                      'Пользователь с такой почтой уже '
                                      'существует.'),
                              }, )

    role = models.CharField(
        'Роль',
        max_length=9,
        choices=ROLES_CHOICES,
        default='user',
    )

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = 'username',

    def __str__(self):
        return f'{self.username}: {self.email}'


class Subscription(models.Model):
    subscriber = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscribers',
        verbose_name='Подписчик'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='authors',
        verbose_name='Автор'
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        ordering = 'author__username',

    def __str__(self):
        return f'{self.subscriber} подписан на  {self.author}'
