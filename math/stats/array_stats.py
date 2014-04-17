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


PRINCIPLES

- Make sure functions are dimension-independent as much as possible
  (i.e. not limited to 1D or 2D only).
- Text output should not hardwired only to sys.stdout via vanilla print
  statement.
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
  """Returns the maximum *relative* absolute difference between two matrices.
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


def rdiff(M1, M2, ztol=1e-15, Abs=False):
  """Returns the *relative* [absolute] difference between two matrices.
  Used for checking whether two matrices are identical.
  Here, M1 is the array being compared, and M2 is the reference array.

  CAVEATS:
  - Zero elements in M2 (reference matrix) are converted to unity for
    calculating the relative difference.
  """
  from numpy import abs, array, asarray
  (mapprox, mref) = (M1, M2)
  if Abs:
    diff = abs(asarray(mapprox) - asarray(mref))
    mref0 = abs(asarray(mref))
    numpy.putmask(mref0, mref0 < ztol, [1.0])
  else:
    diff = asarray(mapprox) - asarray(mref)
    mref0 = array(mref, copy=True)  # must make a copy
    numpy.putmask(mref0, abs(mref0) < ztol, [1.0])

  return (diff / mref0)


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


def study_sparsity(M, binrange=(-16.5,6.5,1.0), kind='log10x', minzero=1e-30, args={}):
  # Adapted from V2b_inspect.py research module.
  """Study the distribution of values or sparsity of a given array, M,
  using histogram.

  Returns a tuple of length N; the first (N-2) elements are the
  histogram() output, while the last two are the number of elements
  whose values are smaller (greater) than the lower (upper) bound of
  the histogram bind range.

  Argument 'kind': By default, the 'x' values of the histogram is on
  logarithmic-10 scale.
  Other common log scales can be chosen using 'log2x' and 'logx'.
  Choose 'linx' if you want the linear scale instead.

  Argument 'binrange' can be one of the following:
  - 3-tuple: the left edge of the first bin, the right edge of the last bin,
    and the width of each bin
  - 2-tuple: the left MIDPOINT of the first bin, the right MIDPOINT
    of the last bin; the width is assumed to be 1.

  The defaults are a 3-tuple, intended for log10x scale, where
  we check order-of-magnitudes between 1e-16 and 1e+5 (roughly).
  """
  from numpy import abs, count_nonzero, arange, histogram, log10, log2, log
  if kind == 'log10x': # usual way, for broad view
    log_val = log10(abs(M.flatten()) + minzero)
  elif kind == 'log2x':
    log_val = log2(abs(M.flatten()) + minzero)
  elif kind == 'logx':
    log_val = log(abs(M.flatten()) + minzero)
  elif kind == 'linx': # linear x scale, usually for more detailed view
    log_val = abs(M.flatten())
  else:
    raise ValueError, "Invalid kind=%s" % (str(kind))
  if len(binrange) == 3:
    binedges = numpy.arange(*binrange)
  elif len(binrange) == 2:
    l = binrange[0]-0.5
    r = binrange[1]+0.5
    binedges = numpy.arange(l,r)
  else:
    raise ValueError, "Invalid binrange parameter value"
  #print binedges
  hist = histogram(log_val, bins=binedges, **args)
  # Count values outside the range being considered:
  l = 0
  r = 0
  llim = binedges[0]
  rlim = binedges[-1]
  l = count_nonzero(log_val < llim)
  r = count_nonzero(log_val > rlim)
  return hist + (l,r)


def print_histogram(hist, xaxis='midpt',
                    # output formatting
                    xwidth=3, xprec=0,
                    out=sys.stdout):
  # Adapted from V2b_inspect.py research module.
  """Prints histogram in an easier way to visualize in text fashion.
  """
  if len(hist) >= 4:
    # special case: for study_sparsity output.
    (bar,edges,lexcess,rexcess) = hist
  else:
    # for all other cases--
    (bar,edges) = hist[:2]
    lexcess = 0
    rexcess = 0
  if xaxis == 'midpt':
    midpt = (edges[1:] + edges[:-1]) * 0.5
  elif xaxis == 'leftpt':
    midpt = edges[:-1]
  elif xaxis == 'rightpt':
    midpt = edges[1:]
  else:
    raise ValueError, "Invalid xaxis parameter value"
  width = max(int(numpy.log10(max(bar.max(), lexcess, rexcess))+1), xwidth)
  #print "width = %d" % width
  barfmt = " %" + str(width) + "d"
  midfmt = " %" + str(width) + "." + str(xprec) + "f"
  if out == str:
    from StringIO import StringIO
    out = StringIO()
    def retval():
      return out.getvalue()
  else:
    def retval():
      return None

  def Print(x):
    out.write(x)

  out.write((barfmt % lexcess) \
            + "".join([ barfmt % i for i in bar ]) \
            + (barfmt % rexcess) \
            + "\n")
  out.write(" " * width + "<" \
            + "".join([ midfmt % i for i in midpt ]) \
            + " " * width + ">" \
            + "\n")

  return retval()



