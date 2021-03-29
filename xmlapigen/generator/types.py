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

This module contains doxyparser-specific types which wrap the xmlschema
types.
"""
from xmlschema.validators import XsdGroup
from xmlschema.validators.elements import XsdElement
from xmlschema.validators.attributes import XsdAttributeGroup, XsdAttribute, XsdAnyAttribute
from xmlschema.validators.simple_types import XsdAtomicBuiltin
from ..element_generator import cache


class Super():
    """Super class all types extend from.
    """
    def __init__(self, definition):
        self._definition = definition

    def get_definition(self):
        """Get the original xmlschema definition type

        Returns:
            mixed
        """
        return self._definition

    def get_xml(self):
        return self.get_definition().tostring()

    def get_type_from_cache(self, type_name):
        """Get the type with the given name from our type cache.

        Args:
            type_name (str): the type's name

        Returns:
            Type: the type matching the given name.
        """
        return cache.get_type(type_name)

    def get_group_from_cache(self, group_name):
        return cache.get_group(group_name)

    def get_cache(self):
        return cache

class Typeable(Super):
    def __init__(self, definition, type_instance=None):
        if type_instance is None:
            self._type = Type(
                definition if isinstance(definition, XsdAnyAttribute)
                else definition.type
            )
        else:
            self._type = type_instance

        super().__init__(definition)

    def get_type(self):
        return self._type

    def get_type_local_name(self):
        return self.get_type().get_local_name()

    def is_any_type(self):
        return self.get_type().is_any_type()

    def is_dox_bool(self):
        return self.get_definition().type.name == 'DoxBool'

    def get_type_name(self):
        return self.get_type().get_name()

    def has_content(self):
        return self.get_type().has_content()

    def get_content(self):
        return self.get_type().get_content()

    def is_element_only(self):
        return self.get_type().is_element_only()

    def is_simple(self):
        return self.get_type().is_simple()

    def is_text_only(self):
        return self.get_type().is_text_only()

    def is_complex(self):
        return self.get_type().is_complex()

    def is_placeholder(self):
        return self.get_type().is_placeholder()


class Buildable(Super):
    """Provides a class with the ability to build doxyparser-specific data
    relating to XSD attributes, elements and groups.
    """
    def __init__(self, definition):
        super().__init__(definition)
        self._attr = {}
        self._elem = {}
        self._group = {}
        self._built = False

    def _build(self):
        """Build the internal types of the components in this class'
        definition.
        """
        if not self._built:
            definition = self.get_definition()
            for component in definition.iter_components():
                if component == definition:
                    continue
                if isinstance(component, XsdAttributeGroup):
                    continue
                if isinstance(component, XsdAttribute):
                    continue
                if isinstance(component, XsdAnyAttribute):
                    continue
                if isinstance(component, XsdGroup):
                    self._build_group(component)
                elif isinstance(component, XsdElement):
                    self._build_element(component)
                else:
                    breakpoint()
                    print(component)

            if hasattr(definition, 'attributes'):
                for attr_name, attr in definition.attributes.items():
                    self._attr[attr_name] = Attribute(attr, self)

        self._built = True

    def _build_group(self, group):
        """Iterate through the group's components and add them to this
        buildable object.

        Args:
            group (XsdGroup): The group to build
        Raises:
            Exception: if we're not currently handline all of the components,
                make it known.
        """
        # This group references a complex type
        if group.ref is not None:
            group_ref = self.get_group_from_cache(group.name)
            self._group[group.name] = group_ref
        else:
            for component in group.iter_components():
                is_group = isinstance(component, XsdGroup)
                # Iterating the components usually returns the group itself so
                # we check to make sure our component isn't the group itself.
                # Also, for groups within groups, we don't want to traverse
                # deeply because it would mean we going into the elements of
                # the child group. We just want a reference to the group's
                # name.
                if component == group or (is_group and component.ref is None):
                    continue
                if is_group:
                    # self._build_group(component)
                    # Since we don't want to dive deeper into child groups,
                    # continue.
                    continue

                if isinstance(component, XsdElement):
                    self._build_element(component)
                else:
                    # Seems we've encountered a component we haven't prepared
                    # for. Make it known.
                    raise Exception(
                        f'Unhandled component {component} during build process!')

    def _build_element(self, element):
        node_type = self.get_type_from_cache(element.type)
        self._elem[element.name] = Element(element, node_type)

    def get_attributes(self):
        """Get a list of Attributes associated with this type.

        Returns:
            Attribute[]: A list of Attribute models for the attributes in
                this type.
        """
        self._build()
        return self._attr

    def get_elements(self):
        """Return a list of Elements associated with this type.

        Returns:
            Element[]: A list of Element models for the elements in this
                type.
        """
        self._build()
        return self._elem

    def get_groups(self):
        """Get the groups associated with this object.

        Returns:
            dict: Returns a dict with group names as keys and Group objects
                as values.
        """
        self._build()
        return self._group

class Type(Buildable):
    def get_name(self):
        """Get the name of this type.

        Returns:
            str: The name of this type.
        """
        return self.get_definition().name

    def has_content(self):
        """Determine whether or not this type has either nested elements
        or text.

        Returns:
            bool: True if there is content in this type, False otherwise.
        """
        return self.get_definition().content is not None

    def has_empty_content(self):
        """Determine whether or not this type's content is empty.

        If the type does not support content, it is considered to have empty
        content.

        Returns:
            bool: True if there is content, False otherwise.
        """
        return not self.has_content() or self.get_content().is_empty()

    def is_placeholder(self):
        """Determine whether or not this type is a simple placeholder.

        A placeholder is defined as an element with no attributes and no content.

        Ex: <hr/>

        Returns:
            bool: True if this is a placeholder type, false otherwise
        """
        return (self.is_empty()
            and self.has_empty_content()
            and not self.has_attributes())

    def has_attributes(self):
        """Determine whether or not this type has attributes.

        Returns:
            bool: True if this type has attributes, False otherwise.
        """
        return len(self.get_definition().attributes) > 0

    def get_content(self):
        """Get the content of this type.

        Returns:
            mixed: None if no content exists, mixed otherwise.
        """
        return self.get_definition().content

    def has_simple_content(self):
        """Determine whether or not this type denys element content but
        allows text content.

        Returns:
            bool: True if only text content is allowed, False otherwise.
        """
        return self.has_content() and self.get_definition().has_simple_content()

    def has_complex_content(self):
        """Determine whether or not this type allows element content.

        Returns:
            bool: True if elements are allowed, False otherwise.
        """
        return self.has_content() and self.get_definition().has_complex_content()

    def has_element_only_content(self):
        """Determine whether or not this type allows child elements but denys
        intermingled text content.

        Returns:
            bool: True if this element does not contain text intermingled
                with elements; False otherwise.
        """
        return self.has_content() and self.get_content().is_element_only()

    def has_mixed_content(self):
        """Determine whether or not this type allows child elements and
        intermingled text.

        Returns:
            bool: True if this type allows elements and intermingled text;
                False otherwise.
        """
        return self.has_content() and self.get_content().has_mixed_content()

    def is_simple(self):
        """Determine whether or not this type is a simple type.

        Simple types do not allow attributes or element content.

        Returns:
            bool: True if this type is a simple type; False otherwise.
        """
        return self.get_definition().is_simple()

    def is_complex(self):
        """Determine whether or not this type is a complex type.

        Complex types allow attributes and/or element content.

        Returns:
            bool: True if this type is a complex type, False otherwise.
        """
        return self.get_definition().is_complex()

    def is_empty(self):
        return self.get_definition().is_empty()

    def is_element_only(self):
        return self.get_definition().is_element_only()

    def is_any_type(self):
        return self.get_local_name() == 'anyType'

    def is_text_only(self):
        return self.get_definition().has_simple_content()

    def allows_elements_and_text(self):
        """Alias method for has_mixed_content()

        Returns:
            bool: True if this type allows elements and/or text. False
                otherwise.
        """
        return self.has_mixed_content()

    def get_local_name(self):
        my_type = self.get_definition()
        local_name = my_type.local_name
        if my_type.is_restriction():
            name = my_type.root_type.python_type.__name__
        elif my_type.is_union():
            for i in my_type.member_types:
                if i.is_restriction():
                    name = i.root_type.python_type.__name__
                    break
        elif my_type.is_complex():
            name = local_name
        elif my_type.is_simple():
            if isinstance(my_type, XsdAtomicBuiltin):
                name = my_type.python_type.__name__
            else:
                name = my_type.python_type
        else:
            name = my_type.python_type.__name__

        return name



class Element(Typeable):
    def __init__(self, element, node_type):
        self._attr = {}
        super().__init__(element, type_instance=node_type)

    def get_name(self):
        return self._definition.name

    def get_attributes(self):
        if len(self._attr) == 0:
            for attr_name, attr in self._definition.attributes.items():
                self._attr[attr_name] = Attribute(attr, self)

        return self._attr

    def get_attribute_by_name(self, name):
        return self._attr.get(name, None)

class Group(Buildable):
    def __init__(self, definition):
        super().__init__(definition)
        self._elements = None
        self._groups = None

    def get_name(self):
        return self.get_definition().name

class Attribute(Typeable):
    """Class responsible for holding information relating to xsd schema
    attributes
    """

    def __init__(self, element, parent):
        self._enums = None
        self._parent = parent
        super().__init__(element)

    def get_name(self):
        """Get the name of this attribute.

        Returns:
            string: The local name of this attribute
        """
        return self._definition.local_name

    def is_any_attribute(self):
        """Determine if this attribute is an XsdAnyAttribute.

        Returns:
            bool
        """
        return isinstance(self.get_definition(), XsdAnyAttribute)

    def is_enum(self):
        """Determine whether or not this attribute has enum values.

        Returns:
            bool
        """
        return len(self.get_enum_values()) > 0

    def get_enum_values(self):
        """Get the enum values associated with this attribute.

        For types that are union types, we dig deep into them to find whether
        or not any of their members have enum values.

        Returns:
            list: A list of enum values
        """

        if self._enums is None:
            resolved = None
            my_type = self.get_definition().type
            if my_type.is_union():
                for i in my_type.member_types:
                    if i.is_restriction():
                        resolved = i
                        break
            elif my_type.is_restriction():
                resolved = my_type

            if resolved is None:
                self._enums = []
            else:
                if resolved.is_simple():
                    self._enums = [] if resolved.enumeration is None or resolved.enumeration == [
                        ''] else resolved.enumeration

        return self._enums

    def is_required(self):
        """Determine whether or not this attribute is required.

        Returns:
            bool
        """
        return self._definition.is_required

    def is_optional(self):
        """Determine whether or not this attribute is optional.

        Returns:
            bool
        """
        return self._definition.is_optional
