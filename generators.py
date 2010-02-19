# -*- python -*-
#
# $Id: generators.py,v 1.1 2010-02-19 18:41:28 wirawan Exp $
#
# Created: 20100218
# Wirawan Purwanto
#
"""

Various generators

"""

def all_combinations(seq):
  """Generates stream of tuples containing all possible
  combinations of items (where order matters).

  This is useful e.g. for generating all possible indices for a multidimensional
  array.
  Example:
  >>> for i in all_combinations((xrange(4), xrange(3))): print i
  (0, 0)
  (1, 0)
  (2, 0)
  (3, 0)
  (0, 1)
  (1, 1)
  (2, 1)
  (3, 1)
  (0, 2)
  (1, 2)
  (2, 2)
  (3, 2)

  """
  if len(seq) <= 1:
    for i in seq[0]:
      yield (i,)
  else:
    for s1 in all_combinations(seq[1:]):
      for s0 in seq[0]:
        yield (s0,) + s1

