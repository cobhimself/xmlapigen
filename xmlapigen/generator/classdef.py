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

This module contains helpers for creating python class definitions for the
generated doxyparser xsd library.
"""
import re
from textwrap import dedent
import inflect
from .config import SIMPLE, BOOLS, COMPLEX, PLACEHOLDER, ANY, ENUMS


class ClassDef():
    """
    Class used to construct a class to be generated.
    """

    HEAD_COMMENT = """
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

    This class has been auto-generated. To add/modify functionality, extend it.
    See util/generator/element_generator.py"""

    def __init__(self, name, config, definition):
        self._name = name
        self._config = config
        self._definition = definition
        self._import_lines = []
        self._decorators = []
        self._doc = ''
        self._supers = []
        self._add_header = True
        self._child_classes = []
        self._child_definitions = {}
        self._parent_class = None

    def get_decorators(self):
        return self._decorators

    def add_header(self, add_header=True):
        self._add_header = add_header

    def add_child_class(self, class_content):
        self._child_classes.append(class_content)

    def add_child_definitions(self, definitions):
        self._child_definitions = definitions

    def set_parent_class(self, parent_class):
        self._parent_class = parent_class

    def get_parent_class(self):
        return self._parent_class

    def get_config(self):
        """Get the configuration data to generate classes from.

        Returns:
            Config: The config object
        """
        return self._config

    @staticmethod
    def indent(text, initial_indent='', subsequent_indent=''):
        """Indent the given text

        Args:
            text (str): The text to indent
            initial_indent (str, optional): The string to place before the first
                line. Defaults to ''.
            subsequent_indent (str, optional): The string to place before the
                rest of the lines. Defaults to ''.

        Returns:
            str: The indented string
        """
        lines = text.splitlines()
        begin = initial_indent + lines.pop(0)
        final_lines = []
        for line in lines:
            final_lines.append((subsequent_indent + line)
                               if line.strip() else '')

        return begin + "\n" + "\n".join(final_lines)

    def get_definition(self):
        """Get the definition of the element represented by this class.

        Returns:
            str: The xml representation of the element
        """
        return self._definition

    def get_child_definition(self, name):
        definition = self._child_definitions.get(name)
        if definition is None:
            raise AttributeError(f'Could not get definition for {name}!')
        return self._child_definitions.get(name)

    def get_parent_or_self(self):
        parent_class = self.get_parent_class()
        return parent_class if parent_class is not None else self


    def get_name(self):
        """Get the name of the element this class represents.

        Returns:
            str
        """
        return self._name

    def determine_extends(self, path=None, supers=None):
        """Determine what class (or classes) this class should extend based
        upon the list of super class names.

        Args:
            path (str): The path to prepend to the super class' name.
            relative (str): The string to prepend to the path if this is a relative import.
            supers (list): The list of super class names this class should extend.
        """
        cls = self.get_parent_or_self()
        xsd = self.get_config().get_xsd()
        if supers is not None and len(supers) > 0:
            for sup in supers:
                class_name = self.get_class_name(sup)
                file_name = self.get_file_name(sup)
                path = path + '.' if path is not None else ''
                final_path = f'..{path}{file_name}'
                imp = f'from {final_path} import {class_name}'
                cls.add_import(imp)
                self.extends(f'{class_name}')
        else:
            cls.add_import('from ....node import Node')
            self.extends('Node')

    def determine_decorator_include(self):
        """Determine the different includes necessary for the decorators this
        class uses.
        """
        cls = self.get_parent_or_self()
        decorators = self.get_decorators()
        seen = []
        regex = r"@(.*)\("

        for decorator in decorators:
            matches = re.search(regex, decorator)
            if matches:
                match = matches.group(1)
                if match not in seen:
                    seen.append(match)

        for decorator in seen:
            cls.add_import(f'from ....decorators.{decorator.lower()} import {decorator}')

    @staticmethod
    def get_file_name(name):
        """Get the file name of this class.

        Args:
            name (str): The name of this class to create a file name for.

        Returns:
            str: The file name this class should have.
        """
        return ''.join(['_'+x.lower() if x.isupper() else x for x in name]).strip('_')

    def add_import(self, import_line):
        """Add an import to this class.

        Args:
            import_line (str): An import line to add to this class.
        """
        if import_line not in self._import_lines:
            self._import_lines.append(import_line)

    def get_imports(self):
        """Get the imports this class definition has.

        Returns:
            str: A line separated list of imports.
        """
        return "\n".join(sorted(self._import_lines))

    def extends(self, name):
        """Add a class for this class to extend.

        Args:
            name (str): The name of the class this class should extend.
        """
        self._supers.append(name)

    def add_decorator(self, decorator):
        """Add a class decorator.

        Args:
            decorator (str): The decorator to add.
        """
        self._decorators.append(decorator)

    def get_sorted_decorators(self):
        """Get the final decorators output.

        Returns:
            str: A line separated string of storted decorator strings.
        """
        return "\n".join(sorted(self._decorators))

    def set_class_doc(self, doc):
        """Set the documentation the class should use.

        Args:
            doc (str): The documentation
        """
        self._doc = doc

    def get_module_doc(self):
        """Get the documentation the module should use.

        Returns:
            str: The documentation
        """
        if self._add_header:
            return self.indent('"""' + dedent(self.HEAD_COMMENT) + "\n" + '"""') + "\n"

        return ''

    def get_class_doc(self):
        """Get the documentation the class should use.

        Returns:
            str: The documentation
        """
        return self.indent('"""' + self._doc + "\n" + '"""', '    ', '    ')

    @staticmethod
    def get_class_name(name):
        """Return the class name version of the given name.

        Args:
            name (str): The name to obtain the class name for.

        Returns:
            str: The class name
        """
        return name[0].upper() + name[1:]

    def get_extends(self):
        """Get a string representation of the classes this class should
            extend.

        Returns:
            str: The string of classes this class extends.
        """
        return ', '.join(self._supers)

    def build(self):
        """Build the class.

        This method must be defined by classes which extend this class.

        Raises:
            Exception: If a chile build method is not implemented.
        """
        raise Exception('Child classes must implement the build method!')

    def __str__(self):
        """Get the final string representation of this class definition.

        Returns:
            str: The final representation of the class.
        """
        self.build()
        self.determine_decorator_include()
        mod_doc = self.get_module_doc()
        imports = self.get_imports()
        decorators = self.get_sorted_decorators()
        class_doc = self.get_class_doc()
        child_classes = "\n\n\n".join(self._child_classes)

        out = (mod_doc + "\n") if mod_doc != '' else ''
        out += (imports + "\n\n") if imports != '' else ''
        out += (decorators + "\n") if decorators != '' else ''
        out += f"class {self.get_class_name(self._name)}({self.get_extends()}):\n"
        out += (class_doc) if class_doc != '' else ''
        out += ("\n\n\n" + child_classes) if child_classes != '' else ''
        # final new line
        if self.get_parent_class() is None:
            out += "\n"

        return out

    def add_attributes_to_class(self, attributes):
        """Add the given attributes to the decorators for this class.

        Args:
            attributes (dict): The attribute configuration.
        """
        for category, category_config in attributes.items():
            for attr_name in category_config:
                if category in [SIMPLE, ENUMS]:
                    self.add_decorator(f"@Attr('{attr_name}', {category_config[attr_name]})")
                elif category == BOOLS:
                    self.add_decorator(f"@BoolAttr('{attr_name}')")

    def _add_element_decorator(self, element_name, element_type):
        if element_type not in ('str', 'int', 'float'):
            element_type = f"'{element_type}'"
        self.add_decorator(
            f"@Element('{element_name}', {element_type})")


    def add_elements_to_class(self, elements):
        """Add the given elements to the decorators for this class.

        Args:
            elements (dict): The element configuration.

        Raises:
            Exception: If we come across an element category we haven't
                prepared for.
        """
        # Order by category
        categories = sorted(elements)
        config = self.get_config()
        for category in categories:
            category_config = elements.get(category)
            # The items in these categories are just element names, not types
            if category in [ANY]:
                for elem_name in category_config:
                    self._add_element_decorator(elem_name, category)
            elif category == PLACEHOLDER:
                if len(category_config) > 0:
                    decorator = "@Placeholders([\n"
                    decorator += ",\n".join(
                        [f"    '{p}'" for p in category_config])
                    decorator += "\n])"
                    self.add_decorator(decorator)
            else:
                for elem_name, type_name in category_config.items():
                    if category == COMPLEX:
                        if config.type_has_enum_attributes(type_name):
                            self.add_collection_decorators(
                                elem_name, type_name)
                        else:
                            self._add_element_decorator(elem_name, type_name)
                    elif category == SIMPLE:
                        self._add_element_decorator(elem_name, type_name)
                    else:
                        raise Exception(
                            f'Unknown element config category {category}')

    def add_collection_decorators(self, elem_name, type_name):
        """Add collection decorators for the given element and type name.

        Args:
            elem_name (str): The name of the element
            type_name (str): The name of its type.
        """
        enum_attrs = self.get_config().get_type_enum_attributes(type_name)
        collection = f"@Collection('{elem_name}', '{type_name}', {{\n"
        filters = []
        for attr, enums in enum_attrs.items():
            item = f"    '[@{attr}=\"{{}}\"]': {{\n"
            for enum in enums:
                plural_key = inflect.engine().plural(enum.replace('-', '_'))
                item += f"        '{plural_key}': '{enum}',\n"
            item += "    }"
            filters.append(item)
        collection += ",\n".join(filters) + "\n"

        collection += "})"

        self.add_decorator(collection)

    def add_complex_element_child_classes(self, complex_elements):
        for element_name, element_type in complex_elements:
            self.add_child_class(str(element_factory(
                element_name,
                element_type,
                self.get_child_definition(element_name),
                self._config,
                add_header=False,
                parent_class=self
            )))

class TypeClassDef(ClassDef):
    """Class representing a Type class.
    """

    def build(self):
        config = self.get_config()
        type_name = self.get_name()
        child_groups = config.get_type_groups(type_name)
        self.determine_extends('groups', child_groups)
        doc = f'Model representation of a doxygen {type_name} type.' + "\n\n"
        doc += "Type XSD:\n\n"
        doc += self.get_definition()
        self.set_class_doc(doc)

        self.add_attributes_to_class(config.get_type_attributes(type_name))
        self.add_elements_to_class(config.get_type_elements(type_name))

        complex_elements = config.get_type_elements(type_name).get(COMPLEX, {}).items()
        self.add_complex_element_child_classes(complex_elements)


        return self


class ElementClassDef(ClassDef):
    """Class representing an Element class.
    """

    def __init__(self, name, config, definition):
        super().__init__(name, config, definition)
        self._type_name = None

    def build(self):
        element_name = self.get_name()
        self.add_decorator(f'@Tag(\'{element_name}\')')
        self.determine_extends('types', [self.get_type(element_name)])
        self.determine_decorator_include()
        doc = f'Model representation of a doxygen {element_name} element.' + "\n\n"
        doc += "Type XSD:\n\n"
        doc += self.get_definition()
        self.set_class_doc(doc)

    def set_type(self, type_name):
        self._type_name = type_name

    def get_type(self, element_name):
        config = self.get_config()
        if self._type_name is None:
            self._type_name = config.get_element_type(element_name)

        return self._type_name



class GroupClassDef(ClassDef):
    """Class representing a Group class.
    """

    def build(self):
        config = self.get_config()
        group_name = self.get_name()
        child_groups = config.get_group_groups(group_name)
        self.determine_extends('groups', supers=child_groups)
        doc = f'Model representation of a doxygen {group_name} group.' + "\n\n"
        doc += "Type XSD:\n\n"
        doc += self.get_definition()
        self.set_class_doc(doc)
        self.add_elements_to_class(config.get_group_elements(group_name))

        complex_elements = config.get_group_elements(group_name).get(COMPLEX, {}).items()
        self.add_complex_element_child_classes(complex_elements)

def group_factory(group_name, config, definition, element_definitions):
    group_class = GroupClassDef(group_name, config, definition)
    group_class.add_child_definitions(element_definitions)

    return group_class

def type_factory(type_name, config, definition, element_definitions):
    type_class = TypeClassDef(type_name, config, definition)
    type_class.add_child_definitions(element_definitions)

    return type_class

def element_factory(element_name, element_type, definition, config, add_header=True, parent_class=None):
    element_class = ElementClassDef(element_name, config, definition)
    element_class.set_type(element_type)
    element_class.add_header(add_header)
    element_class.set_parent_class(parent_class)

    return element_class
