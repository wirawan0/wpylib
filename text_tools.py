# $Id: text_tools.py,v 1.6 2011-06-03 18:24:00 wirawan Exp $
#
# wpylib.text_tools
# Created: 20091204
# Wirawan Purwanto
#
# Simple and dirty text tools
#

import numpy
from wpylib.sugar import ifelse

def make_matrix(Str, debug=None):
  """Simple tool to convert a string like
    '''1 2 3
    4 5 6
    7 8 9'''
  into a numpy matrix (or, actually, an array object).
  This is for convenience in programming quick scripts, much like octave matrix
  format (but without the evaluation of math expressions that octave has,
  of course)."""
  if isinstance(Str, numpy.matrix):
    return numpy.array(Str)
  elif isinstance(Str, numpy.ndarray):
    if len(Str.shape) == 2:
      return Str.copy()
    else:
      raise ValueError, "Cannot make matrix out of non-2D array"
  Str2 = ";".join([ row.split("#",1)[0].rstrip().rstrip(";")
                      for row in Str.split("\n")
                        if row.split("#",1)[0].strip() != ""
                  ])
  rslt = numpy.matrix(Str2)
  if debug: print rslt
  return numpy.array(rslt)

def vector_str(M, fmt="%22.15g", V=False):
  if len(M.shape) != 1:
    raise ValueError, "Wrong shape: expecting a one-dimensional array."
  if V:
    return "\n".join([ fmt % m for m in M ])
  else:
    return " ".join([ fmt % m for m in M ])

def matrix_str(M, fmt="%22.15g"):
  if len(M.shape) != 2:
    raise ValueError, "Wrong shape: expecting a two-dimensional array."
  return "\n".join([ " ".join([ fmt % c for c in R ] ) for R in M ])


def str_unindent(S, amount=None):
  """Automatically unidents a string based on the first indentation found
  on a nonempty string line. Assuming UNIX LF end-of-line."""

  if amount == None:
    nindent = -1  # autodetect, default
  else:
    nindent = amount
    indent_whsp = " " * nindent

  strs = S.split("\n")
  rslt = []
  for s in strs:
    if s.strip() != "":
      if nindent == -1:
        nindent = len(s) - len(s.lstrip())
        indent_whsp = " " * nindent
      if s[:nindent] == indent_whsp:
        s = s[nindent:]
      # else, quietly accept all strings that are not properly indented
      # at their beginning
    rslt.append(s)

  return "\n".join(rslt)


def str_save_to_file(filename, s1, *more_str, **opts):
  """Save one or more string (or iterables) to a file with a given file.

  Additional options (with their defaults shown below):
  * append=False: if True, then the string(s) are appended to the file.
  * eol=False: if True, then an EOLN is added between strings.
  """
  add_eol = opts.get("eol", False)
  append = opts.get("append", False)
  if append:
    F = open(filename, "a")
  else:
    F = open(filename, "w")

  for S in (s1,) + more_str:
    if getattr(S, "__iter__", False):
      for S2 in S:
        F.write(S2)
        if add_eol: F.write("\n")
    else:
      F.write(S)
      if add_eol: F.write("\n")

  F.close()


def str_expand(template, params, maxiter=100):
  """Doing iterative python-style %(KWD)* substitution until no more
  substitution takes place.
  This is used to constructively build input string, etc. that contain
  parameter within parameter."""
  str1 = None
  str2 = template
  i = 0
  while str1 != str2 and (maxiter > 0 and i < maxiter):
    str1 = str2
    str2 = str1 % params
    i += 1

  if str1 != str2: raise RuntimeError, "Iteration limit exceeded"
  return str1


def str_grep(S, strs):
  """Returns a list of strings wherein the substring S is found."""
  return [s for s in strs if s.find(S) >= 0]

def str_igrep(S, strs):
  """Returns a list of the indices of the strings wherein the substring S
  is found."""
  return [i for (s,i) in zip(strs,xrange(len(strs))) if s.find(S) >= 0]


def slice_str(s):
  return "%s:%s:%s" % (
    ifelse(s.start == None, "", str(s.start)),
    ifelse(s.stop == None, "", str(s.stop)),
    ifelse(s.step == None, "", str(s.step)),
  )


