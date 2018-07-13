class FilterException(Exception):
    def __init__(self, message=None):
        self.message = message

    def __str__(self):
        filter_message = f': {self.message}' if self.message else ''
        return f'Invalid filter{filter_message}'
