"""
REFERENCES:

Jackknife and Bootstrap Resampling Methods in Statistical Analysis to Correct for Bias.
P. Young
http://young.physics.ucsc.edu/jackboot.pdf


Notes on Bootstrapping
Author unspecified
http://www.math.ntu.edu.tw/~hchen/teaching/LargeSample/notes/notebootstrap.pdf


"""

import numpy

from numpy import pi, cos
from numpy.random import normal

def test1_generate_data(ndata=1000):
  """

  """
  return pi / 3 + normal(size=ndata)


def test1():
  global test1_dset
  test1_dset = test1_generate_data()
  dset = test1_dset
  print "first jackknife routine: jk_generate_datasets -> jk_wstats"
  dset_jk = jk_generate_datasets(dset)
  cos_avg1 = jk_wstats(dset_jk, func=numpy.cos)
  print cos_avg1

  print "second jackknife routine: jk_generate_averages -> jk_stats_aa"
  aa_jk = jk_generate_averages(dset)
  cos_avg2 = jk_stats_aa(aa_jk, func=numpy.cos)
  print cos_avg2

  # the two results above must be identical


def test2_generate_data():
  rootdir = "/home/wirawan/Work/PWQMC-77/expt/qmc/MnO/AFM2/rh.1x1x1/Opium-GFRG/vol10.41/k-0772+3780+2187.run"
  srcfile = rootdir + "/measurements.h5"
  from pyqmc.results.pwqmc_meas import meas_hdf5

  global test2_db
  test2_db = meas_hdf5(srcfile)


def jk_select_dataset(a, i):
  """Selects the i-th dataset for jackknife operation from a
  given dataset 'a'.
  The argument i must be: 0 <= 0 < len(a).
  This is essentially deleting the i-th data point from the
  original dataset.
  """
  a = numpy.asarray(a)
  N = a.shape[0]
  assert len(a.shape) == 1
  assert 0 <= i < N
  rslt = numpy.empty(shape=(N-1,), dtype=a.dtype)
  rslt[:i] = a[:i]
  rslt[i:] = a[i+1:]
  return rslt

def jk_generate_datasets(a):
  """Generates ALL the datasets for jackknife operation from
  the original dataset 'a'.
  For the i-th dataset, this is essentially deleting the
  i-th data point from 'a'.
  """
  a = numpy.asarray(a)
  N = a.shape[0]
  assert len(a.shape) == 1
  rslt = numpy.empty(shape=(N,N-1,), dtype=a.dtype)
  for i in xrange(N):
    rslt[i, :i] = a[:i]
    rslt[i, i:] = a[i+1:]
  return rslt

def jk_generate_averages_old1(a, weights=None):
  """Generates ALL the average samples for jackknife operation
  from the original dataset 'a'.
  For the i-th dataset, this is essentially deleting the
  i-th data point from 'a', then taking the average.
  
  This version does not store N*(N-1) data points; only (N).
  This version is SLOW because it has to compute
  the averages N times---thus it still computationally scales as N**2.
  """
  a = numpy.asarray(a)
  N = a.shape[0]
  assert len(a.shape) == 1
  aa_jk = numpy.empty(shape=(N,), dtype=a.dtype)
  dset_i = numpy.empty(shape=(N-1,), dtype=a.dtype)
  if weights != None:
    weights_i = numpy.empty(shape=(N-1,), dtype=weights.dtype)
  for i in xrange(N):
    dset_i[:i] = a[:i]
    dset_i[i:] = a[i+1:]
    if weights != None:
      weights_i[:i] = weights[:i]
      weights_i[i:] = weights[i+1:]
      aa_jk[i] = numpy.average(dset_i, weights=weights_i)
    else:
      aa_jk[i] = numpy.mean(dset_i)

  return aa_jk

def jk_generate_averages(a, weights=None):
  """Generates ALL the average samples for jackknife operation
  from the original dataset 'a'.
  For the i-th dataset, this is essentially deleting the
  i-th data point from 'a', then taking the average.

  This version does not store N*(N-1) data points; only (N).
  This version is faster by avoiding N computations of average.
  """
  a = numpy.asarray(a)
  N = a.shape[0]
  assert len(a.shape) == 1
  if weights != None:
    weights = numpy.asarray(weights)
    assert weights.shape == a.shape
    aw = a * weights
    num = numpy.sum(aw) * 1.0
    denom = numpy.sum(weights)
    aa_jk = (num - aw) / (denom - weights)
  else:
    num = numpy.sum(a) * 1.0
    aa_jk = (num - a[i]) / (N - 1)

  return aa_jk

'''
def jk_stats_old(a_jk, func=None):
  """a_jk must be in the same format as that produced by

  """
  # get all the jackknived stats.
  if func == None:
    jk_mean = numpy.mean(a_jk, axis=1)
  else:
    jk_mean = numpy.mean(func(a_jk), axis=1)
'''

def jk_wstats_dsets(a_jk, w_jk=None, func=None):
  """Computes the jackknife statistics from the preprocessed datasets
  produced by jk_generate_datasets() routine.
  The input a_jk and w_jk must be in the same format as that produced by
  jk_generate_datasets.
  """
  # get all the jackknived stats.
  N = len(a_jk)
  # reconstruct full "a" array:
  a = numpy.empty(shape=(N,), dtype=a_jk.dtype)
  a[1:] = a_jk[0]
  a[0] = a_jk[1][0]
  if func == None:
    func = lambda x : x
  aa_jk = numpy.average(a_jk, axis=1, weights=w_jk)
  #print aa_jk
  f_jk = func(aa_jk)
  mean = numpy.mean(f_jk)
  var = numpy.std(f_jk) * numpy.sqrt(N-1)
  mean_unbiased = N * func(a.mean()) - (N-1) * mean
  return (mean, var, mean_unbiased)


def jk_stats_aa(aa_jk, func=None, a=None):
  """Computes the jackknife statistics from the preprocessed
  jackknife averages (aa_jk).
  The input array aa_jk is computed by jk_generate_averages().
  """
  # get all the jackknived stats.
  N = len(aa_jk)
  # reconstruct full "a" array:
  if func == None:
    func = lambda x : x
  f_jk = func(aa_jk)
  mean = numpy.mean(f_jk)
  var = numpy.std(f_jk) * numpy.sqrt(N-1)
  if a != None:
    mean_unbiased = N * func(a.mean()) - (N-1) * mean
  else:
    mean_unbiased = None
  return (mean, var, mean_unbiased)
