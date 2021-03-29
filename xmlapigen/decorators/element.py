"""
MIT License

Copyright (c) 2020 Collin Brooks

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
from .decorator import Decorator
from ..loader import Loader

ELEMENTS = 'elements'
TYPE = 'type'

class Element(Decorator):
    def __init__(self, tag_name, tag_type):
        super().__init__()
        self._tag_name = tag_name
        self._tag_type = tag_type

    def do(self):
        self._add_tag_element()
        self._add_element_method()

    def _add_tag_element(self):
        # Make sure we have a collection ready
        elements = self.provide(self.meta, ELEMENTS, {})

        # Add the element type data
        self.provide(elements, self._tag_name, {TYPE: self._tag_type})

    @staticmethod
    def _getter(fn_name, tag_name, tag_type):
        def get_element(self):
            return self.get_child(tag_name, tag_type)
        get_element.__name__ = fn_name

        return get_element

    def _add_element_method(self):
        xsd = self.xsd
        name = self._tag_name
        element_meta = self.get_meta(ELEMENTS).get(name)
        if element_meta is None:
            raise Exception(f'Element metadata for {name} does not exist!')

        node_type = element_meta.get(TYPE)

        if node_type is None:
            raise Exception(f'Cannot add {name} element method because its type cannot be determined!')

        doc = f"""Return child {name} element

        Returns:
            {node_type}: The model representing the {name}.
        """
        fn_name = f'get_{name}'
        self.add_method_to_cls(
            fn_name,
            self._getter(fn_name, name, node_type),
            doc
        )
