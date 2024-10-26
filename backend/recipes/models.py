from django.core import validators
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

from user.models import User


class Ingredient(models.Model):
    """Ингедиенты."""
    name = models.CharField(
        verbose_name='Название ингредиента',
        max_length=200,
    )
    measurement_unit = models.CharField(
        verbose_name='Единица измерения ингредиента',
        max_length=200,
    )

    class Meta:
        ordering = ('name', )
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return f'{self.name}, {self.measurement_unit}.'


class Tag(models.Model):
    """Тэги."""
    name = models.CharField(
        verbose_name='Имя',
        max_length=60,
        unique=True,
    )
    color = models.CharField(
        verbose_name='Цвет',
        max_length=7,
        unique=True,
    )
    slug = models.SlugField(
        verbose_name='Ссылка',
        max_length=100,
        unique=True,
    )

    class Meta:
        verbose_name = 'Тэг'
        verbose_name_plural = 'Тэги'
        ordering = ('-id', )

    def __str__(self):
        return self.name


class Recipe(models.Model):
    """Рецепты."""
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipe',
        verbose_name='Автор',
    )
    name = models.CharField(
        verbose_name='Название рецепта',
        max_length=255,
    )
    image = models.ImageField(
        verbose_name='Изображение рецепта',
        upload_to='static/recipe/',
        blank=True,
        null=True,
    )
    text = models.TextField(
        verbose_name='Описание рецепта'
    )
    cooking_time = models.BigIntegerField(
        verbose_name='Время приготовления рецепта'
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='RecipeIngredient'
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name='Тэги',
        related_name='recipes',
    )
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Время приготовления в минутах',
        validators=[validators.MinValueValidator(
            1, message='Мин. время приготовления 1 минута'
        ), ]
    )
    pub_date = models.DateTimeField(
        'Дата публикации',
        auto_now_add=True,
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ('-pub_date', )

    def __str__(self):
        return f'{self.author.email}, {self.name}'


class RecipeIngredient(models.Model):
    """Связь рецептов с ингредиентами."""
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='recipe'
    )
    ingredient = models.ForeignKey(
        'Ingredient',
        on_delete=models.CASCADE,
        related_name='ingredient'
    )
    amount = models.PositiveSmallIntegerField(
        default=1,
        validators=(
            validators.MinValueValidator(
                1, message='Мин. количество ингридиентов 1'
            ),
        ),
        verbose_name='Количество',
    )

    class Meta:
        verbose_name = 'Количество ингредиента'
        verbose_name_plural = 'Количество ингредиентов'
        ordering = ('-id', )
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'ingredient'],
                name='unique ingredient'
            )
        ]


class Subscribe(models.Model):
    """Подписки."""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='Подписчик',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='Автор',
    )
    created = models.DateTimeField(
        'Дата подписки',
        auto_now_add=True,
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        ordering = ('-id', )
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'author'],
                name='unique_subscription'
            )
        ]

    def __str__(self):
        return f'Пользователь {self.user} -> автор {self.author}'


class FavoriteRecipe(models.Model):
    """Избанные рецепты."""
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        null=True,
        related_name='favorite_recipe',
        verbose_name='Пользователь',
    )
    recipe = models.ManyToManyField(
        Recipe,
        related_name='favorite_recipe',
        verbose_name='Избранный рецепт',
    )

    class Meta:
        verbose_name = 'Избранный рецепт'
        verbose_name_plural = 'Избранные рецепты'

    def __str__(self):
        list_ = [item['name'] for item in self.recipe.values('name')]
        return f'Пользователь {self.user} добавил {list_} в избранные.'

    @receiver(post_save, sender=User)
    def create_favorite_recipe(sender, instance, created, **kwargs):
        if created:
            return FavoriteRecipe.objects.create(user=instance)


class ShoppingCart(models.Model):
    """Избанные рецепты для скачивание."""
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='shopping_cart',
        null=True,
        verbose_name='Пользователь',
    )
    recipe = models.ManyToManyField(
        Recipe,
        related_name='shopping_cart',
        verbose_name='Покупка',
    )

    class Meta:
        verbose_name = 'Покупка'
        verbose_name_plural = 'Покупки'
        ordering = ('-id', )

    def __str__(self):
        list_ = [item['name'] for item in self.recipe.values('name')]
        return f'Пользователь {self.user} добавил {list_} в покупки.'

    @receiver(post_save, sender=User)
    def create_shopping_cart(sender, instance, created, **kwargs):
        if created:
            return ShoppingCart.objects.create(user=instance)
