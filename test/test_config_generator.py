import pathlib
from xmlapigen.config_generator import ConfigGenerator

if __name__ == '__main__':
  here = str(pathlib.Path(__file__).parent.parent)
  data_dir = here + '/test/_data/'

  ConfigGenerator(
    None,
    [
      data_dir + 'compound.xsd',
      data_dir + 'index.xsd',
      data_dir + 'xml.xsd'
    ]
 ).generate_config()