from rest_framework.views import exception_handler


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is not None:
        response.data = {'code': response.status_code}
        if response.status_code == 404:
            response.data['message'] = 'Item not found'
        elif response.status_code == 400:
            response.data['message'] = 'Validation Failed'

    return response
