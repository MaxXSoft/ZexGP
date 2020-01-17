from config import ConfigManager
from tree import TreeManager


class Kernel:
  '''
  Core part of ZexGP. You can use 'Kernel' to run a GP process.
  '''

  def __init__(self):
    self.__conf = ConfigManager(default={
      'populationSize': 1000,
      'maxGenerations': 100,
      'maxRuns': 10,
      'probCrossover': 0.9,
      'probMutation': 0.1,
      'probLeafMutation': 0.5,
      'minScale': 10,
      'maxScale': 100,
      'minMutationScale': 5,
      'maxMutationScale': 50,
      'tournamentSize': 4,
    })
    self.__tm = TreeManager()
    self.__fit_func = None

  def load_conf(self, conf):
    '''
    Load configuration.

    Parameter
    -----
    conf: str
      Path of configuration file.
    '''
    with open(conf, 'r') as f:
      self.__conf.load(f)

  def dump_conf(self, conf):
    '''
    Store configuration.

    Parameter
    -----
    conf: str
      Path of configuration file.
    '''
    with open(conf, 'w') as f:
      self.__conf.dump(f)

  def add(self, name, func):
    '''
    Add function/terminal to kernel.
    '''
    self.__tm.add(name, func)

  def set_fitness(self, fit_func):
    '''
    Set fitness function of current kernel.

    Parameter
    -----
    fit_func: Callable[Any, float]
      Fitness function, accepts individual's output and returns fitness.
    '''
    self.__fit_func = fit_func

  def run(self):
    '''
    Run a genetic programming process.
    '''
    pass
