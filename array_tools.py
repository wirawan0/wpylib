#
# Created: 20140207
# Wirawan Purwanto
#

"""
wpylib.array_tools

Various tools for arrays (mainly, numpy array objects).

"""


def array_indices_cond_1d(arr, cond):
  """Get the odered list of array indices whose corresponding elements satisfy
  a given condition.
  Useful for conditional assignment or evaluation.

  The input `cond' argument can be an ufunc-like function that evaluates
  a logical expression in bulk for each of the arr's element.
  Or it can be an array of logical values that has the same length as arr.

  Example use case:

     r = numpy.linspace(1.97, 3.5, num=150)
     i_select = cond_indices_1d(r, r <= 2.5)
     # ... then we can do something with r[i_select]
     # for conditional assignment or value extraction.
  """
  arr = numpy.asarray(arr)
  assert len(arr.shape) == 1

  if callable(cond):
    cond = cond(arr)
  # otherwise, assume cond is already a good array
  return numpy.array(xrange(len(arr)))[ cond ]




