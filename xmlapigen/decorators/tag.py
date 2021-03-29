from .decorator import Decorator

TAG = 'tag'

class Tag(Decorator):
    def __init__(self, tag_name):
        super().__init__()
        self._tag_name = tag_name

    def do(self):
        self.provide(self.meta, TAG, self._tag_name)