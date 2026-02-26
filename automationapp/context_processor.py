from automationapp import settings


def global_vars(request):
    return {
        'TEMPLATE_APP_NAME': settings.APP_NAME,
        'TEMPLATE_APP_ENV': settings.APP_ENV,
        'TEMPLATE_CONTACT_EMAIL': settings.ADMIN_EMAILS[0],
    }
