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
from ..util.generator.classdef import ClassDef

COLLECTIONS = 'collections'
COLLECTORS = 'collectors'
TYPE = 'type'
GETTER = 'getter'
ARGS = 'args'

class Collection(Decorator):
    """Describe a collection of child elements in the decorated class which
       can be obtained through the use of xpath filters.
    """
    __slots__ = ['_tag_name', '_node_type','_collectors_to_init']

    def __init__(self, tag_name, node_type, collectors=None):
        super().__init__()
        self.tag_name = tag_name
        self.node_type = node_type
        self._collectors_to_init = collectors

    @property
    def tag_name(self):
        """Get the collection's tag name.

        Returns:
            str: The collection's tag name.
        """
        return self._tag_name

    @tag_name.setter
    def tag_name(self, value):
        """Set the collection's tag name.

        Args:
            value (str): The collection's tag name.
        """
        self._tag_name = value

    @property
    def node_type(self):
        """Get the type of this collection's node.

        Returns:
            [type]: [description]
        """
        return self._node_type

    @node_type.setter
    def node_type(self, value):
        self._node_type = value

    @property
    def collections(self):
        """Get the collections metadata.

        Returns:
            dict: The collections metadata.
        """
        return self.provide(self.meta, COLLECTIONS, {})

    @property
    def collection(self):
        """Get the collection data for this collection's tag.

        Returns:
            dict: This collection's tag's collection data.
        """
        return self.provide(self.collections, self.tag_name, {TYPE: self.node_type})

    @property
    def collectors(self):
        """Get the collectors for this collection's tag.

        Returns:
            dict: This collectin's tag's collectors.
        """
        return self.provide(self.collection, COLLECTORS, {})

    @collectors.setter
    def collectors(self, value):
        """Set the collectors for this collection's tag.

        Args:
            value (dict): Collectors data.
        """
        if value is None:
            value = {}

        self.collection[COLLECTORS] = value

    @property
    def path(self):
        node_type = self.node_type
        return f'types.{ClassDef.get_file_name(node_type)}.{node_type}'

    def do(self):
        """Perform the decoration
        """
        self.collectors = self._collectors_to_init
        self._collectors_to_init = None
        self._add_tag_collection()
        self._add_collection_methods()

    def _add_tag_collection(self):
        """Add a collection for this collection's tag.
        """

        #Add our collector methods
        if self.collectors is not None:
            for xpath, getters in self.collectors.items():
                for getter, args in getters.items():
                    xpath_methods = self.provide(self.collectors, xpath, {})
                    xpath_methods[getter] = args

    @staticmethod
    def _getter(fn_name, xpath_args=None):
        def collect(self):
            return self.get_collection(self.tag_name, xpath_args)
        collect.__name__ = fn_name

        return collect

    def _add_collection_methods(self):
        tag_class = Loader.load_tag_class(self.xsd, self.path)
        collectors = self.collectors

        main_doc_template = f'Return child {self.tag_name} elements'
        collection_doc_template = main_doc_template + ' matching xpath \'{tag}/{filter}\''
        return_template = """

        Returns:
            list({returns}): A list of {tag} elements found.
        """

        #Our main collection tag should have a method where all elements
        #matching the tag name are returned. This method will not use any
        #xpath arguments and will simply return all elements matching the
        #tag name.
        fn_name = f'get_{self.tag_name}s'
        doc = main_doc_template + return_template.format(
            tag=self.tag_name,
            returns='.'.join([tag_class.__module__, tag_class.__name__])
        )
        self.add_method_to_cls(fn_name, self._getter(fn_name), doc)

        if collectors:
            for pattern, xpath_args in collectors.items():
                for method_tail, pattern_arg in xpath_args.items():
                    fn_name = f'get_{self.tag_name}_{method_tail}'
                    get = self._getter(fn_name, [pattern, pattern_arg])
                    doc = (collection_doc_template + return_template).format(
                        tag=self.tag_name,
                        filter=pattern.format(pattern_arg),
                        returns='.'.join([tag_class.__module__, tag_class.__name__])
                    ).strip()
                    self.add_method_to_cls(fn_name, get, doc)
