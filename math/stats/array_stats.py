# $Id: __init__.py,v 1.1 2010-10-07 15:57:29 wirawan Exp $
#
# wpylib.math.stats.array_stats module
# Created: 20140404
# Wirawan Purwanto
#

"""
wpylib.math.stats.array_stats module
Tools for studying the statistics of an array, the difference of
two or more arrays, etc.

"""

import os
import sys
import numpy


# Functions below were imported from V2b_inspect.py, 20140404

"""
CONVENTIONS

- Usually, M1 is the matrix under examination, M2 is the reference matrix.
"""

def report_diff_stat(M1, M2, out=sys.stdout):
  # Original function name: statdiff
  """Studies the difference of two arrays (or matrices).
  Usually, M1 is the matrix under examination, M2 is the reference
  matrix.
  Prints out standard report to a given text file, or returns
  the report as a string.
  """
  dM = M1 - M2
  if len(M1.shape) == 2:
    dM_diag = numpy.diagonal(dM)
    stats = (
      dM.max(),
      dM.min(),
      dM.mean(),
      numpy.abs(dM).mean(),
      rms(dM),
      dM_diag.max(),
      dM_diag.min(),
      dM_diag.mean(),
      numpy.abs(dM_diag).mean(),
      rms(dM_diag),
    )
    if out == tuple:
      return stats

    rslt = """\
- max difference  = %13.6e
- min difference  = %13.6e
- mean difference = %13.6e
- mean abs diff   = %13.6e
- rms difference  = %13.6e
- max difference  = %13.6e   on diagonal
- min difference  = %13.6e   on diagonal
- mean difference = %13.6e   on diagonal
- mean abs diff   = %13.6e   on diagonal
- rms difference  = %13.6e   on diagonal
""" % stats
  else:
    stats = (
      dM.max(),
      dM.min(),
      dM.mean(),
      numpy.abs(dM).mean(),
      rms(dM),
    )
    if out == tuple:
      return stats

    rslt = """\
- max difference  = %13.6e
- min difference  = %13.6e
- mean difference = %13.6e
- mean abs diff   = %13.6e
- rms difference  = %13.6e
""" % stats

  if out == str:
    return rslt
  else:
    out.write(rslt)
    out.flush()


def maxadiff(M1, M2):
  # Original function name: maxdiff
  """Returns the maximum absolute difference between two matrices.
  Used for checking whether two matrices are identical."""
  return numpy.abs(M1 - M2).max()


def maxadiff_by_col(M1, M2):
  # Original function name: maxdiff_by_col
  """Assuming two-dimensional array (where first index is the row
  index), computes the maximum absolute difference.
  """
  return numpy.abs(M1 - M2).max(axis=0)


def maxradiff(M1, M2, ztol=1e-15):
  # Original function name: maxrdiff
  """Prints the maximum *relative* absolute difference between two matrices.
  Used for checking whether two matrices are identical.

  CAVEATS:
  - Zero elements in M2 (reference matrix) are converted to unity for
    calculating the relative difference.
  """
  (mapprox, mref) = (M1, M2)
  diff = numpy.asarray(numpy.abs(mapprox - mref))
  mref0 = numpy.asarray(numpy.abs(mref))
  numpy.putmask(mref0, mref0 < ztol, [1.0])
  
  return (diff / mref0).max()


class ArrayStat(object):
  """A class to compute the statistics of an array.
  """
  def __init__(self, mat, save=False):
    mat = numpy.asarray(mat)
    amat = numpy.abs(mat)
    if save:
      self.mat = mat
    self.min = mat.min()
    self.max = mat.max()
    self.mean = mat.mean()
    self.amin = amat.min()
    self.amax = amat.max()
    self.amean = amat.mean()
    self.rms = numpy.sqrt(numpy.sum(amat**2) / amat.size)

  def report(self, out=sys.stdout):
    """Prints out a standard report.
    """
    #print_histogram(study_sparsity(self.diff, (log_delta-5.5,log_delta+4.5+0.1)), xaxis='left_edge')
    rslt = """\
. min       = %12.6g
. max       = %12.6g
. mean      = %12.6g
. absmin    = %12.6g
. absmax    = %12.6g
. absmean   = %12.6g
. rms       = %12.6g
""" % (self.min, self.max, self.mean,
       self.amin, self.amax, self.amean,
       self.rms)

    if out == str:
      return rslt
    else:
      out.write(rslt)
      out.flush()
