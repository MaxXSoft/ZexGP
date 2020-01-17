from inspect import signature
import random


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


if __name__ == '__main__':
  tm = TreeManager()
  tm.add('+', lambda x, y: x + y)
  tm.add('-', lambda x, y: x - y)
  tm.add('*', lambda x, y: x * y)
  tm.add('/', lambda x, y: x / y)
  tm.add('1', lambda: 1)
  tm.add('2', lambda: 2)
  tm.add('3', lambda: 3)
  tree = tm.generate(random.randint(10, 30))
  print(tree.dumps())
  print(tree.invoke())
