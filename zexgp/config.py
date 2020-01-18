import json


class ConfigManager:
  '''
  'ConfigManager' stores all configurations of program.
  '''

  def __init__(self, default=None):
    self.__config = default if isinstance(default, dict) else {}

  def __getitem__(self, key):
    return self.__config[key]

  def __setitem__(self, key, value):
    self.__config[key] = value

  def load(self, f):
    '''
    Load configuration from file.
    '''
    self.__config = json.load(f)
    if not isinstance(self.__config, dict):
      raise RuntimeError('invalid configuration file')

  def dump(self, f):
    '''
    Store configuration to file.
    '''
    json.dump(self.__config, f)
