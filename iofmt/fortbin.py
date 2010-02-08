# $Id: fortbin.py,v 1.1 2010-02-08 21:49:54 wirawan Exp $
#
# wpylib.iofmt.fortbin module
# Created: 20100208
# Wirawan Purwanto
#
"""
Fortran binary format.

"""

import numpy
import sys

from wpylib.sugar import ifelse

class fortran_bin_file(object):
  """A tool for reading Fortran binary files."""
  def __init__(self, filename=None):
    self.record_marker_type = numpy.uint32
    self.debug = 100
    if filename:
      self.open(filename)

  def open(self, filename):
    self.F = open(filename, "rb")

  def read(self, *fields, **opts):
    """Reads a Fortran record.
    The description of the fields are given as
    (name, dtype, length) tuples."""
    from numpy import fromfile as rd
    if self.debug:
      dbg = lambda msg : sys.stderr.write(msg)
    else:
      dbg = lambda msg : None
    def fld_count(f):
      if len(f) > 2:
        return f[2]
      else:
        return 1

    reclen = numpy.fromfile(self.F, self.record_marker_type, 1)
    dbg("Record length = %d\n" % reclen)
    expected_len = sum([ fld_count(f) * numpy.dtype(f[1]).itemsize
                           for f in fields ])
    dbg("Expected length = %d\n" % expected_len)
    if expected_len > reclen:
      raise IOError, \
        "Attempting to read %d bytes from a record of length %d bytes" \
        % (expected_len, reclen)

    if "out" in opts:
      rslt = opts["out"]
    else:
      rslt = {}

    if (issubclass(rslt.__class__, dict) and issubclass(dict, rslt.__class__)) \
       or "__setitem__" in dir(rslt):
      def setval(d, k, v):
        d[k] = v
    else:
      # Assume we can use setattr method:
      setval = setattr

    for f in fields:
      if len(f) > 2:
        (name,Dtyp,Len) = f
        dtyp = numpy.dtype(Dtyp)
        setval(rslt, name, numpy.fromfile(self.F, dtyp, Len))
      else:
        # Special handling for scalars
        name = f[0]
        dtyp = numpy.dtype(f[1])
        setval(rslt, name, numpy.fromfile(self.F, dtyp, 1)[0])

    if expected_len < reclen:
      self.F.seek(reclen - expected_len, 1)

    reclen2 = numpy.fromfile(self.F, self.record_marker_type, 1)
    dbg("Record length tail = %d\n" % reclen2)

    if reclen2 != reclen:
      raise IOError, \
        "Inconsistency in record: end-marker length = %d; was expecting %d" \
        % (reclen2, reclen)

    return rslt

