from django.http import HttpResponse

from recipes.models import FavoriteRecipe, ShoppingCart, Subscribe


def get_cart_txt(ingredients):
    """Функция для создания текстового файла для списка покупок."""
    content_list = []
    for ingredient in ingredients:
        content_list.append(
            f'{ingredient["ingredient__name"]} '
            f'({ingredient["ingredient__measurement_unit"]}): '
            f'{ingredient["total_amount"]}')
    content = 'Ваш список покупок:\n\n' + '\n'.join(content_list)
    filename = 'shopping_cart.txt'
    file = HttpResponse(content, content_type='text/plain')
    file['Content-Disposition'] = 'attachment; filename={0}'.format(
        filename)
    return file


MODELS = {
    Subscribe: {
        'name': 'author',
        'err_exist': 'Вы уже подписаны на этого пользователя!',
        'err_not_exist': 'Вы не подписаны на этого пользователя!',
    },
    FavoriteRecipe: {
        'name': 'recipe',
        'err_exist': 'Этот рецепт уже в избранном!',
        'err_not_exist': 'Этого рецепта нет в избранном!',
    },
    ShoppingCart: {
        'name': 'recipe',
        'err_exist': 'Этот рецепт уже в корзине!',
        'err_not_exist': 'Этого рецепта нет в корзине!',
    },
}
