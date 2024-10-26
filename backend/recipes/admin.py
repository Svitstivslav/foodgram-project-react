from django.contrib import admin

from user.models import User

from .models import (FavoriteRecipe, Ingredient, Recipe, RecipeIngredient,
                     ShoppingCart, Subscribe, Tag)

EMPTY_MSG = '-пусто-'


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = (
        'username',
        'email',
        'first_name',
        'last_name',
        'password'
    )
    search_fields = ('username',)
    empty_value_display = EMPTY_MSG


class RecipeIngredientAdmin(admin.StackedInline):
    model = RecipeIngredient
    autocomplete_fields = ('ingredient',)


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'name', 'text',
        'cooking_time',
        'pub_date', 'author',
        'image',
    )
    search_fields = ('author', 'tags')
    list_filter = ('pub_date', 'tags',)
    inlines = (RecipeIngredientAdmin,)
    empty_value_display = EMPTY_MSG


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'name', 'color', 'slug',
    )
    search_fields = ('name', 'slug',)
    empty_value_display = EMPTY_MSG


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'name', 'measurement_unit',
    )
    search_fields = (
        'name', 'measurement_unit',)
    empty_value_display = EMPTY_MSG


@admin.register(Subscribe)
class SubscribeAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'user', 'author', 'created',
    )
    search_fields = (
        'user__email', 'author__email',
    )
    empty_value_display = EMPTY_MSG


@admin.register(FavoriteRecipe)
class FavoriteRecipeAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'user', 'get_recipe', 'get_count'
    )
    empty_value_display = EMPTY_MSG

    @admin.display(
        description='Рецепты'
    )
    def get_recipe(self, obj):
        return [
            f'{item["name"]} ' for item in obj.recipe.values('name')[:5]]

    @admin.display(
        description='В избранных')
    def get_count(self, obj):
        return obj.recipe.count()


@admin.register(ShoppingCart)
class SoppingCartAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'user', 'get_recipe', 'get_count')
    empty_value_display = EMPTY_MSG

    @admin.display(description='Рецепты')
    def get_recipe(self, obj):
        return [
            f'{item["name"]} ' for item in obj.recipe.values('name')[:5]]

    @admin.display(description='В избранных')
    def get_count(self, obj):
        return obj.recipe.count()
