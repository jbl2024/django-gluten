from django.http import HttpResponseNotAllowed, HttpResponse
from django.utils.decorators import available_attrs
from django.conf import settings
from django.utils.functional import wraps
from http import check_api_key_authentication, coerce_put_post, requested_language
from django.utils import translation

import logging
logger = logging.getLogger("gluten")


def activate_language(language):
    if language in settings.ALLOWED_LANGUAGES:
        translation.activate(language)


def gluten_api(methods=['GET', 'POST', 'PUT', 'DELETE'], login_required=True):
    """
    """
    def decorator(func):
        def inner(request, *args, **kwargs):
            if request.method not in methods:
                logger.warning(
                    'Method Not Allowed (%s): %s' % (
                        request.method, request.path),
                    extra={
                        'status_code': 405,
                        'request': request
                    }
                )
                return HttpResponseNotAllowed(methods)

            coerce_put_post(request)

            language = requested_language(request)
            if language is not None and language != request.LANGUAGE_CODE:
                activate_language(language)

            authorized = check_api_key_authentication(request)
            if not authorized:
                authorized = request.user.is_authenticated()
            if login_required and not authorized:
                return HttpResponse(status=401)

            return func(request, *args, **kwargs)
        return wraps(func, assigned=available_attrs(func))(inner)
    return decorator


def html_decorator(func):
    """
    wrap it inside html
    """

    def _decorated(*args, ** kwargs):
        response = func(*args, **kwargs)

        wrapped = ("<html><body>",
                   response.content,
                   "</body></html>")

        return HttpResponse(wrapped)

    return _decorated
