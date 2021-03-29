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


class ConfigGenerator():
    """Class responsible for generating xsd-based configuration and classes
    """

    def __init__(self, output, inputs):
        self._root = str(pathlib.Path(__file__).parent.parent)
        output = output if output is not None else '_build'

        self._output_dir = self._root + '/' + output

        if not os.path.exists(self._output_dir):
            os.mkdir(self._output_dir);

        self._inputs = inputs

        config_file = str(pathlib.Path(
            self._output_dir + '/config.yml'))

        self._config = Config(config_file)

    def load_schema(self, xsd):
        """Load the schema for the given xsd file.

        Args:
            xsd (str): The xsd file name without the extension.
        """
        self._schema = Schema(xsd)

    def generate_config(self):
        """Generate the config for our final class generation.
        """

        for inp in self._inputs:
          schema = Schema(inp)
          schema.compile()
          self._write_config(inp)

    def _write_config(self, xsd):
        """Create and write the configuration.
        """
        # if config is None:
        config = self._config.load()
        config.set_xsd(xsd)
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