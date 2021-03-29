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

import os
import argparse

if __name__ == "__main__":
  parser = argparse.ArgumentParser(prog='xmlapigen', description="Generate an xml API from xsd files")

  subparsers = parser.add_subparsers(help='sub-command help')

  config_parser = subparsers.add_parser('config', help='Generate configuration')
  config_parser.add_argument('output_dir', nargs='?', default='_build', help='The directory where generated output will reside')
  config_parser.add_argument('input', nargs='+', help='One or more xsd files to generate APIs for.')

  element_parser = subparsers.add_parser('elements', help='Generate elements from configuration')
  element_parser.add_argument('-c', '--config', help="The configuration file to generate elements from")

  args = parser.parse_args()

  #generator = ElementGenerator(args[1])
  #operation = args[2]

  #if operation == 'config':
  #    generator.generate_config()
  #elif operation == 'elements':
  #    generator.generate()
  #else:
  #    print('Unknown operation!')
