from inspect import signature
import random
from copy import deepcopy
from zexgp.define import GenMethod


class TreeNode:
  '''
  Single node of GP-tree, can be either a function or a terminal.
  '''

  def __init__(self, name, func):
    self.set_func(name, func)

  def __reset_args(self):
    self.__args = [None] * len(signature(self.__func).parameters)

  def __getitem__(self, index):
    return self.__args[index]

  def __setitem__(self, index, value):
    assert isinstance(value, TreeNode)
    self.__args[index] = value

  def __len__(self):
    return len(self.__args)

  def __str__(self):
    return self.dumps()

  def __repr__(self):
    return self.dumps()

  def set_func(self, name, func):
    '''
    Reset node name and function.
    '''
    self.__name = name
    self.__func = func
    self.__reset_args()

  def eval(self):
    '''
    Evaluate current GP-tree recursively.
    '''
    args = [i.eval() for i in self.__args]
    return self.__func(*args)

  def dumps(self):
    '''
    Dump current GP-tree to string.
    '''
    args = [i.dumps() for i in self.__args]
    if args:
      return f'({self.__name} {" ".join(args)})'
    else:
      return self.__name

  def grow_gen(self, depth, node_gen, term_gen):
    '''
    Generate child nodes recursively using 'grow' method.

    Parameters
    -----
    depth: int
      Maximum depth of generated tree.
    node_gen: Callable[[], TreeNode]
      Function that randomly returns a new function/terminal node.
    term_gen: Callable[[], TreeNode]
      Function that randomly returns a new terminal node.
    '''
    for i in range(len(self.__args)):
      if depth:
        self.__args[i] = node_gen()
        self.__args[i].grow_gen(depth - 1, node_gen, term_gen)
      else:
        self.__args[i] = term_gen()

  def full_gen(self, depth, func_gen, term_gen):
    '''
    Generate child nodes recursively using 'full' method.

    Parameters
    -----
    depth: int
      Maximum depth of generated tree.
    func_gen: Callable[[], TreeNode]
      Function that randomly returns a new function node.
    term_gen: Callable[[], TreeNode]
      Function that randomly returns a new terminal node.
    '''
    for i in range(len(self.__args)):
      if depth:
        self.__args[i] = func_gen()
        self.__args[i].full_gen(depth - 1, func_gen, term_gen)
      else:
        self.__args[i] = term_gen()

  def select(self, depth=0):
    '''
    Select a subtree randomly.

    Return: Tuple[Optional[TreeNode], int]
      Selected subtree and its depth.
    '''
    if self.__args:
      node, d = random.choice(self.__args).select(depth + 1)
      if d == depth:
        return (self, d)
      else:
        return (node, d)
    else:
      d = random.randint(0, depth - 1) + 1
      if d == depth:
        return (self, d)
      else:
        return (None, d)

  def replace(self, tree, depth=0):
    '''
    Replace a random child node with a specific tree.
    '''
    if self.__args:
      d = random.choice(self.__args).replace(tree, depth + 1)
      if d == depth:
        self.__name = tree.__name
        self.__func = tree.__func
        self.__args = deepcopy(tree.__args)
    else:
      d = random.randint(0, depth - 1) + 1
    return d

  def duplicate(self):
    '''
    Return a copy of current tree.
    '''
    return deepcopy(self)


class TreeManager:
  '''
  'TreeManager' manages all user defined functions/terminals
  and can generate a random tree for GP.
  '''

  def __init__(self):
    # all functions (with at least 1 argument)
    self.__funcs = {}
    # all terminals (with no argument)
    self.__terms = {}

  def __pick_all(self):
    return random.choice(list(self.__funcs.items()) +
                         list(self.__terms.items()))

  def __pick_func(self):
    return random.choice(list(self.__funcs.items()))

  def __pick_term(self):
    return random.choice(list(self.__terms.items()))

  def __tree_gen(self, tree, method, depth):
    assert depth > 0
    assert len(self.__funcs) > 0 and len(self.__terms) > 0
    node_gen = lambda: TreeNode(*self.__pick_all())
    func_gen = lambda: TreeNode(*self.__pick_func())
    term_gen = lambda: TreeNode(*self.__pick_term())
    if method == GenMethod.GROW:
      tree.grow_gen(depth, node_gen, term_gen)
    elif method == GenMethod.FULL:
      tree.full_gen(depth, func_gen, term_gen)
    else:
      raise RuntimeError('invalid generation method')

  def add(self, name, func):
    '''
    Add an user defined function to current tree.
    '''
    sig = signature(func)
    if len(sig.parameters) >= 1:
      self.__funcs[name] = func
    else:
      self.__terms[name] = func

  def generate(self, method, depth):
    '''
    Generate a new tree randomly using specific method.

    Parameters
    -----
    method: GenMethod
      Generation method.
    depth: int
      Maximum depth of generated tree.
    '''
    tree = TreeNode(*self.__pick_func())
    self.__tree_gen(tree, method, depth)
    return tree

  def mutate(self, tree, method, depth):
    '''
    Perform mutation on a specific tree.

    Parameters
    -----
    tree: TreeNode
      The specific tree.
    method: GenMethod
      Method of subtree generation.
    depth: int
      Maximum depth of generated subtree.
    '''
    sub, _ = tree.select()
    if not len(sub):
      sub.set_func(*self.__pick_func())
    self.__tree_gen(sub, method, depth)

  def crossover(self, tree1, tree2):
    '''
    Perform a recombination between two specific trees.
    '''
    tree = tree1.duplicate()
    tree.replace(tree2.select()[0])
    return tree


if __name__ == '__main__':
  import sys
  tm = TreeManager()
  tm.add('+', lambda x, y: x + y)
  tm.add('-', lambda x, y: x - y)
  tm.add('*', lambda x, y: x * y)
  tm.add('/', lambda x, y: x / y if y else x / sys.float_info.min)
  tm.add('1', lambda: 1)
  tm.add('2', lambda: 2)
  tm.add('3', lambda: 3)
  tree = tm.generate(GenMethod.GROW, random.randint(2, 10))
  print('original tree:')
  print(tree)
  print('=>', tree.eval())
  t = tree.duplicate()
  tm.mutate(tree, GenMethod.GROW, random.randint(2, 10))
  print('mutated tree:')
  print(tree)
  print('=>', tree.eval())
  print('hybridized tree:')
  ht = tm.crossover(t, tree)
  print(ht)
  print('=>', ht.eval())
