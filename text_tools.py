# $Id: text_tools.py,v 1.8 2011-09-13 21:50:16 wirawan Exp $
#
# wpylib.text_tools
# Created: 20091204
# Wirawan Purwanto
#
# Simple and dirty text tools
#

"""
wpylib.text_tools

Frequently used text tools.
"""

import numpy
from wpylib.sugar import ifelse

def read_text_table(F, maps={}, sep=None, comment_char="#"):
  """Reads in a 2-D table from a text stream.
  Returns a list of lists containing the table content, in each cell by
  default as a string, unless a mapping function is provided (for simple
  data conversion only)."""
  rows = []
  for L in F:
    if comment_char != None:
      L = L.split(comment_char,1)[0]
    flds = L.split(sep)
    if len(flds) == 0:
      continue
    if maps:
      for i in xrange(len(flds)):
        if i in maps:
          flds[i] = maps[i](flds[i])
    rows.append(flds)
  return rows

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

def vector_str(M, fmt="%22.15g", V=False, prefix="", suffix=""):
  if len(M.shape) != 1:
    raise ValueError, "Wrong shape: expecting a one-dimensional array."
  if V:
    return prefix + (suffix + "\n" + prefix).join([ fmt % m for m in M ]) + suffix
  else:
    return prefix + " ".join([ fmt % m for m in M ]) + suffix

def matrix_str(M, fmt=None, prefix="", suffix=""):
  """Prints a matrix in a textual format.
  Applicable for integer, float, and complex 2-D arrays.

  COMPLEX NUMBER SUPPORT

  By default, we print in full precision and in python-friendly format, like:

      (+3.200000000000000e+00+4.700000000000000e+00j)

  To print in C++ and Fortran friendly format, use:

      >>> A_str = text_tools.matrix_str(A, '(%+#22.15e,%+#22.15e)')

  The resulting output will be:

      (+3.200000000000000e+00,+4.700000000000000e+00)
  """
  linesep = suffix + "\n" + prefix
  if isinstance(M, numpy.matrix):
    M = numpy.asarray(M)
  elif not isinstance(M, numpy.ndarray):
    M = numpy.asarray(M)
  if len(M.shape) != 2:
    raise ValueError, "Wrong shape: expecting a two-dimensional array."
  if numpy.iscomplex(M[0,0]):
    if fmt is None:
      fmt = "(%+22.15e%+22.15ej)"
    mkfmt = lambda z: fmt % (z.real, z.imag)
    return prefix + linesep.join([ " ".join([ mkfmt(c) for c in R ]) for R in M ]) + suffix
  else:
    if fmt is None:
      fmt = "%22.15g"
    return prefix + linesep.join([ " ".join([ fmt % c for c in R ]) for R in M ]) + suffix


def str_indent(text, indent=" "*4):
  """Indents a text block by a given prefix.
  If the indent is a number 'N', a string of N white spaces are taken as
  the prefix.

  In python 3, textwrap.indent can accomplish the same thing."""
  if not isinstance(indent, basestring):
    # Assume this is a numeric:
    indent = " " * indent
  return indent + ('\n'+indent).join(x for x in str(text).splitlines())

def str_unindent(S, amount=None):
  """Automatically unidents a string based on the first indentation found
  on a nonempty string line. Assuming UNIX LF end-of-line.

  Note: textwrap.dedent accomplishes a similar function (but the amount of
  white spaces to remove is automatically detected)."""

  if amount == None:
    nindent = -1  # autodetect, default
  else:
    nindent = amount
    indent_whsp = " " * nindent

  strs = S.splitlines()
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


def str_snippet(S):
  """Standard processing for input snippet:
  Unindent a string and strip the trailing whitespaces (mainly for input
  file segments."""
  return str_unindent(S).rstrip()

def str_trunc_begin(S, L):
  """Returns a possibly truncated S (ellipsis added at the string's
  beginning) if the length of S is greater than L.
  L should be equal to or greater than 3 to be making sense."""
  if len(S) > L:
    return "..." + S[min(-L+3,0):]
  else:
    return S

def str_trunc_end(S, L):
  """Returns a possibly truncated S (ellipsis added at the string's
  ending) if the length of S is greater than L.
  L should be equal to or greater than 3 to be making sense."""
  if len(S) > L:
    return S[:max(L-3,0)] + "..."
  else:
    return S

def str_lstrip(S, substr):
  """Strips a prefix from S if it matches the string in `substr'.
  """
  # This is akin to ${VAR#$substr} in Bourne-shell dialect.
  if len(substr) > 0 and S.startswith(substr):
    return S[len(substr):]
  else:
    return S

def str_rstrip(S, substr):
  """Strips a suffix from S if it matches the string in `substr'.
  """
  # This is akin to ${VAR%$substr} in Bourne-shell dialect.
  if len(substr) > 0 and S.endswith(substr):
    return S[:-len(substr)]
  else:
    return S

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


# Internal variable: don't mess!
_str_fmt_heading_rx = None
def str_fmt_heading(fmt):
  """Replaces a printf-style formatting with one suitable for table heading:
  all non-string conversions are replaced with string conversions,
  preserving the minimum widths."""
  # Originally from: $PWQMC77/scripts/cost.py and later Cr2_analysis_cbs.py .
  #
  #_str_fmt_heading_rx = None # only for development purposes
  import re
  global _str_fmt_heading_rx
  if _str_fmt_heading_rx == None:
    # Because of complicated regex, I verbosely write it out here:
    _str_fmt_heading_rx = re.compile(r"""
      (
        %                 # % sign
        (?:\([^)]+\))?    # optional '(keyname)' mapping key
        [-+#0 hlL]*       # optional conversion flag
        [0-9*]*           # optional minimum field width
      )
      ((?:\.[0-9]*)?)     # optional precision
      [^-+#*0 hlL0-9.%s]  # not conv flag, dimensions, nor literal '%',
                          # nor 's' conversion specifiers
    """, re.VERBOSE)
  return _str_fmt_heading_rx.sub(r'\1s', fmt)


def str_grep(S, strs):
  """Returns a list of strings wherein the substring S is found."""
  return [s for s in strs if s.find(S) >= 0]

def str_igrep(S, strs):
  """Returns a list of the indices of the strings wherein the substring S
  is found."""
  return [i for (i,s) in enumerate(strs) if s.find(S) >= 0]
  #return [i for (s,i) in zip(strs,xrange(len(strs))) if s.find(S) >= 0]



def slice_str(s):
  return "%s:%s:%s" % (
    ifelse(s.start == None, "", str(s.start)),
    ifelse(s.stop == None, "", str(s.stop)),
    ifelse(s.step == None, "", str(s.step)),
  )


