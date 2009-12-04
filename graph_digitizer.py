#!/usr/bin/ipython -pylab
#
# $Id: graph_digitizer.py,v 1.1 2009-12-04 19:30:26 wirawan Exp $
#
# Created: 20091204
# Wirawan Purwanto
#
# Simple and dirty utility module to digitize a graph (e.g. those image files
# obtained from a journal article PDF).
#

import numpy

def make_matrix(Str, debug=None):
  """Simple tool to convert a string like
    '''1 2 3
    4 5 6
    7 8 9'''
  into a numpy matrix (or, actually, an array object)."""
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

def get_axis_scaler(data, axis):
  """Simple routine to obtain the scaling factor from pixel coordinate to
  x or y value. The `data' string argument is a literal table like:
      xpixel  ypixel   xvalue
      ...
  or
      xpixel  ypixel   yvalue
      ...
  Only linear scale is supported."""
  from scipy import stats
  datamtx = make_matrix(data)

  if axis == "x":
    xx = datamtx[:,0]
    yy = datamtx[:,2]
  else:
    xx = datamtx[:,1]
    yy = datamtx[:,2]

  # example from
  # http://www2.warwick.ac.uk/fac/sci/moac/currentstudents/peter_cock/python/lin_reg
  (gradient, intercept, r_value, p_value, std_err) = stats.linregress(xx,yy)
  print gradient, intercept, r_value, p_value, std_err

  #return (float(gradient[0]), float(intercept[0]))
  return (gradient, intercept)


class axes_scaler:
  """The main engine to "unscale" the graph's data points from pixel (x,y) to
  true axis (x,y) value. Only linear axis is supported here."""

  def __init__(self, data_x, data_y):
    """Initialize the axis scalers (x and y) from a given `pixel -> axis value'
    mapping."""
    self.init(data_x, data_y)

  def init(self, data_x, data_y):
    self.xscaler = get_axis_scaler(data_x, "x")
    self.yscaler = get_axis_scaler(data_y, "y")

  def __call__(self, x, y):
    return ((self.xscaler[0]*x + self.xscaler[1]), \
            (self.yscaler[0]*y + self.yscaler[1]))

  def scale_many(self, data):
    mtx = make_matrix(data)
    rslt = []
    for row in mtx:
      (x, y) = row[0], row[1]
      rslt.append(list( self(x, y) ))
      #print x, y
    return numpy.array(rslt)

