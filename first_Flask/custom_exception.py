## if we getting any error then we raise exception
class CustomException(Exception):
    def __init__(self, data=None, message_code=None, status=None):
        self.message_code = message_code
        self.status = status
        self.data = data

