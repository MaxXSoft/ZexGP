from inspect import signature
import random
from copy import deepcopy
from zexgp.define import GenMethod


class TreeNode:
  '''
  Single node of GP-tree, can be either a function or a terminal.

  It's not safe to access the same 'TreeNode' in two threads.

  Parameters
  -----
  name: str
    Name of node.
  func: Optional[Callable[..., Any]]
    If not 'None', it'll be called when evaluating.
  arg_index: Optional[int]
    If not 'None', the specific argument will be returned when evaluating.
  '''

  def __init__(self, name, func=None, arg_index=None):
    self.reset(name, func, arg_index)

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

  def reset(self, name, func, arg_index):
    '''
    Reset current node.
    '''
    if func:
      self.__name = name
      self.__func = func
      self.__arg_index = None
      self.__reset_args()
    elif arg_index is not None:
      self.__name = name
      self.__func = None
      self.__arg_index = arg_index
      self.__args = []
    else:
      raise RuntimeError('both "func" and "arg_index" are None')

  def eval(self, *args):
    '''
    Evaluate current GP-tree recursively.
    '''
    if self.__arg_index is not None:
      return args[self.__arg_index]
    else:
      nodes = [i.eval(*args) for i in self.__args]
      return self.__func(*nodes)

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
        self.__arg_index = tree.__arg_index
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
    name, (func, index) = random.choice(list(self.__funcs.items()) +
                                        list(self.__terms.items()))
    return name, func, index

  def __pick_func(self):
    name, (func, index) = random.choice(list(self.__funcs.items()))
    return name, func, index

  def __pick_term(self):
    name, (func, index) = random.choice(list(self.__terms.items()))
    return name, func, index

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

  def add(self, name, func=None, arg_index=None):
    '''
    Add an user defined function or argument reference to current tree.

    Parameters
    -----
    name: str
      Name of function/reference.
    func: Optional[Callable[..., Any]]
      User defined function.
    arg_index: Optional[int]
      Index of argument refernce if not 'None'.
    '''
    if arg_index is not None:
      self.__terms[name] = (None, arg_index)
    else:
      sig = signature(func)
      if len(sig.parameters) >= 1:
        self.__funcs[name] = (func, None)
      else:
        self.__terms[name] = (func, None)

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
      sub.reset(*self.__pick_func())
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
  tm.add('x', arg_index=0)
  tree = tm.generate(GenMethod.GROW, random.randint(2, 10))
  print('original tree:')
  print(tree)
  print('=>', tree.eval(1))
  t = tree.duplicate()
  tm.mutate(tree, GenMethod.GROW, random.randint(2, 10))
  print('mutated tree:')
  print(tree)
  print('=>', tree.eval(1))
  print('hybridized tree:')
  ht = tm.crossover(t, tree)
  print(ht)
  print('=>', ht.eval(1))
