from threading import Thread
from zexgp.define import GenMethod, SelectMethod, Operation
import random


class SubRun(Thread):
  '''
  Thread object of GP kernel. For one-time use only.

  Each 'SubRun' can run part of the generation process.

  Parameters
  -----
  conf: ConfigManager
    'ConfigManager' in kernel, shared by all threads.
  tm: TreeManager
    'TreeManager' in kernel, shared by all threads.
  fit: Callable[[TreeNode], float]
    Fitness function.
  pop: List[Tuple[TreeNode, float]]
    Current population list.
  size: int
    Size of generated population list.
  '''

  def __init__(self, conf, tm, fit, pop, size):
    Thread.__init__(self)
    self.__conf = conf
    self.__tm = tm
    self.__fit = fit
    self.__pop = pop
    self.__size = size
    self.__next_pop = []
    self.__gen_method = {
      'grow': GenMethod.GROW,
      'full': GenMethod.FULL,
    }
    self.__select_method = {
      'fitness': SelectMethod.FITNESS,
      'tournament': SelectMethod.TOURNAMENT,
    }

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

  def __select_tree(self, pop):
    '''
    Select top 2 individuals from specific population.
    '''
    method = self.__get_select_method()
    if method == SelectMethod.FITNESS:
      # get weights of each individuals
      w = [i[1] for i in pop]
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

  @property
  def next_pop(self):
    '''
    Generated population list.

    Returns: List[Tuple[TreeNode, float]]
    '''
    return self.__next_pop

  def run(self):
    for _ in range(self.__size):
      # pick 2 individuals
      t1, t2 = self.__select_tree(self.__pop)
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
      self.__next_pop.append((tree, self.__fit(tree)))
