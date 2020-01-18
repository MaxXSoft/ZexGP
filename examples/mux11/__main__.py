from zexgp.kernel import Kernel
from os import path


# some necessary global variables
lines = 0
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
  Fitness function.
  '''
  global lines
  lines = 0
  sum = 0
  while lines < 2048:
    if tree.eval() == table[lines]:
      sum += 1
    lines += 1
  return sum / 2048


def get_bit(index):
  '''
  Helper function of 
  '''
  return lambda: bool(lines & (1 << index))


# create kernel and load settings from disk
k = Kernel()
k.load_conf(path.dirname(__file__) + '/config.json')

# add functions
k.add('and', lambda x, y: x and y)
k.add('or', lambda x, y: x or y)
k.add('not', lambda x: not x)
k.add('if', lambda c, t, f: t if c else f)

# add terminals in a tricky way
for i in range(8):
  k.add(f'd{i}', get_bit(i))
for i in range(3):
  k.add(f'a{i}', get_bit(i + 8))

# set fitness function
k.set_fitness(fitness)

# run & print results
init_lut()
results = k.run()
for i in results:
  print(i)
