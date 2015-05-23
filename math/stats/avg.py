# $Id: avg.py,v 1.1 2010-10-07 15:56:55 wirawan Exp $
# Create: 20090112

# TODO: Use less roundoff-error algorithm found in:
# http://en.wikipedia.org/wiki/Standard_deviation#Weighted_calculation

import math

class avg(object):
  def __init__(self):
    self.clear()
  def clear(self):
    self.N = 0
    self.sum1 = 0.0
    self.sum2 = 0.0
  def add(self, value):
    self.N += 1
    self.sum1 += value
    self.sum2 += value*value
    return self
  #__add__ = add  << HERETICAL!!!
  def mean(self):
    return self.sum1 / self.N
  def stddev(self):
    N = self.N
    avg1 = self.sum1 / N
    avg2 = self.sum2 / N
    return math.sqrt(abs( (avg2 - avg1**2) * N / (N - 1) ))

# Operator overloading:
avg.__iadd__ = avg.add
avg.__call__ = avg.mean


class weighted_stats(object):
  def __init__(self, a=None, weights=None):
    if a != None:
      get_sample_stats(a, weights, result=self)


def get_sample_stats(a, weights=None, result=None):
  """Applies basic statistics (average, variance, standard deviation)
  for a given sample, optionally with a weight.
  """
  from numpy import asarray, count_nonzero, product, sqrt, sum, nan
  a = asarray(a)
  if result is None:
    r = weighted_stats()
  else:
    r = result
  if weights is None:
    r.s0 = product(a.shape)
    r.s1 = sum(a)
    r.s2 = sum(a**2)
    r.N = r.s0
    r.N_nz = r.s0
  else:
    weights = asarray(weights)
    r.s0 = sum(weights)
    r.s1 = sum(weights * a)
    r.s2 = sum(weights * a**2)
    r.N_nz = count_nonzero(weights)
    r.N = product(a.shape)
  # Ref: http://en.wikipedia.org/wiki/Standard_deviation#Weighted_calculation
  # TODO: Use less roundoff-error algorithm found therein.
  r.avg = r.s1 / r.s0
  r.var_pop = (r.s0 * r.s2 - r.s1**2) / (r.s0**2)
  r.std_pop = sqrt(r.var_pop)
  if r.N_nz > 1:
    r.var_samp = (r.N_nz / (r.N_nz - 1.0)) * r.var_pop
    r.std_samp = sqrt(r.var_samp)
  else:
    r.var_samp = nan
    r.std_samp = nan

  return r

