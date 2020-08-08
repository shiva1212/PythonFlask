from http import HTTPStatus

from flask_restx import Resource
from werkzeug.exceptions import HTTPException

from first_Flask.custom_exception import CustomException


class Response(dict):
    __setattr__ = dict.__setitem__
    __setattr__ = dict.__setitem__

    def __init__(self, data=None, message_code="UNKNOWN_ERROR"):
        self.data = data
        # self.status = status
        self.message_code = message_code


class BaseResource(Resource):
    def dispatch_request(self, *args, **kwargs):
        try:
            data, status, code = super().dispatch_request(*args, **kwargs)
            response = Response(data=data, message_code=code)
        except HTTPException as http_exception:
            status = http_exception.code
            code = "HTTP_ERROR"
            response = Response(message_code=code)

        except CustomException as custom_exception:
            status = custom_exception.status
            code = custom_exception.message_code
            response = Response(data=custom_exception.data, message_code=code)

        except BaseException as be:
            code="TECHNICAL_ERROR"
            status =  HTTPStatus.INTERNAL_SERVER_ERROR
            response = Response(message_code=code)
        return response, status

