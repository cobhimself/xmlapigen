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
import pathlib
import sys
import os
from .generator import cache
from .schema import Schema
from .generator.classdef import ElementClassDef, element_factory, group_factory, type_factory
from .generator.config import Config, COMPLEX


class ElementGenerator():
    """Class responsible for generating xsd-based configuration and classes
    """

    def __init__(self, output, inputs):
        self._root = str(pathlib.Path(__file__).parent.parent)
        self._output_dir = output
        self._inputs = inputs
        self._xmldir = self._root + '/../test/_sample_data/_build/php/xml/'
        config_file = str(pathlib.Path(
            self._root + '/util/generator/config.yml'))
        self._config = Config(config_file)
        self._xsd = xsd
        self._xsd_out_dir = self._root + '/xsd/'
        self._schema = None

    def load_schema(self, xsd):
        """Load the schema for the given xsd file.

        Args:
            xsd (str): The xsd file name without the extension.
        """
        self._schema = Schema(self._get_xsd_file_path(xsd))

    def get_schema(self):
        return self._schema

    @staticmethod
    def _write(path, content):
        """Write the content to the file at the given path.

        Args:
            path (str): The location where we should write the content.
            content (str): The content to write.
        """
        file = open(path, 'w')
        file.write(content)
        file.close()

    @staticmethod
    def _append(path, content):
        file = open(path, 'a')
        file.write(content)
        file.close()

    def _get_xsd_file_path(self, xsd):
        """Get the file path for the given xsd file.

        Args:
            xsd (str): The name of the xsd file, without the extension, we
            want to get the path for.

        Returns:
            str: The file path for the xsd file.
        """
        return str(pathlib.Path(f'{self._xmldir}/{xsd}.xsd').resolve())

    def _get_xsd_dir(self):
        """Get the directory of the xsd root folder.

        Returns:
            str: The xsd root folder path.
        """
        return self._root + '/xsd/'

    def _get_dir_for_xsd(self, xsd):
        """Get the directory where we will put files relating to the given
        xsd name.

        Args:
            xsd (str): The name of the xsd without file extension.

        Returns:
            str: The directory where files for this xsd will be placed.
        """
        return self._get_xsd_dir() + f'{xsd}/'

    def _get_elements_dir(self, xsd):
        """Get the elements directory for the given xsd.

        Args:
            xsd (str): The name of the xsd without file extension.

        Returns:
            str: The directory where elements will be placed for the given
                xsd.
        """
        return self._get_dir_for_xsd(xsd) + 'elements/'

    def _get_types_dir(self, xsd):
        """Get the types directory for the given xsd.

        Args:
            xsd (str): The name of the xsd without file extension.

        Returns:
            str: The directory where types will be placed for the given
                xsd.
        """
        return self._get_dir_for_xsd(xsd) + 'types/'

    def _get_groups_dir(self, xsd):
        """Get the groups directory for the given xsd.

        Args:
            xsd (str): The name of the xsd without file extension.

        Returns:
            str: The directory where groups will be placed for the given
                xsd.
        """
        return self._get_dir_for_xsd(xsd) + 'groups/'

    def _generate_groups(self, xsd_name):
        config = self._config
        groups_dir = self._get_groups_dir(xsd_name)
        groups = config.get_groups()
        schema = self.get_schema()
        if len(groups) > 0:
            self._write_package_folders([groups_dir])

        for group_name in groups.keys():
            class_def = group_factory(
                group_name,
                config,
                schema.get_group_definition(group_name),
                schema.get_group_element_definitions(group_name)
            )
            out = groups_dir + class_def.get_file_name(group_name) + '.py'
            self._write(
                out,
                str(class_def)
            )

    def _generate_types(self, xsd_name):
        config = self._config
        types_dir = self._get_types_dir(xsd_name)
        types = config.get_types()
        schema = self.get_schema()
        if len(types) > 0:
            self._write_package_folders([types_dir])

        # Types
        for type_name in types.keys():
            class_def = type_factory(
                type_name,
                self._config,
                schema.get_type_definition(type_name),
                schema.get_type_element_definitions(type_name)
            )
            self._write(
                types_dir + class_def.get_file_name(type_name) + '.py',
                str(class_def)
            )

    def _generate_elements(self, xsd_name):
        config = self._config
        elements_dir = self._get_elements_dir(xsd_name)
        elements = config.get_elements()
        schema = self.get_schema()
        if len(elements) > 0:
            self._write_package_folders([elements_dir])

        # Elements
        for element_name, element_type in elements.items():
            class_def = element_factory(
                element_name,
                element_type,
                schema.get_element_definition(element_name),
                self._config,
            )
            ElementGenerator._write(
                elements_dir +
                class_def.get_file_name(element_name) + '.py',
                str(class_def)
            )

    def generate(self):
        """Generate the classes based on our config.
        """
        config = self._config.load()
        for xsd_name in config.get_xsd_names():
            self.load_schema(xsd_name)
            config.set_xsd(xsd_name)
            cache.clear()
            self._generate_groups(xsd_name)
            self._generate_types(xsd_name)
            self._generate_elements(xsd_name)

    def generate_config(self):
        """Generate the config for our final class generation.
        """
        self.load_schema(self._xsd)
        self._schema.compile()
        self._write_config()

    @staticmethod
    def _write_package_folders(dirs):
        """Make sure the given directories exist as well as their __init__.py
        files.

        Args:
            dirs (list): A list of directories to confirm exist.
        """
        for my_dir in dirs:
            os.makedirs(my_dir, exist_ok=True)
            init = pathlib.Path(my_dir + '__init__.py')
            if not init.exists():
                init.touch()

    def _write_config(self):
        """Create and write the configuration.
        """
        # if config is None:
        config = self._config.load()
        config.set_xsd(self._xsd)
        config.clear_xsd()

        # Groups
        for name, group_type in cache.get_group_cache().items():
            config.add_group_config(name, group_type)

        # Types
        for name, node_type in cache.get_type_cache().items():
            config.add_type_config(name, node_type)

        # Elements
        for element_name, element_type in cache.get_element_cache():
            config.add_element_config(element_name, element_type)

        self._config.save()


if __name__ == "__main__":
    args = sys.argv
    generator = ElementGenerator(args[1])
    operation = args[2]

    if operation == 'config':
        generator.generate_config()
    elif operation == 'elements':
        generator.generate()
    else:
        print('Unknown operation!')
