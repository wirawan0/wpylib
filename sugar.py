#!/usr/bin/ipython -pylab
#
# $Id: sugar.py,v 1.2 2010-02-08 19:58:44 wirawan Exp $
#
# Created: 20100121
# Wirawan Purwanto
#
# Syntactic sugar for python programming. May not be efficient, but many
# of these tools are nice for quick-and-dirty programming.
# Beware of their caveats!
#
#
import sys

def ifelse(cond, trueval, *args):
  """An alternative to python's own ternary operator, but with multiple
  conditions to test (like chained if-else-if-else... which is found in
  e.g. m4 language).
  This is of course only a syntactic sugar with its inefficiency and
  dangers (all expressions are evaluated before choosing which one is to
  select). So, beware!"""
  if cond:
    return trueval
  else:
    i = 0
    while i+1 < len(args):
      if args[i]: return args[i+1]
      i += 2

    if i < len(args): return args[i]

  return None # Fallback solution: "None"


if sys.version_info < (2,4):
  def sorted(List):
    rslt = [ L for L in List ] # == L.copy()
    rslt.sort()
    return rslt
else:
  #print dir(globals())
  sorted = sorted

#print dir(globals())

def dict_slice(Dict, *keys):
  """Returns a shallow copy of the subset of a given dict (or an otherwise
  hashable object) with a given set of keys.

  Example: if d = {'abc': 12, 'def': 7, 'ghi': 32, 'jkl': 98 }
  then dict_slice(d, 'abc', 'ghi') will yield {'abc': 12, 'ghi': 32 }
  """
  return dict([ (k, Dict[k]) for k in keys ])

