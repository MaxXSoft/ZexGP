from enum import Enum, unique


@unique
class GenMethod(Enum):
  '''
  Generation method of GP-tree.
  '''
  GROW = 0
  FULL = 1


@unique
class SelectMethod(Enum):
  '''
  Selection method during GP process.
  '''
  FITNESS = 0
  TOURNAMENT = 1
