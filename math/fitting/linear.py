#
# wpylib.math.fitting.linear module
# Created: 20121015
# Wirawan Purwanto
#

"""
wpylib.math.fitting.linear module

Linear fitting tools.
"""

import numpy
from wpylib.math.fitting import fit_result

def linregr2d_SZ(x, y, sigma=None):
  """Performs a linear least square regression to according to a
  linear model

    y(x) = a + b*x ,

  where the input y has uncertainty given by sigma.
  """
  from numpy import sum, sqrt

  # Based on Shiwei's regr.F code (from email received 20060102).
  # See Linear-regression.txt in my repository of Shiwei's files.
  # See also Numerical Recipes in C, 2nd ed, Sec. 15.2.
  xx = numpy.array(x, copy=False)
  yy = numpy.array(y, copy=False)
  if sigma == None:
    # My addition -- can be dangerous
    # In case of no errorbar, we proceed as if all measurement
    # data have the same uncertainty, taken to be 1.
    ww = numpy.ones_like(y)
  else:
    ww = numpy.array(sigma, copy=False)
    ww **= -2      # make 1/sigma**2 array

  e1 = sum(xx * yy * ww)
  e2 = sum(yy * ww)
  d11 = sum(xx * ww)
  d12 = sum(xx**2 * ww)
  d21 = sum(ww)
  d22 = d11

  detinv = 1.0 / (d11*d22 - d12*d21)
  a = (e1*d22 - e2*d12) * detinv
  b = (e2*d11 - e1*d21) * detinv

  # Shiwei's old method of computing the uncertainty of the
  # y-intersect (sigma_a):
  varsum = sum((xx*d11 - d12)**2 * ww)
  var = varsum * detinv**2
  sigma = sqrt(var)

  # New method based on NR chapter: sqrt(sigma_a2) must give
  # identical result to sigma or else something is screwy!
  sigma_a2 = d12 * (-detinv)
  sigma_b2 = d21 * (-detinv)

  #print sigma_a2
  #print sigma_b2

  return fit_result(
    fit_method='linregr2d_SZ',
    fit_model='linear',
    a=a,
    b=b,
    sigma=sigma,
    sigma_a=sqrt(sigma_a2),
    sigma_b=sqrt(sigma_b2),
  )



def Test_1():
  """Testcase 1.

      >>> wpylib.math.fitting.linear.Test_1()
      ...
      {'a': -1392.3182324234213,
       'b': -0.82241012516149792,
       'fit_method': 'linregr2d_SZ',
       'fit_model': 'linear',
       'sigma': 0.00048320905704467775,
       'sigma_a': 0.00048320905704467786,
       'sigma_b': 0.080335909573397646}

  My wlinreg tool (via 'dtextrap' shell script alias gives:

      a stats:
      Total number of data     : 100000
      Average                  : -1392.32
      Sample standard deviation: 0.000460341
      Error of the average     : 1.45573e-06 (-1.046e-07%)
      b stats:
      Total number of data     : 100000
      Average                  : -0.822099
      Sample standard deviation: 0.0803118
      Error of the average     : 0.00025397 (-0.03089%)
      Summary
      a =      -1392.31823569246 +/-   0.000460341146124978 = -1392.31824(46)
      b =     -0.822098515674071 +/-     0.0803118207916705 = -0.822(80)

  which is close enough for this purpose!
  """
  from wpylib.text_tools import make_matrix as mtx
  M = mtx("""
  # Source: Co+ QMC/CAS(8,11)d26 cc-pwCVQZ-DK result dated 20121015
   0.01    -1392.32619 0.00047
   0.005   -1392.32284 0.00037
   0.0025  -1392.31994 0.00038
  """)
  x = M[:,0]
  y = M[:,1]
  dy = M[:,2]
  rslt = linregr2d_SZ(x,y,dy)
  print rslt
  return rslt


def Test_2():
  """Testcase 2.
  Similar to testcase 1 but with all uncertainties == 1.

      >>> wpylib.math.fitting.linear.Test_2()
      polyfit result = -0.809999999961 -1392.318265
      {'a': -1392.3182649999987,
       'b': -0.81000000006627304,
       'fit_method': 'linregr2d_SZ',
       'fit_model': 'linear',
       'sigma': 1.2247448713915881,
       'sigma_a': 1.2247448713915885,
       'sigma_b': 185.16401995451022}

  This is to be compared with the polyfit output.
  """
  from wpylib.text_tools import make_matrix as mtx
  M = mtx("""
  # Source: Co+ QMC/CAS(8,11)d26 cc-pwCVQZ-DK result dated 20121015
   0.01    -1392.32619 1.0
   0.005   -1392.32284 1.0
   0.0025  -1392.31994 1.0
  """)
  x = M[:,0]
  y = M[:,1]
  dy = M[:,2]
  rslt = linregr2d_SZ(x,y,dy)

  polyfit_result = numpy.polyfit(x,y,deg=1,full=False)
  print "polyfit result = ", polyfit_result[0], polyfit_result[1]
  return rslt


def Test_3():
  """Testcase 3.
  Feed of test from 1/x**3 extrapolation, Ca+4H2 Z=2.3 cc-pCV[TQ5]Z basis

      >>> wpylib.math.fitting.linear.Test_3()
      {'a': -0.92257959784330612,
       'b': 10.193612525866801,
       'fit_method': 'linregr2d_SZ',
       'fit_model': 'linear',
       'sigma': 0.0010352279401853368,
       'sigma_a': 0.0010352279401853377,
       'sigma_b': 0.036555525396641586}

  """
  from wpylib.text_tools import make_matrix as mtx
  M = mtx("""
  # Source: Co+ QMC/CAS(8,11)d26 cc-pwCVQZ-DK result dated 20121015
  # Groff notebook 1.90, table "testZ23 geometry: Z=2.3 dHH=0.7682", near
  # "/// begin extra (for paper)"
   0.03703704 -0.54533  0.00061
   0.015625   -0.76167  0.00074
   0.008      -0.8442   0.0012
  """)
  x = M[:,0]
  y = M[:,1]
  dy = M[:,2]
  rslt = linregr2d_SZ(x,y,dy)
  return rslt
