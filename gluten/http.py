from django.utils import simplejson as json

import logging
logger = logging.getLogger("gluten")


def coerce_put_post(request):
    """
    Django doesn't particularly understand REST.
    In case we send data over PUT, Django won't
    actually look at the data and load it. We need
    to twist its arm here.

    The try/except abominiation here is due to a bug
    in mod_python. This should fix it.
    """
    if request.method == "PUT":
        # Bug fix: if _load_post_and_files has already been called, for
        # example by middleware accessing request.POST, the below code to
        # pretend the request is a POST instead of a PUT will be too late
        # to make a difference. Also calling _load_post_and_files will result
        # in the following exception:
        #   AttributeError: You cannot set the upload handlers after the upload has been processed.
        # The fix is to check for the presence of the _post field which is set
        # the first time _load_post_and_files is called (both by wsgi.py and
        # modpython.py). If it's set, the request has to be 'reset' to redo
        # the query value parsing in POST mode.
        if hasattr(request, '_post'):
            del request._post
            del request._files

        try:
            request.method = "POST"
            request._load_post_and_files()
            request.method = "PUT"
        except AttributeError:
            request.META['REQUEST_METHOD'] = 'POST'
            request._load_post_and_files()
            request.META['REQUEST_METHOD'] = 'PUT'

        request.PUT = request.POST


def check_api_key_authentication(request):
    from django.contrib.auth import authenticate, login
    token = request.COOKIES.get('token')

    username = request.REQUEST.get('username')
    if username is None:
        username = request.REQUEST.get('data[username]')
    if username is None:
        try:
            data = json.loads(request.raw_post_data)
            username = data.get('data', {}).get('username')
        except:
            pass

    if username and token:
        user = authenticate(username=username, token=token)
        if user:
            login(request, user)
            return True
    return False


def requested_language(request):
    return request.REQUEST.get('lang')
