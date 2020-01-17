from inspect import signature
import random
from copy import deepcopy


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

  def invoke(self):
    '''
    Invoke current GP-tree recursively.
    '''
    args = [i.invoke() for i in self.__args]
    return self.__func(*args)

  def dumps(self):
    '''
    Dump current GP-tree to string.
    '''
    args = [i.dumps() for i in self.__args]
    if args:
      return '({} {})'.format(self.__name, ' '.join(args))
    else:
      return self.__name

  def generate(self, callback):
    '''
    Generate child nodes in BFS way.

    Parameters
    -----
    callback: Callable[[], Optional[TreeNode]]
      Function that randomly returns a function/terminal node.
      Generation will stop if callback returns None.
    '''
    # TODO: try to generate an unbalanced tree?
    q = [self]
    while q:
      top = q.pop(0)
      for i in range(len(top.__args)):
        top.__args[i] = callback()
        if top.__args[i]:
          q.append(top.__args[i])

  def trim(self, callback):
    '''
    Replace all non-terminal leaf nodes with terminals.

    Parameters
    -----
    callback: Callable[[], TreeNode]
      Function that returns a new terminal node.
    '''
    # check if current node needs to be replaced
    trim_flag = False
    for i in self.__args:
      if not i:
        trim_flag = True
        break
    # recursively replace
    if trim_flag:
      node = callback()
      self.__name = node.__name
      self.__func = node.__func
      self.__args = node.__args
    else:
      for i in self.__args:
        i.trim(callback)

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

  def __pick_func(self):
    return random.choice(list(self.__funcs.items()))

  def __pick_term(self):
    return random.choice(list(self.__terms.items()))

  def add(self, name, func):
    '''
    Add an user defined function to current tree.
    '''
    sig = signature(func)
    if len(sig.parameters) >= 1:
      self.__funcs[name] = func
    else:
      self.__terms[name] = func

  def generate(self, scale):
    '''
    Generate a new tree randomly.

    Parameters
    -----
    scale: int
      Scale of generated tree.
    '''
    def gen_node():
      nonlocal scale
      if scale <= 0:
        return None
      else:
        scale -= 1
        return TreeNode(*self.__pick_func())

    assert scale > 0
    assert len(self.__funcs) > 0 and len(self.__terms) > 0
    tree = gen_node()
    tree.generate(gen_node)
    tree.trim(lambda: TreeNode(*self.__pick_term()))
    return tree

  def mutate(self, tree, scale):
    '''
    Perform mutation on a specific tree.

    Parameters
    -----
    tree: TreeNode
      The specific tree.
    scale: int
      Scale of generated subtree.
    '''
    def gen_node():
      nonlocal scale
      if scale <= 0:
        return None
      else:
        scale -= 1
        return TreeNode(*self.__pick_func())

    assert scale > 0
    assert len(self.__funcs) > 0 and len(self.__terms) > 0
    sub, _ = tree.select()
    if not len(sub):
      sub.set_func(*self.__pick_func())
    sub.generate(gen_node)
    sub.trim(lambda: TreeNode(*self.__pick_term()))

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
  tree = tm.generate(random.randint(10, 30))
  print('original tree:')
  print(tree)
  print('=>', tree.invoke())
  t = tree.duplicate()
  tm.mutate(tree, random.randint(2, 10))
  print('mutated tree:')
  print(tree)
  print('=>', tree.invoke())
  print('hybridized tree:')
  ht = tm.crossover(t, tree)
  print(ht)
  print('=>', ht.invoke())
