'''
An example of using ZexGP to solve the Boolean 11-multiplexer problem.
'''

from zexgp.kernel import Kernel
from os import path


# some necessary global variables
table = []


def init_lut():
  '''
  Initialize look up table.
  '''
  for i in range(2048):
    addr = (i >> 8) & 0b111
    data = i & 0xff
    table.append(bool(data & (1 << addr)))


def fitness(tree):
  '''
  Fitness function. Thread-safe required.
  '''
  sum = 0
  for l in range(2048):
    args = (bool(l & (1 << i)) for i in range(11))
    if tree.eval(*args) == table[l]:
      sum += 1
  return sum / 2048


# create kernel and load settings from disk
k = Kernel()
k.load_conf(path.dirname(__file__) + '/config.json')

# add functions
k.add('and', func=lambda x, y: x and y)
k.add('or', func=lambda x, y: x or y)
k.add('not', func=lambda x: not x)
k.add('if', func=lambda c, t, f: t if c else f)

# add terminals
for i in range(8):
  k.add(f'd{i}', arg_index=i)
for i in range(3):
  k.add(f'a{i}', arg_index=i + 8)

# set fitness function
k.set_fitness(fitness)

# run & print results
init_lut()
results = k.run(jobs=4)
for i in results:
  print(i)
