import time
from functools import wraps

from rest_framework.response import Response
from rest_framework.views import exception_handler as origin_handler


def exception_handler(exc, context):
    response = origin_handler(exc, context)

    # Now add the HTTP status code to the response.
    incorrect_status_code_list = [400, 401, 403, 404, 405, 429, 500]

    payloads = {}

    if response is not None:
        if response.status_code in incorrect_status_code_list:
            payloads.update({"success": 0})
            payloads.update({"message": response.data})

        return Response(payloads, status=response.status_code)

    return response


def api_handler(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()

        payloads = {}
        status_code = 200

        result = func(*args, **kwargs)
        payloads.update({"success": 1, "result": result})

        if kwargs:
            payloads.update(kwargs)

        elapsed_time = round((time.time() - start_time) * 1000, 1)
        payloads["elapsed_time"] = f"{elapsed_time}ms"

        return Response(payloads, status=status_code)

    return wrapper
