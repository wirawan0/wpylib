# $Id: text_tools.py,v 1.1 2009-12-04 19:57:22 wirawan Exp $
#
# Created: 20091204
# Wirawan Purwanto
#
# Simple and dirty text tools
#

import numpy

def make_matrix(Str, debug=None):
  """Simple tool to convert a string like
    '''1 2 3
    4 5 6
    7 8 9'''
  into a numpy matrix (or, actually, an array object).
  This is for convenience in programming quick scripts, much like octave matrix
  format (but without the evaluation of math expressions that octave has,
  of course)."""
  if isinstance(Str, numpy.matrix):
    return numpy.array(Str)
  elif isinstance(Str, numpy.ndarray):
    if len(Str.shape) == 2:
      return Str.copy()
    else:
      raise ValueError, "Cannot make matrix out of non-2D array"
  Str2 = ";".join([ row.rstrip().rstrip(";") for row in Str.split("\n") if row.strip() != "" ])
  rslt = numpy.matrix(Str2)
  if debug: print rslt
  return numpy.array(rslt)

