#!/usr/bin/ipython -pylab
#
# $Id: sugar.py,v 1.1 2010-01-22 18:46:50 wirawan Exp $
#
# Created: 20100121
# Wirawan Purwanto
#
# Syntactic sugar for python programming. May not be efficient, but many
# of these tools are nice for quick-and-dirty programming.
# Beware of their caveats!
#
#

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
