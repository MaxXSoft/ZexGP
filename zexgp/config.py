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

  def __getattr__(self, name):
    return self.__config[name]

  def __setattr__(self, name: str, value):
    if name.startswith('_' + self.__class__.__name__):
      super().__setattr__(name, value)
    else:
      self.__config[name] = value

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
