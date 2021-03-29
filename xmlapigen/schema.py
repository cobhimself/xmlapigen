from xmlschema import XMLSchema
from .generator import cache

class Schema():
    def __init__(self, xmlschema):
        self._schema = XMLSchema(xmlschema)
        self._compiled = False

    def compile(self):
        if not self._compiled:
            self._compile_groups()
            self._compile_types()
            self._compile_elements()
            self._compiled = True

    def _compile_groups(self):
        """Compile a cache of group data from our schema.
        """
        for group in self._schema.groups.values():
            cache.add_group(group)

    def _compile_types(self):
        """Compile a cache of type data from our schema.
        """
        for com in self._schema.complex_types:
            cache.add_type(com)

    def _compile_elements(self):
        """Compile a cache of global element data from our schema.
        """
        # Global elements
        for element in self._schema.elements.values():
            cache.add_element(element)

    def get_type(self, type_name):
        """Search the schema for the given type.

        Args:
            type_name (str): The name of the type to get.

        Raises:
            AttributeError: If unable to find the given type.

        Returns:
            Type: The type.
        """
        my_type = cache.get_type_or_define(
            type_name,
            self._schema.types.get(type_name)
        )
        if my_type is None:
            raise AttributeError(f'Unable to find type with name {type_name}')

        return my_type

    def get_group(self, group_name):
        """Search the schema for the given group.

        Args:
            group_name (str): The name of the group to get.

        Raises:
            AttributeError: If unable to find the given group.

        Returns:
            Group: The group.
        """
        my_group = cache.get_group_or_define(
            group_name,
            self._schema.groups.get(group_name)
        )
        if my_group is None:
            raise AttributeError(
                f'Unable to find group with name {group_name}'
            )

        return my_group

    def get_element(self, element_name):
        """Search the schema for the given element.

        Args:
            element_name (str): The name of the element to get.

        Raises:
            AttributeError: If unable to find the given element.

        Returns:
            XsdElement: The element.
        """
        my_element = self._schema.elements.get(element_name)
        if my_element is None:
            raise AttributeError(
                f'Unable to find element with name {element_name}'
            )

        return my_element

    def get_type_definition(self, type_name):
        """Return the xml definition of the given type.

        Args:
            type_name (str): The type to retrieve the raw xml for.

        Returns:
            str: The xml version of the given type.
        """
        return self.get_type(type_name).get_xml()

    def get_element_definition(self, element_name):
        """Return the xml definition of the given element.

        Args:
            element_name (str): The element to retrieve the raw xml for.

        Returns:
            str: The xml version of the given element.
        """
        return self.get_element(element_name).tostring()

    def get_group_element_definitions(self, group_name):
        definitions = {}
        elements = self.get_group(group_name).get_elements().items()
        for elem_name, elem in elements:
            definitions[elem_name] = elem.get_xml()

        return definitions

    def get_type_element_definitions(self, type_name):
        definitions = {}
        elements = self.get_type(type_name).get_elements().items()
        for elem_name, elem in elements:
            definitions[elem_name] = elem.get_xml()

        return definitions

    def get_group_definition(self, group_name):
        """Return the xml definition of the given group.

        Args:
            group_name (str): The group to retrieve the raw xml for.

        Returns:
            str: The xml version of the given group.
        """
        return self.get_group(group_name).get_xml()