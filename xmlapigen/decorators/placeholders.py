from .decorator import Decorator

PLACEHOLDERS = 'placeholders'

class Placeholders(Decorator):
    def __init__(self, placeholders):
        super().__init__()
        self._placeholders = placeholders

    def do(self):
        self._add_placeholders()

    def _add_placeholders(self):
        self.provide(self.get_meta(), PLACEHOLDERS, self._placeholders)