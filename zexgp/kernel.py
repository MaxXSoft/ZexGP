from zexgp.config import ConfigManager
from zexgp.tree import TreeManager
from zexgp.define import GenMethod, SelectMethod, Operation
from zexgp.thread import SubRun
import random


class Kernel:
  '''
  Core part of ZexGP. You can use 'Kernel' to run a GP process.
  '''

  def __init__(self):
    self.__conf = ConfigManager(default={
      'populationSize': 1000,
      'maxGenerations': 100,
      'maxRuns': 10,
      'probCrossover': 0.8,
      'probMutation': 0.1,
      'probReproduction': 0.1,
      'minDepth': 2,
      'maxDepth': 10,
      'genMethod': 'grow',
      'selectMethod': 'tournament',
      'tournamentSize': 10,
    })
    self.__tm = TreeManager()
    self.__gen_method = {
      'grow': GenMethod.GROW,
      'full': GenMethod.FULL,
    }
    self.__fit_func = None
    self.__quiet = False

  def __get_depth(self):
    return random.randint(self.__conf['minDepth'], self.__conf['maxDepth'])

  def __get_gen_method(self):
    return self.__gen_method.get(self.__conf['genMethod'], -1)

  def __log(self, msg):
    if not self.__quiet:
      print(msg)

  def __run_single(self, run, jobs):
    '''
    Perform a single run.

    Parameters
    -----
    run: int
      Id of current run.
    jobs: int
      Thread count.

    Return: TreeNode
      Best result.
    '''
    # initialize population
    pop = []
    for _ in range(self.__conf['populationSize']):
      tree = self.__tm.generate(self.__get_gen_method(),
                                self.__get_depth())
      pop.append((tree, self.__fit_func(tree)))
    # perform GP
    for gen in range(self.__conf['maxGenerations']):
      # generate next generation
      subs = []
      sizes = [len(pop) // jobs] * (jobs - 1)
      sizes.append(len(pop) - (len(pop) // jobs * (jobs - 1)))
      for i in sizes:
        assert i
        sub = SubRun(self.__conf, self.__tm, self.__fit_func, pop, i)
        sub.start()
        subs.append(sub)
      next_pop = []
      for s in subs:
        s.join()
        next_pop += s.next_pop
      # update status
      pop = next_pop
      best = max(pop, key=lambda x: x[1])[1]
      worst = min(pop, key=lambda x: x[1])[1]
      self.__log(f'run: {run}, gen: {gen}, best: {best}, worst: {worst}')
    return max(pop, key=lambda x: x[1])[0]

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

  def add(self, name, func=None, arg_index=None):
    '''
    Add function, terminal or argument reference to kernel.

    Parameters
    -----
    name: str
      Name of function/reference.
    func: Optional[Callable[..., Any]]
      User defined function.
    arg_index: Optional[int]
      Index of argument refernce if not 'None'.
    '''
    self.__tm.add(name, func, arg_index)

  def set_fitness(self, fit_func):
    '''
    Set fitness function of current kernel.

    NOTE: fitness function must be thread-safe!

    Parameter
    -----
    fit_func: Callable[[TreeNode], float]
      Fitness function, accepts an individual (tree) and returns fitness.
    '''
    self.__fit_func = fit_func

  def set_quiet(self, quiet):
    '''
    Set whether to enable quiet mode.
    '''
    self.__quiet = quiet

  def run(self, jobs=1):
    '''
    Run a genetic programming process.

    Parameters
    -----
    jobs: int
      Thread count in one generation.

    Return: List[Optional[TreeNode]]
      Results of all runs.
    '''
    results = []
    for run in range(self.__conf['maxRuns']):
      self.__log(f'run {run} started')
      # update results
      try:
        results.append(self.__run_single(run, jobs))
      except KeyboardInterrupt:
        self.__log(f'run {run} terminated')
        results.append(None)
    return results
