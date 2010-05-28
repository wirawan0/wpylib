# $Id: fortbin.py,v 1.3 2010-05-28 18:43:14 wirawan Exp $
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
  """A tool for reading and writing Fortran binary files.

  Caveat: On 64-bit systems, typical Fortran implementations still have int==int32
  (i.e. the LP64 programming model), unless "-i8" kind of option is enabled.
  To use 64-bit default integer, set the default_int attribute to numpy.int64 .
  """
  record_marker_type = numpy.uint32
  default_int = numpy.int32
  default_float = numpy.float64
  default_str = numpy.str_

  def __init__(self, filename=None, mode="r"):
    self.debug = 0
    if filename:
      self.open(filename, mode)

  def open(self, filename, mode="r"):
    self.F = open(filename, mode+"b")

  def close(self):
    if getattr(self, "F", None):
      self.F.close()
      self.F = None

  def read(self, *fields, **opts):
    """Reads a Fortran record.
    The description of the fields are given as
    either (name, dtype) or (name, dtype, length) tuples.
    If length is not specified, then a scalar value is read.
    Length is a scalar for 1-D array, or a tuple or list for multidimensional
    array."""
    from numpy import fromfile as rd
    if self.debug or opts.get("debug"):
      dbg = lambda msg : sys.stderr.write(msg)
    else:
      dbg = lambda msg : None
    def fld_count(f):
      if len(f) > 2:
        if isinstance(f[2], (list,tuple)):
          return numpy.product(f[2])
        else:
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

    if "dest" in opts:
      rslt = opts["dest"]
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
        Len2 = fld_count(f)
        if isinstance(f[2], list) or isinstance(f[2], tuple):
          # Special handling for shaped arrays
          arr = numpy.fromfile(self.F, dtyp, Len2)
          setval(rslt, name, arr.reshape(tuple(Len), order='F'))
        else:
          setval(rslt, name, numpy.fromfile(self.F, dtyp, Len2))

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

  def write_vals(self, *vals, **opts):
    """Writes a Fortran record.
    Only values need to be given, because the types are known.
    This is a direct converse of read subroutine."""
    if self.debug:
      dbg = lambda msg : sys.stderr.write(msg)
    else:
      dbg = lambda msg : None

    vals0 = vals
    vals = []
    for v in vals0:
      if isinstance(v, int):
        v2 = self.default_int(v)
        if v2 != v:
          raise OverflowError, \
            "Integer too large to represent by default int: %d" % v
        vals.append(v2)
      elif isinstance(v, float):
        v2 = self.default_float(v)
        # FIXME: check for overflow error like in integer conversion above
        vals.append(v2)
      elif isinstance(v, str):
        v2 = self.default_str(v)
        vals.append(v2)
      elif "itemsize" in dir(v):
        vals.append(v)
      else:
        raise NotImplementedError, \
          "Unsupported object of type %s of value %s" \
          (str(type(v)), str(v))

    reclen = numpy.sum([ v.size * v.itemsize for v in vals ], \
                       dtype=self.record_marker_type)

    dbg("Record length = %d\n" % reclen)
    dbg("Item count = %d\n" % len(vals))
    reclen.tofile(self.F)

    for v in vals:
      if isinstance(v, numpy.ndarray):
        # Always store in "Fortran" format, i.e. column major
        # Since tofile() always write in the row major format,
        # we will transpose it before writing:
        v.T.tofile(self.F)
      else:
        v.tofile(self.F)

    reclen.tofile(self.F)


  def write_fields(self, src, *fields, **opts):
    if (issubclass(src.__class__, dict) and issubclass(dict, src.__class__)) \
       or "__getitem__" in dir(src):
      def getval(d, k):
        return d[k]
    else:
      # Assume we can use getattr method:
      getval = getattr

    vals = []
    for f in fields:
      if isinstance(f, str):
        vals.append(getval(src, f))
      elif isinstance(f, (list, tuple)):
        v = getval(src, f[0])
        # FIXME: check datatype and do necessary conversion if f[1] exists
        # Exception: if a string spec is found, we will retrofit the string
        # to that kind of object. Strings that are too long are silently
        # truncated and those that are too short will have whitespaces
        # (ASCII 32) appended.
        if len(f) > 1:
          dtyp = numpy.dtype(f[1])
          if dtyp.char == 'S':
            strlen = dtyp.itemsize
            v = self.default_str("%-*s" % (strlen, v[:strlen]))
        # FIXME: check dimensionality if f[2] exists
        vals.append(v)
      else:
        raise ValueError, "Invalid field type: %s" % str(type(f))

    self.write_vals(*vals, **opts)


def array_major_dim(arr):
  """Tests whether a numpy array is column or row major.
  It will return the following:
    -1 : row major
    +1 : column major
    0  : unknown (e.g. no indication one way or the other)
  In the case of inconsistent order, we will raise an exception."""
  if len(arr.shape) <= 1:
    return 0
  elif arr.flags['C_CONTIGUOUS']:
    return -1
  elif arr.flags['F_CONTIGUOUS']:
    return +1
  # In case of noncontiguous array, we will have to test it
  # based on the strides
  else:
    Lstrides = numpy.array(arr.shape[:-1])
    Rstrides = numpy.array(arr.shape[1:])
    if numpy.all(Lstrides >= Rstrides):
      # Categorizes equal consecutive strides to "row major" as well
      return -1
    elif numpy.all(Lstrides <= Rstrides):
      return +1
    else:
      raise RuntimeError, \
        "Unable to determine whether this is a row or column major object."


