from rest_framework.views import exception_handler
import rest_framework.exceptions as drf_exc
import django.core.exceptions as django_exc


# https://www.django-rest-framework.org/api-guide/exceptions/#custom-exception-handling
def custom_exception_handler(exc, context):
    if isinstance(exc, django_exc.ValidationError):
        exc = drf_exc.ValidationError(detail=dict(detail=exc.messages))

    response = exception_handler(exc, context)

    return response
