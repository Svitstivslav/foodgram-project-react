from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Пользователи."""
    email = models.EmailField(
        verbose_name='Email',
        max_length=200,
        unique=True,
    )
    first_name = models.CharField(
        verbose_name='Имя',
        max_length=150)
    last_name = models.CharField(
        verbose_name='Фамилия',
        max_length=150,
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('id', )

    def __str__(self):
        return self.email
