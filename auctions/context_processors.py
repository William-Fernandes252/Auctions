from django.conf import settings


def default_listing_img(request):
    return {
        'default_listing_img' : f'{settings.STATIC_URL}img/default_listing_img.jpg'
    }