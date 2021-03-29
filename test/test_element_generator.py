import pathlib
from xmlapigen.element_generator import ElementGenerator

if __name__ == '__main__':
  here = str(pathlib.Path(__file__).parent.parent)
  data_dir = here + '/_build/'

  ElementGenerator(
    data_dir,
    data_dir + 'config.yml'
 ).generate()