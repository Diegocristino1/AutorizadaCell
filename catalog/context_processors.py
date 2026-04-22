from django.conf import settings


def social_links(request):
    return {
        'whatsapp_phone': getattr(settings, 'WHATSAPP_PHONE', ''),
        'whatsapp_message_default': getattr(
            settings,
            'WHATSAPP_DEFAULT_MESSAGE',
            'Olá! Vim pelo site e gostaria de mais informações.',
        ),
        'instagram_url': getattr(settings, 'INSTAGRAM_URL', '#'),
        'store_locale': getattr(settings, 'STORE_LOCALE', ''),
        'store_assistance_address': getattr(settings, 'STORE_ASSISTANCE_ADDRESS', ''),
    }
