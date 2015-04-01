#
# wpylib.iofmt.hdf5 module
# Created: 20150401
# Wirawan Purwanto
#
"""
HDF5 binary format support, using h5py.

"""

import h5py
import numpy
import sys


# Quickie functions

def hdf5_read_value(filename, key):
  """Single-value read action from a file.
  Raises KeyError if the item does not exist.
  """
  F = h5py.File(filename, 'r')
  try:
    val = F[key].value
  except KeyError:
    F.close()
    raise
  F.close()
  return val


def hdf5_write_value(filename, key, value):
  """Single-value write action from a file.
  Overwrites the existing value, if it exists.
  Raises an exception upon error.
  """
  F = h5py.File(filename, 'a')
  try:
    if key in F:
      del F[key]
    F[key] = value
  except:
    F.close()
    raise
  F.close()


def hdf5_write_values(filename, keyvals):
  """Multiple-value write action to a file.
  The key-value pairs are specified as a dict.
  Overwrites the existing value, if it exists.
  Raises an exception upon error.
  """
  F = h5py.File(filename, 'a')
  try:
    for (key,value) in keyvals.iteritems():
      if key in F:
        del F[key]
      F[key] = value
  except:
    F.close()
    raise
  F.close()

