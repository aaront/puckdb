class FilterException(Exception):
    def __init__(self, message=None):
        self.message = message

    def __str__(self):
        return 'Invalid filter{message}'.format(': ' + self.message if self.message else '')
