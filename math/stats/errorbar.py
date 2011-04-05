# $Id: errorbar.py,v 1.4 2011-04-05 19:20:55 wirawan Exp $
#
# Module wpylib.math.stats.errorbar
# Errorbar text handling for Python
#
# Created: 20081118
# Wirawan Purwanto
#
# Moved to wpylib, 20101007

import math
from math import sqrt
import os
import os.path
import re
import wpylib.shell_tools as sh

class regexp__aux(object):
  '''Auxiliary objects for routines below. Compiled into regexp objects
  for speed.'''
  # CHECKME FIXME: This class is NOT originally designed to be multithread-safe
  # since regex objects are shared between all threads.
  # To be thread-safe, the regex objects or aux classes may need to be
  # instantiated separately for each thread instance, or whatever else way
  # possible.
  init = False

  @staticmethod
  def initialize():
    R = regexp__aux
    # Each of the regex stuff below is a 2-tuple containing the regex
    # object and its associated function to extract the value/errbar pair
    # (as a tuple) from the re.Match object.
    #
    # Standard errorbar matcher (errorbar in parantheses), in the form of a tuple
    # The first element of the matcher is a regexp matcher object, and the
    # second element is a function to extract the (value,error) tuple from the
    # successful matching process.
    R.errbar = \
      (
        re.compile(r"([-+]?\d+)"    # leading digits with optional sign
                   r"((?:\.\d*)?)"  # optional digits after decimal point
                   r"\((\d+\.?\d*[Ee]?[-+]?\d*)\)" # errorbar in paranthesis
                   r"((?:[Ee][-+]?\d+)?)$"),
        lambda M: ( float(M.group(1) + M.group(2) + M.group(4)), # value = simple composition
                    # for errorbar:
                    # - must multiply with value's exponent
                    # - and account for decimal digits (if any)
                    float(M.group(3)) * float("1"+M.group(4)) * 10**(-max(len(M.group(2))-1, 0)) )
      )
    # Later additional matchers can be added here
    R.init = True

  @staticmethod
  def aux():
    R = regexp__aux
    if not R.init: R.initialize()
    return R

  @staticmethod
  def match(matcher, Str, rslt, flatten=False):
    '''Matches the string `Str' against the errorbar regexp pattern in `matcher[0]'.
    If it matches, the value and error are added to the `rslt' list.
    Depending on whether `flatten' is True or not, it is added as a tuple or as
    two elements, respectively, into the `rslt' list.'''
    # Note: matcher is an object like R.errbar above.
    m = matcher[0].match(Str)
    if m:
      if flatten:
        rslt.extend(matcher[1](m))
      else:
        rslt.append(matcher[1](m))
      return True
    else:
      return False

def expand(obj, convert_float=False, flatten=False):
  '''Expands compressed errorbar notation to two consecutive numbers
  (returned as a tuple).

  Input: The input can be a string, or a list of strings.

  Output:
  The list element that has the format of "VAL(ERR)" (or its scientific
  format twist) will be expanded into two numbers in the output list.
  All other elements will be passed "as is" to the output.
  Optionally, the non-float items can be force-converted to floats if
  the convert_float is set to True.
  '''
  if getattr(obj, "__iter__", False):
    iterable_inp = True
    objs = obj
  else:
    iterable_inp = False
    objs = ( obj, )

  rgx = regexp__aux.aux()

  rslt = []
  for o in objs:
    t = type(o)
    if t == int  or  t == float  or  t == complex:
      rslt.append(o)
    else:
      # Assume a string!
      o = o.strip()
      #m = rgx.errbar.match(o)
      if (rgx.match(rgx.errbar, o, rslt, flatten)):
        #print "match: errbar"
        pass
      elif convert_float:
        # Convert to float right away, store into the `rslt' list
        rslt.append(float(o))
        #rslt.append( (float(o),) )
      else:
        # Unless otherwise requested, the object will not be converted
        # to float:
        rslt.append(o)
  return rslt


COMPRESS_ERRORBAR_EXE = os.path.dirname(__file__) + "/compress_errorbar.exe"

def compress_errorbar_cxx(v, e, errdigits=2):
  """Temporary plug-hole measure to get python compress errorbars.
  Using a small C++ executable to perform the task."""
  #perl_lib_dir = sh.getenv("WORK_DIR", "HOME") + "/scripts"
  return sh.pipe_out((COMPRESS_ERRORBAR_EXE, str(v), str(e), str(errdigits))).strip()


class float_decomp(object):
  """Floating-point decomposer.
  We are assuming IEEE double precision here."""

  def __init__(self, val, decdigits=16):
    self.val = val
    V = "%+.*e" % (decdigits, val)
    self.sign = V[0]
    self.digits = V[1] + V[3:3+16]
    self.exp = int(V[20:])

  set = __init__



class errorbar(object):
  """A simple class holding a scalar value with an error bar.
  When converted to a float, its mean is returned.
  When converted to a string, its string representation is returned.
  which usually is meant to be a value with errorbar in parenthesis.
  This value is custom-made."""

  ebproc = staticmethod(compress_errorbar_cxx)

  def __init__(self, val, err, eb=None, ebproc=None):
    self.val = val
    self.err = err
    if ebproc != None:
      self.ebproc = ebproc
    if eb == None:
      self.eb = self.ebproc(val, err)
    else:
      self.eb = eb

  def __float__(self):
    return self.val
  def __float__(self):
    return self.val
  value = __float__
  mean = __float__
  def error(self):
    return self.err
  def __str__(self):
    if getattr(self, "eb", None):
      return self.eb
    else:
      return "%g +- %g" % (self.val, self.err)
  display = __str__
  def __repr__(self):
    return "errorbar(%s,%s,'%s')" % (self.val, self.err, self.display())
  def ebupdate(self):
    self.eb = self.ebproc(self.val, self.err)
  def copy(self):
    return self.__class__(self.val, self.err, self.eb, self.ebproc)
  # Some algebraic operations with scalars are defined here:
  def __mul__(self, y):
    """Scales by a scalar value."""
    return self.__class__(self.val*y, self.err*abs(y), ebproc=self.ebproc)
  __rmul__ = __mul__
  def __imul__(self, y):
    """Scales itself by a scalar value."""
    self.val *= y
    self.err *= abs(y)
    self.ebupdate()
    return self
  def __div__(self, y):
    """Divides by a scalar value."""
    return self.__class__(self.val/y, self.err/abs(y), ebproc=self.ebproc)
  def __idiv__(self, y):
    """Scales itself by a scalar value (division)."""
    self.val /= y
    self.err /= abs(y)
    self.ebupdate()
    return self

  def __add__(self, y):
    """Adds by a scalar value or another errorbar value.
    In the latter case, the uncertainty is assumed to be uncorrelated,
    thus we can use a simple formula to update the errorbar."""
    if isinstance(y, errorbar):
      return self.__class__(self.val+y.val,
                            sqrt(self.err**2 + y.err**2),
                            ebproc=self.ebproc)
    else:
      return self.__class__(self.val+y, self.err, ebproc=self.ebproc)
  __radd__ = __add__

  def __sub__(self, y):
    """Subtracts by a scalar value or another errorbar value.
    In the latter case, the uncertainty is assumed to be uncorrelated,
    thus we can use a simple formula to update the errorbar."""
    if isinstance(y, errorbar):
      return self.__class__(self.val-y.val,
                            sqrt(self.err**2 + y.err**2),
                            ebproc=self.ebproc)
    else:
      return self.__class__(self.val-y, self.err, ebproc=self.ebproc)

  def __rsub__(self, y):
    """Subtracts this errorbar value from a scalar value or another
    errorbar value.
    In the latter case, the uncertainty is assumed to be uncorrelated,
    thus we can use a simple formula to update the errorbar."""
    if isinstance(y, errorbar):
      return self.__class__(y.val-self.val,
                            sqrt(self.err**2 + y.err**2),
                            ebproc=self.ebproc)
    else:
      return self.__class__(y-self.val, self.err, ebproc=self.ebproc)

  @staticmethod
  def create_str(s):
    """Creates an errorbar object from an errorbar string."""
    eb = expand(s, convert_float=True)[0]
    return errorbar(*eb)


class errorbar_compressor(object):
  """Compressor for errorbar string."""
  def __init__(self):
    self.errdigits = 2
  def __call__(self, val, err, **args):
    errdigits = args.get("errdigits", self.errdigits)
    v = float_decomp(val)
    e = float_decomp(err, decdigits=errdigits)



#def errorbar_algebra


