# Always prefer setuptools over distutils
from setuptools import setup, find_packages
import pathlib

here = pathlib.Path(__file__).parent.resolve()

# Get the long description from the README file
long_description = (here / 'README.rst').read_text(encoding='utf-8')

setup(
  name='xmlapigen',
  description='Generate xml apis from xsd files',
  url='https://github.com/cobhimself/xmlapigen',
  long_description=long_description,
  long_description_content_type='text/x-rst',
  author='Collin D. Brooks',
  author_email='collin.brooks@gmail.com',
  license='MIT',
  keywords='xml, parser',
  packages=find_packages(),
  python_requires='>=3.5, <4',
  install_requires=[],
  classifiers = [
    'Development Status :: 1 - Planning',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: MIT License',
    'Natural Language :: English',
    'Operating System :: OS Independent',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: Implementation :: Stackless',
    'Topic :: Documentation',
    'Topic :: Software Development :: Documentation',
    'Topic :: Software Development :: Libraries',
    'Topic :: Utilities'
  ],
  setup_requires=['setuptools_scm'],
  use_scm_version=True
)