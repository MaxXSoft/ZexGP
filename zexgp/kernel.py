from config import ConfigManager
from tree import TreeManager
from define import GenMethod, SelectMethod, Operation
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
    self.__select_method = {
        'fitness': SelectMethod.FITNESS,
        'tournament': SelectMethod.TOURNAMENT,
    }
    self.__fit_func = None
    self.__quiet = False

  def __get_depth(self):
    return random.randint(self.__conf['minDepth'], self.__conf['maxDepth'])

  def __get_gen_method(self):
    return self.__gen_method.get(self.__conf['genMethod'], -1)

  def __get_select_method(self):
    return self.__select_method.get(self.__conf['selectMethod'], -1)

  def __get_op(self):
    w = [
      self.__conf['probCrossover'],
      self.__conf['probMutation'],
      self.__conf['probReproduction'],
    ]
    return random.choices(list(Operation), weights=w)[0]

  def __log(self, msg):
    if not self.__quiet:
      print(msg)

  def __select_tree(self, pop):
    '''
    Select top 2 individuals from specific population.
    '''
    method = self.__get_select_method()
    if method == SelectMethod.FITNESS:
      # get weights of each individuals
      sum = 0
      for _, f in pop:
        sum += f
      w = [i[1] / sum for i in pop]
      # random choice
      t1, _ = random.choices(pop, weights=w)[0]
      t2, _ = random.choices(pop, weights=w)[0]
      return t1, t2
    elif method == SelectMethod.TOURNAMENT:
      # get tournament
      size = self.__conf['tournamentSize']
      trees = [random.choice(pop) for _ in range(size)]
      trees.sort(key=lambda x: x[1], reverse=True)
      # return top 2 trees
      return trees[0][0], trees[1][0]
    else:
      raise RuntimeError('invalid selection method')

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
    fit_func: Callable[TreeNode, float]
      Fitness function, accepts an individual (tree) and returns fitness.
    '''
    self.__fit_func = fit_func

  def set_quiet(self, quiet):
    '''
    Set whether to enable quiet mode.
    '''
    self.__quiet = quiet

  def run(self):
    '''
    Run a genetic programming process.

    Return: List[TreeNode]
      Results of all runs.
    '''
    results = []
    for run in range(self.__conf['maxRuns']):
      self.__log(f'run {run} started')
      # initialize population
      pop = []
      for _ in range(self.__conf['populationSize']):
        tree = self.__tm.generate(self.__get_gen_method(),
                                  self.__get_depth())
        pop.append((tree, self.__fit_func(tree)))
      # perform GP
      for gen in range(self.__conf['maxGenerations']):
        # generate next generation
        next_pop = []
        for _ in range(len(pop)):
          # pick 2 individuals
          t1, t2 = self.__select_tree(pop)
          # perform operation
          op = self.__get_op()
          if op == Operation.CROSSOVER:
            tree = self.__tm.crossover(t1, t2)
          elif op == Operation.MUTATION:
            tree = t1.duplicate()
            self.__tm.mutate(tree, self.__get_gen_method(),
                             self.__get_depth())
          elif op == Operation.REPRODUCTION:
            tree = t1.duplicate()
          else:
            assert False
          # insert into population
          next_pop.append((tree, self.__fit_func(tree)))
        # update status
        pop = next_pop
        best = max(pop, key=lambda x: x[1])[1]
        worst = min(pop, key=lambda x: x[1])[1]
        self.__log(f'run: {run}, gen: {gen}, best: {best}, worst: {worst}')
      # update results
      results.append(max(pop, key=lambda x: x[1])[0])
    return results
