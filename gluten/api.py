from django.core.serializers.json import DjangoJSONEncoder
from django.http import HttpResponse
import datetime
from django.utils import simplejson


class DataEncoder(DjangoJSONEncoder):
    """JSON encoder class that adds support for special types like dates."""

    def default(self, o):
        if isinstance(o, datetime.datetime):
            return o.replace(microsecond=0).isoformat()
        else:
            return super(DataEncoder, self).default(o)


def api_response(data, total_count=None, limit=None, offset=0, next_url=None, previous_url=None):
    """return json response.

    If data is an array, it returns::

        data = {
            'success': True,
            'result': {
                'meta': {
                    'limit': limit,
                    'next': next_url,
                    'offset': offset,
                    'previous': previous_url,
                    'total_count': total_count
                },
                'objects': data
            }
        }

    """

    if isinstance(data, type([])):
        if total_count is None:
            total_count = len(data)
        if limit is None:
            limit = total_count

        response = {
            'success': True,
            'result': {
                'meta': {
                    'limit': limit,
                    'next': next_url,
                    'offset': offset,
                    'previous': previous_url,
                    'total_count': total_count
                },
                'objects': data
            }
        }
        json_response = simplejson.dumps(response, cls=DataEncoder)
        return HttpResponse(json_response, mimetype='application/json')
    else:
        json_response = simplejson.dumps(data, cls=DataEncoder)
        return HttpResponse(json_response, mimetype='application/json')


def api_response_success(data=None, message=None):
    """shortcut to standard success response::

        response = {
            'success': True,
            'result': data,
            'message': message
        }

    """

    response = {
        'success': True,
        'result': data if data is not None else {},
    }

    if message is not None:
        response['message'] = unicode(message)

    return api_response(response)


def api_response_error(data=None, message=None):
    """shortcut to standard error response::

        response = {
            'success': False,
            'message': message
        }

    """

    response = {
        'success': False,
        'result': data if data is not None else {}
    }

    if message is not None:
        response['message'] = unicode(message)

    return api_response(response)


def api_response_raw(data):
    """return data in json format, with encoder aware of datetime
    """

    json_response = simplejson.dumps(data, cls=DataEncoder)
    return HttpResponse(json_response, mimetype='application/json')
