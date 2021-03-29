from .attr import Attr

class BoolAttr(Attr):
    def __init__(self, attr_name):
        super().__init__(attr_name, bool)
