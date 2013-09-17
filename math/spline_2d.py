# $Id: spline_2d.py,v 1.1 2010-01-22 18:48:19 wirawan Exp $
#
# wpylib.math.spline_2d module
# Created: 20091204
# Wirawan Purwanto
#

import numpy
import scipy.interpolate

class spline_2d:
  """Simple interpolation for two-dimensional curve.
  Created to handle the quirks of current SciPy interpolation
  routines."""
  # Important notes on spline CAVEATS:
  # - for some reason we HAVE to make a copy of the 'x' array
  #   (to make it contiguous, probably?)
  # - also, the x values better be sorted in ascending order, or else
  #   the routine would return nonsense (i.e. NaN's).
  def __init__(self, x, y):
    self.init(x,y)

  def init(self, x, y):
    # First, the x must be sorted, so we make a private copy of
    # the data:
    self.data = numpy.array(zip(x, y), dtype=[('x', float), ('y', float)])
    # Quirk 1: The x axis data must be sorted ascending
    self.data.sort(order=['x'])
    self.x = self.data['x']
    self.y = self.data['y']
    # Quirk 2: the x data for spline function must be contiguous
    # See below in init_spline_params()
    #self.x_copy = self.x.copy()

    try:
      del self.spline_params
    except:
      pass

  def init_spline_params(self):
    """Initialize spline params with default params.
    You can call something to initialize the spline params before
    calling the first spline function if you want different, non-default
    parameters."""
    self.spline_params \
      = scipy.interpolate.splrep(self.x, self.y, s=0)

  def spline(self, xnew):
    try:
      params = self.spline_params
    except:
      self.init_spline_params()
    return scipy.interpolate.splev(x=xnew, tck=self.spline_params, der=0)



class spline_2d_piecewise:
  """Simple spline_2d interpolator with piecewise datasets.
  Interpolation is possible only in the ranges defined by the piecewise
  datasets.
  No checking is done whether the pieces are overlapping, discontinuous, etc.
  The first piece found enclosing the coordinate will be taken for
  interpolation."""
  def __init__(self, *datasets):
    self.init(*datasets)

  def init(self, *datasets):
    #if len(dsets) % 2:
    #  raise ValueError, "The input datasets must be given in x, y pairs
    self.pieces = []
    for dset in datasets:
      x = dset[0]
      y = dset[1]
      xmin = numpy.min(x)
      xmax = numpy.max(x)
      piece = spline_2d(x, y)
      piece.xmin = xmin
      piece.xmax = xmax
      self.pieces.append(piece)

  def in_range(self, piece, x):
    return piece.xmin <= x and x <= piece.xmax

  def get_piece(self, x):
    for p in self.pieces:
      if self.in_range(p, x):
        return p
    raise ValueError, "Out-of-range x value = %g" % x

  def spline(self, x):
    return self.get_piece(x).spline(x)
