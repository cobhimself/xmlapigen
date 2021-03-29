from .decorator import Decorator

ATTRIBUTES = 'attributes'

class Attr(Decorator):
    def __init__(self, attr_name, attr_type):
        super().__init__()
        self._attr_name = attr_name
        self._attr_type = attr_type

    def do(self):
        self._add_tag_attribute()
        self._add_attribute_method()

    def _add_tag_attribute(self):
        # Make sure we have a collection ready
        attributes = self.provide(self.meta, ATTRIBUTES, {})

        # Add the element type data
        self.provide(attributes, self._attr_name, {'type': self._attr_type})

    @staticmethod
    def _getter(fn_name, attr_name, attr_type):
        def get_attribute(self):
            return self.get_attr(attr_name, attr_type)
        get_attribute.__name__ = fn_name

        return get_attribute

    def _add_attribute_method(self):
        name = self._attr_name
        attr_type = self._attr_type

        doc = f"""Return {name} attribute value

        Returns:
            {self._attr_type}
        """
        fn_name = f'get_{name}'
        self.add_method_to_cls(
            fn_name,
            self._getter(fn_name, name, attr_type),
            doc
        )
