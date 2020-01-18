'''
An example of fitting a function with ZexGP.
'''

from zexgp.kernel import Kernel
from os import path
from sys import float_info as fi


# some necessary global variables
func_val = []


def init_func_val():
  '''
  Initialize function value.
  '''
  def func(x): return 1 / (1 + 25 * x ** 2)
  for i in range(100):
    x = (i - 50) / 50
    func_val.append(func(x))


def get_int(i):
  '''
  Get a function that returns a specific integer.
  '''
  return lambda: i


def pow(x, y):
  try:
    return float(x ** y)
  except (OverflowError, ZeroDivisionError):
    return fi.max
  except TypeError:
    return float('nan')


def fitness(tree):
  '''
  Fitness function.
  '''
  sum = 0
  for i in range(100):
    x = (i - 50) / 50
    ans = tree.eval(x)
    exp = func_val[i]
    sum += abs(ans - exp)
  return 1 / (sum + 1) if sum == sum else 0


# create kernel and load settings from disk
k = Kernel()
k.load_conf(path.dirname(__file__) + '/config.json')

# add functions
k.add('+', func=lambda x, y: x + y)
k.add('-', func=lambda x, y: x - y)
k.add('*', func=lambda x, y: x * y)
k.add('/', func=lambda x, y: x / y if y else fi.max)
k.add('^', func=pow)

# add terminals
k.add('x', arg_index=0)
for i in range(1, 4):
  k.add(str(i), func=get_int(i))

# set fitness function
k.set_fitness(fitness)

# run & print results
init_func_val()
results = k.run(jobs=4)
for i in results:
  print(i)
