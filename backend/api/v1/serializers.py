import django.contrib.auth.password_validation as validators
from django.contrib.auth import authenticate
from django.contrib.auth.hashers import make_password
from django.shortcuts import get_object_or_404
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from recipes.models import Ingredient, Recipe, RecipeIngredient, Subscribe, Tag
from user.models import User

from .fields import Base64ImageField

ERR_MSG = 'Не удается войти в систему с предоставленными учетными данными.'


class GetIsSubscribedMixin:

    def get_is_subscribed(self, obj):
        user = self.context['request'].user
        if not user.is_authenticated:
            return False
        return user.follower.filter(author=obj).exists()


class UserListSerializer(GetIsSubscribedMixin, serializers.ModelSerializer):
    """
    Сериализатор для модели User, который возвращает список пользователей.
    """
    is_subscribed = serializers.BooleanField(read_only=True)

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username',
            'first_name', 'last_name', 'is_subscribed')


class UserCreateSerializer(serializers.ModelSerializer):
    """
    Сериализатор для создания новых экземпляров модели User в системе
    """
    class Meta:
        model = User
        fields = (
            'id', 'email', 'username',
            'first_name', 'last_name', 'password',)

    def validate_password(self, password) -> str:
        """
        Метод для валидации поля password.
        """
        validators.validate_password(password)
        return password


class UserPasswordSerializer(serializers.ModelSerializer):
    """
    Сериализатор для изменения пароля пользователя.
    """
    new_password = serializers.CharField(
        label='Новый пароль')
    current_password = serializers.CharField(
        label='Текущий пароль')

    class Meta:
        model = User
        fields = ('new_password', 'current_password')

    def validate_current_password(self, current_password):
        """
        Проверка правильности текущего пароля пользователя.
        """
        user = self.context['request'].user
        if not authenticate(
                username=user.email,
                password=current_password):
            raise serializers.ValidationError(
                ERR_MSG, code='authorization')
        return current_password

    def validate_new_password(self, new_password):
        """
        Проверка правильности нового пароля пользователя.
        """
        validators.validate_password(new_password)
        return new_password

    def create(self, validated_data):
        """
        Изменение пароля пользователя.
        """
        user = self.context['request'].user
        password = make_password(
            validated_data.get('new_password'))
        user.password = password
        user.save()
        return validated_data


class TokenSerializer(serializers.Serializer):
    """
    Сериализатор для генерации токена аутентификации.
    """
    email = serializers.CharField(
        label='Email',
        write_only=True)
    password = serializers.CharField(
        label='Пароль',
        style={'input_type': 'password'},
        trim_whitespace=False,
        write_only=True)
    token = serializers.CharField(
        label='Токен',
        read_only=True)

    def validate(self, attrs):
        """
        Проверка введенных данных для аутентификации пользователя.
        """
        email = attrs.get('email')
        password = attrs.get('password')
        if email and password:
            user = authenticate(
                request=self.context.get('request'),
                email=email,
                password=password)
            if not user:
                raise serializers.ValidationError(
                    ERR_MSG,
                    code='authorization')
        else:
            msg = 'Необходимо указать "адрес электронной почты" и "пароль".'
            raise serializers.ValidationError(
                msg,
                code='authorization')
        attrs['user'] = user
        return attrs


class TagSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Teg.
    """
    class Meta:
        model = Tag
        fields = (
            'id', 'name', 'color', 'slug',
        )


class IngredientSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Ingredient.
    """
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit',)
        validators = [
            UniqueTogetherValidator(
                queryset=Ingredient.objects.all(),
                fields=('name', 'measuer'),
                message=('Такой ингредиент уже есть в базе.')
            )
        ]

    def validate_name(self, value):
        """
        Проверка, что название ингредиента не пустое.
        """
        if not value.strip():
            raise serializers.ValidationError(
                'Название ингредиента не должно быть пустым.'
            )
        return value


class RecipeIngredientSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели RecipeIngredient.
    """
    id = serializers.ReadOnlyField(
        source='ingredient.id')
    name = serializers.ReadOnlyField(
        source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit')

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeUserSerializer(
        GetIsSubscribedMixin,
        serializers.ModelSerializer):
    """
    Сериализатор для модели User.
    """
    is_subscribed = serializers.SerializerMethodField(
        read_only=True)

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username',
            'first_name', 'last_name', 'is_subscribed'
        )


class IngredientsEditSerializer(serializers.ModelSerializer):
    """
    Сериализатор для создания и обновления объектов модели Ingredient.
    """
    id = serializers.IntegerField()
    amount = serializers.IntegerField()

    class Meta:
        model = Ingredient
        fields = ('id', 'amount')

    def validate_ingredient_amount(self, value):
        """
        Проверка, что ingredient_amount является положительным числом.
        """
        if value < 1:
            raise serializers.ValidationError(
                "Количество ингредиента должно быть положительным числом."
            )
        return value


class RecipeWriteSerializer(serializers.ModelSerializer):
    """
    Сериализатор для создания и обновления объектов модели Recipe.
    """
    image = Base64ImageField()
    tags = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Tag.objects.all())
    ingredients = IngredientsEditSerializer(
        many=True)

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags',
            'author', 'ingredients',
            'name', 'image', 'text',
            'cooking_time',
        )
        read_only_fields = ('author',)

    def validate_ingredients(self, ingredients):
        if not ingredients:
            raise serializers.ValidationError(
                'Мин. 1 ингредиент в рецепте!')
        for ingredient in ingredients:
            if int(ingredient.get('amount')) < 1:
                raise serializers.ValidationError(
                    'Количество ингредиента >= 1!')
        return ingredients

    def create_ingredients(self, ingredients, recipe):
        for ingredient in ingredients:
            RecipeIngredient.objects.create(
                recipe=recipe,
                ingredient_id=ingredient.get('id'),
                amount=ingredient.get('amount'), )

    def validate(self, data):
        if data['cooking_time'] <= 0:
            raise serializers.ValidationError(
                'Время приготовления не может быть менее минуты.'
            )
        ingredients = data['ingredients']
        ingredient_list = []
        for items in ingredients:
            ingredient = get_object_or_404(
                Ingredient, id=items['id'])
            if ingredient in ingredient_list:
                raise serializers.ValidationError(
                    'Ингредиент должен быть уникальным!')
            ingredient_list.append(ingredient)
        return data

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        self.create_ingredients(ingredients, recipe)
        return recipe

    def update(self, instance, validated_data):
        if 'ingredients' in validated_data:
            ingredients = validated_data.pop('ingredients')
            instance.ingredients.clear()
            self.create_ingredients(ingredients, instance)
        if 'tags' in validated_data:
            instance.tags.set(
                validated_data.pop('tags'))
        return super().update(
            instance, validated_data)

    def to_representation(self, instance):
        return RecipeReadSerializer(
            instance,
            context={
                'request': self.context.get('request')
            }).data


class RecipeReadSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Resipe.
    """
    image = Base64ImageField()
    tags = TagSerializer(
        many=True,
        read_only=True)
    author = RecipeUserSerializer(
        read_only=True,
        default=serializers.CurrentUserDefault())
    ingredients = RecipeIngredientSerializer(
        many=True,
        required=True,
        source='recipe')
    is_favorited = serializers.BooleanField(
        read_only=True)
    is_in_shopping_cart = serializers.BooleanField(
        read_only=True)

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'author', 'ingredients',
            'is_favorited', 'is_in_shopping_cart', 'name',
            'image', 'text', 'cooking_time'
        )


class SubscribeRecipeSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Resipe.
    """
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class SubscribeSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Resipe.
    """
    id = serializers.IntegerField(
        source='author.id')
    email = serializers.EmailField(
        source='author.email')
    username = serializers.CharField(
        source='author.username')
    first_name = serializers.CharField(
        source='author.first_name')
    last_name = serializers.CharField(
        source='author.last_name')
    recipes = serializers.SerializerMethodField()
    is_subscribed = serializers.BooleanField(
        read_only=True)
    recipes_count = serializers.IntegerField(
        read_only=True)

    class Meta:
        model = Subscribe
        fields = (
            'email', 'id', 'username', 'first_name', 'last_name',
            'is_subscribed', 'recipes', 'recipes_count',)

    def get_recipes(self, obj):
        request = self.context.get('request')
        limit = request.GET.get('recipes_limit')
        recipes = (
            obj.author.recipe.all()[:int(limit)] if limit
            else obj.author.recipe.all())
        return SubscribeRecipeSerializer(
            recipes,
            many=True).data
