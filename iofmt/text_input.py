#!/usr/bin/python
# $Id: text_input.py,v 1.6 2011-09-16 21:21:23 wirawan Exp $
#
# wpylib.iofmt.text_input module
# Quick-n-dirty text input utilities
#
# Wirawan Purwanto
# Created: 20090601
#
# Routines put here are commonly used in my own scripts.
# They are not necessarily suitable for general-purpose uses; evaluate
# your needs and see if they can them as well.
#
# 20090601: Created as pyqmc.utils.text_input .
# 20100927: Moved to wpylib.iofmt.text_input .
#
# TODO
# - book-keep the line number. Also note superfile must have its own line
#   number keeping.
#
"""
Simple text-based input reader.

This module is part of wpylib project.
"""

import re
import numpy

from wpylib.sugar import zip_gen
from wpylib.file.file_utils import open_input_file
from wpylib.py import make_unbound_instance_method
import wpylib.py.im_weakref

def make_match_proc(match):
  """Make matching procedure: simple string becomes regexp,
  regexp remains regexp, and other callable object is passed as is."""
  if isinstance(match, basestring):
    Regexp = re.compile(match)
    match_proc = lambda x: Regexp.search(x)
  elif hasattr(getattr(match, "search", None), "__call__"):
    Regexp = match
    match_proc = lambda x: Regexp.search(x)
  else:
    match_proc = match
  return match_proc


class text_input(object):
  '''Text input reader with support for UNIX-style comment marker (#) and
  standard field separation (tabs and whitespaces).
  Used for quick and dirty data reading (iterating only once in forward
  direction without the need of rewinding or skipping).
  This object can be treated like an input file, e.g. used as an iterator,
  etc.

  To support more fancy options (e.g., rewinding), use "superize=1" when
  creating the instance.

  Other valid constructor flags:
  - expand_errorbar (default: False)
  - comment_char (default: "#")
  - skip_blank_lines (default: True)
  '''

  def __init__(self, fname, **opts):
    if opts.get("superize", 0):
      open_opts = { "superize" : opts["superize"] }
      del opts["superize"]
    else:
      open_opts = {}
    self.file = open_input_file(fname, **open_opts)
    # Do NOT touch the "next_" field below unless you know what you're doing:
    self.set_next_proc(self.next_line)
    # field_filtering_proc field can be used to filter unwanted fields, or do
    # some additional transformations before final feed to the main iteration.
    self.field_filtering_proc = lambda flds : flds
    # Default fancy options:
    self.skip_blank_lines = True
    if len(opts) > 0:
      self.set_options(**opts)
    self.lineno = 0

  def __del__(self):
    if getattr(self, "file", None):
      self.file.close()

  def close(self):
    if getattr(self, "file", None):
      self.file.close()
      del self.file

  def __iter__(self):
    return self

  """
  def next(self):
    while True:
      L = self.file.next()
      F = self.field_filtering_proc(L.split("#")[0].split())
      if len(F) > 0:
        return F
  """

  def next_rec(self):
    '''Yields the next record, which is already separated into fields.'''
    comment_char = getattr(self, "comment_char", "#")
    while True:
      self.lineno += 1
      L = self.file.next()
      F = self.field_filtering_proc(L.split(comment_char)[0].split())
      if len(F) > 0 or not self.skip_blank_lines:
        return F

  def next_line(self):
    '''Yields the next line, which is already separated into fields.'''
    comment_char = getattr(self, "comment_char", "#")
    while True:
      self.lineno += 1
      L = self.file.next()
      F = self.field_filtering_proc(L.split(comment_char)[0].rstrip())
      if len(F) > 0 or not self.skip_blank_lines:
        return F

  def set_next_proc(self, proc):
    self.next_ = make_unbound_instance_method(proc)
  def next(self):
    return self.next_(self)

  def seek_text(self, regex=None, match=None):
    """Seeks the file until a particular piece text is encountered.
    We ignore all comments.
    The `regex' argument can be either a regex string or a standard python
    regular expression object."""

    if regex:
      if isinstance(regex, basestring):
        Regexp = re.compile(regex)
      else:
        Regexp = regex
      match_proc = lambda x: Regexp.search(x)
    else:
      match_proc = match

    while True:
      L = self.next_line()
      if match_proc(L):
        return L


  def read_floats(self, *cols, **kwd):
    """Quickly reads a set of floats from a text file.
    Returns a numpy array of the values in double precision.

    Example usage:
      >>> arr = text_input("/tmp/file.txt").read_floats(0, 2, 3)
    to read columns 1, 3, and 4 of the text file /tmp/file.txt, while disregarding
    comments.
    """
    # float_fields extracts the desired columns and converts them to floats
    float_fields = lambda vals : [ float(vals[col]) for col in cols ]
    if "maxcount" in kwd:
      rslt = [ float_fields(vals.split()) for (c,vals) in zip(xrange(kwd['maxcount']),self) ]
    else:
      rslt = [ float_fields(vals.split()) for vals in self ]
    # finally convert them to a numpy ndarray:
    return numpy.array(rslt)

  def read_items(self, *col_desc, **kwd):
    """Quickly reads a set of items from records of whitespace-separated fields
    in a text file.
    Returns a structured numpy array of the values read.

    Example usage:

      >>> arr = text_input("/tmp/file.txt").read_items(0, (2, int), (3, "S10", "Atom"))

    reads columns 1 (as floats, by default), 3 (as integers), and 4 (as strings of
    max length of 10, which field is named "Atom") from the text file /tmp/file.txt,
    while disregarding comments.

    If the tuple contains the third field, it is used as the name of the field;
    otherwise the fields are named f0, f1, f2, ....

    Preliminary ability to read in complex data has been added!
    Complex data (floating-point only) must be specified as a tuple of two columns
    containing the real and imaginary data, like this:
       ((2, 3), complex, 'ampl')
    or
       ((7, 9), complex)     # fine to interleave column with something else


    Additional keyword options:
    * deftype: default datatype
    * maxcount: maximum number of records to be read
    * end_line_match: a regular expression or test subroutine accepting a
      single argument (i.e. the text line) marking the end boundary of the list
      to be read (i.e. one line past the list contents)
    * last_line_match: a regular expression or test subroutine accepting a
      single argument (i.e. the text line) marking the last element of the list
      to be read

    """
    deftype = kwd.get("deftype", float)

    class register_item_t:
      flds = []
      cols = []
      complex_types = (complex, numpy.complexfloating)
      def add(self, col, fldname, type):
        dtype = numpy.dtype(type)
        t = dtype.type
        dsamp = t() # create a sample
        # Special handling for complex:
        # -- unfortunately this detection fails because even real
        # numbers have its 'imag' attribute:
        #dattrs = dir(dsamp)
        #if "imag" in dattrs and "real" in dattrs:
        if isinstance(dsamp, numpy.complexfloating):
          dtype_elem = dsamp.real.dtype
          t_elem = dtype_elem.type
          conv_func = lambda v, c: t(t_elem(v[c[0]]) + 1j*t_elem(v[c[1]]))
          self.cols.append((conv_func, col))
          self.flds.append((fldname, dtype))
        else:
          # other datatypes: much easier
          # Simply get the string, and use numpy to convert to the datatype
          # on-the-fly
          conv_func = lambda v, c: t(v[c])
          self.cols.append((conv_func, col))
          self.flds.append((fldname, dtype))
    reg = register_item_t()

    for (i,c) in zip(xrange(len(col_desc)), col_desc):
      if type(c) == int:
        reg.add(c, 'f' + str(i), deftype)
      elif len(c) == 1:
        reg.add(c[0], 'f' + str(i), deftype)
      elif len(c) == 2:
        reg.add(c[0], 'f' + str(i), c[1])
      elif len(c) == 3:
        reg.add(c[0], c[2], c[1])
      else:
        raise ValueError, \
          "Invalid column specification: %s" % (c,)

    cols = reg.cols
    flds = reg.flds
    get_fields = lambda vals : tuple([ filt(vals,col) for (filt,col) in cols ])

    if "maxcount" in kwd:
      src_iter = zip_gen(xrange(kwd['maxcount']),self)
    else:
      src_iter = enumerate(self)
    # FIXME below: zip() evaluates the function before the loop, thus may
    # eat a lot of memory.
    if 'end_line_match' in kwd:
      rslt = []
      match = make_match_proc(kwd['end_line_match'])
      for (c,vals) in src_iter:
        if match(vals):
          break
        rslt.append(get_fields(vals.split()))
    elif 'last_line_match' in kwd:
      rslt = []
      match = make_match_proc(kwd['end_line_match'])
      for (c,vals) in src_iter:
        rslt.append(get_fields(vals.split()))
        if match(vals):
          break
    elif "maxcount" in kwd:
      #print "hello"
      rslt = [ get_fields(vals.split()) for (c,vals) in zip(xrange(kwd['maxcount']),self) ]
    else:
      rslt = [ get_fields(vals.split()) for vals in self ]
    #print rslt
    # finally convert them to a numpy ndarray:
    return numpy.array(rslt, dtype=flds)

  # Sets fancy options
  def set_options(self, **opts):
    for (o,v) in opts.iteritems():
      if o == "expand_errorbar":
        self.expand_errorbar(v)
      elif o == "skip_blank_lines":
        self.skip_blank_lines = v
      elif o == "comment_char":
        self.comment_char = v
      else:
        raise ValueError, "Invalid option: %s" % (o,)
    return self

  # Option for errorbar expansion:
  def expand_errorbar(self, v=True):
    '''Enables or disables errorbar expansion.'''
    from wpylib.py.im_weakref import im_ref
    if v:
      self.opt_expand_errorbar = True
      self.field_filtering_proc = im_ref(self.expand_errorbar_hook)
    else:
      self.opt_expand_errorbar = False
      self.field_filtering_proc = lambda flds : flds
    return self

  def expand_errorbar_hook(self, F):
    # A hook for field_filtering_proc for expanding errorbars:
    from pyqmc.stats.errorbar import expand
    return expand(F, flatten=True)


# Various sundry tools

def head(filename, maxlines):
  """Emulates UNIX head(1) command by reading at most `maxlines`
  text lines.
  It is intended for plain text files only!
  It also supports compressed files through text_input() facility.
  """
  # head is easy to implement. But how about tail?
  F = text_input(filename, skip_blank_lines=False, comment_char='\0')
  out = []
  try:
    for x in xrange(maxlines):
      out.append(F.next())
  except StopIteration:
    pass
  return out


def tail(filename, maxlines):
  """Emulates UNIX tail(1) command by reading at most `maxlines`
  text lines at the end of a text file.
  It is intended for plain text files only!
  It also supports compressed files through text_input() facility.

  Warning: this algorithm is far less optimal than head() since it
  has to read the whole file.
  It's okay for moderately small files.
  """
  F = text_input(filename, skip_blank_lines=False, comment_char='\0')
  out = []
  lines2read = max(2*maxlines, 100)
  try:
    while True:
      for x in xrange(lines2read):
        out.append(F.next())
      out = out[-maxlines:]
  except StopIteration:
    pass
  return out[-maxlines:]



# More tools for extracting data from table-like text stream/string.

tbl_filter_num1_rx = re.compile('^\s*[-+]?(?:[0-9]+|[0-9]+\.|\.[0-9]+|[0-9]+\.[0-9]+)(?:[EeDd][-+]?[0-9]+)?')
def tbl_filter_num1(flds, col=0, **args):
  """Simple filter function: given a list of splitted text in `flds`,
  if the col-th field of the row is a numerical
  string, then it is a valid row; otherwise we will ignore this row.
  """
  return tbl_filter_num1_rx.match(flds[col])


def filter_table_text(T, filter=tbl_filter_num1, filter_args={}):
  """Filters out irrelevant text (junk) from the table by commenting them out.
  Using the default filter, we assume that the target column (default==0)
  is a numerical value (usually a geometry value or a similar parameter).

  Input:
  * T = a text table (a multi-line string, with the linebreaks)
  * filter = a filter function
  * filter_args = dict-style arguments for the filter function."""
  Lines = T.splitlines()
  for (i,L) in enumerate(Lines):
    F = L.split()
    if len(F) == 0:
      pass
    elif not F[0].startswith("#") and not filter(F, **filter_args):
      Lines[i] = "#" + L
  return "\n".join(Lines)


class tbl_filter_num1_limited_range(object):
  """Fancy filtering: Assume that the first column is numerical
  (e.g., rbond); and only include rows where this `rbond` fall
  within a given range.
  """
  def __init__(self, rmin, rmax, col=0):
    self.rmin, self.rmax = rmin, rmax
    self.col = col
  def __call__(self, flds, **args):
    if tbl_filter_num1_rx.match(flds[self.col]):
      r = float(flds[0])
      return self.rmin <= r <= self.rmax
    else:
      return False
  def mk_table_filter(self):
    return lambda T: filter_table_text(T,filter=self)
  @classmethod
  def create(cls, rmin, rmax, col=0):
    o = cls(rmin, rmax, col=col)
    func = o.mk_table_filter()
    func.__name__ = "%s.create(%.4f,%.4f,%d)" \
                  % (cls.__name__, rmin, rmax, col)
    return func


def read_table(F, maps={}):
  """Reads in a 2-D table from a text stream.
  Returns a list of lists containing the table content, in each cell by
  default as a string, unless a mapping function is provided (for simple
  data conversion only).

  This is a legacy tool. It appears that numpy.genfromtxt can do what
  this tool can do, and better.
  You should probably check if numpy.genfromtxt can do the required job
  before using read_table/read_table_text provided in this module.
  """
  rows = []
  comment_char = "#"
  for L in F:
    L = L.split(comment_char,1)[0]
    flds = L.split()
    if len(flds) == 0:
      continue
    if maps:
      for i in xrange(len(flds)):
        if i in maps:
          flds[i] = maps[i](flds[i])
    rows.append(flds)
  return rows


def read_table_text(txt, maps={}):
  """Reads in a 2-D table from a text stream.
  The text (as a whole string) is given in the txt argument.
  """
  from StringIO import StringIO
  return read_table(StringIO(txt), maps)

