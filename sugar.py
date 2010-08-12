#!/usr/bin/ipython -pylab
#
# $Id: sugar.py,v 1.5 2010-08-12 19:35:55 wirawan Exp $
#
# Created: 20100121
# Wirawan Purwanto
#
# Syntactic sugar for python programming. May not be efficient, but many
# of these tools are nice for quick-and-dirty programming.
# Beware of their caveats!
#
#
import sys

def ifelse(cond, trueval, *args):
  """An alternative to python's own ternary operator, but with multiple
  conditions to test (like chained if-else-if-else... which is found in
  e.g. m4 language).
  This is of course only a syntactic sugar with its inefficiency and
  dangers (all expressions are evaluated before choosing which one is to
  select). So, beware!"""
  if cond:
    return trueval
  else:
    i = 0
    while i+1 < len(args):
      if args[i]: return args[i+1]
      i += 2

    if i < len(args): return args[i]

  return None # Fallback solution: "None"


if sys.version_info < (2,4):
  def sorted(List):
    rslt = [ L for L in List ] # == L.copy()
    rslt.sort()
    return rslt
else:
  #print dir(globals())
  sorted = sorted

#print dir(globals())

def dict_slice(Dict, *keys):
  """Returns a shallow copy of the subset of a given dict (or an otherwise
  hashable object) with a given set of keys.

  Example: if d = {'abc': 12, 'def': 7, 'ghi': 32, 'jkl': 98 }
  then dict_slice(d, 'abc', 'ghi') will yield {'abc': 12, 'ghi': 32 }
  """
  return dict([ (k, Dict[k]) for k in keys ])

def dict_join(*dicts):
  """Join multiple dicts into one, updating duplicate keys from left-to-right
  manner.
  Thus the items from the rightmost dict will take precedence."""

  rslt = {}
  for d in dicts:
    rslt.update(d)
  return rslt

def list_join(*L):
  r = []
  for i in L:
    r += i
  return r


class ranges_type:
  """This class is to provide dirty magic to specify piecewice slices
  of one-dimensional ranges.
  To this end, use the `ranges' instance already defined in this module.
  Example:

     >>> ranges[1]
     [1]

     >>> ranges[1, 4, 7, 9]
     [1]

     >>> ranges[1:7, 9:11]
     [1, 2, 3, 4, 5, 6, 9, 10]

     >>> rr[1,4,7,9,[2,3,2]]      # it even works like this!
     [1, 4, 7, 9, 2, 3, 2]

  The key is, anything 1-D will be flattened out. So be careful.
  Slices must have defined starting and ending points.
  Undefined step will be reinterpreted as unit step.
  As always: endpoints are not included when using the slicing syntax.
  """
  def expand_range(self, rr):
    pass
  def __getitem__(self, rr):
    if "__iter__" in dir(rr):
      return list_join(*[ self[r] for r in rr ])
    elif isinstance(rr, slice):
      if rr.step == None:
        step = 1
      else:
        step = rr.step
      return range(rr.start, rr.stop, step)
    else:
      return [rr]

ranges = ranges_type()


class Parameters(object):
  """A standardized way to define and/or pass parameters (with possible
  default values) among routines.
  This provides a very flexible lookup scheme for a parameter with a given name.
  It scans through the namescopes (dicts) in a deterministic order, returning
  the first one found.
  This, hopefully, gets rid of kitchen-sink parameter passing, at least from
  programmer's point of view.

  WARNING: This object is derived object instead of python dict, so as to avoid
  messing with standard dict names.
  Names reserved by this class begin and end with an underscore.
  Names reserved by python begin and end with two underscores.
  So, avoid specifying parameters with both leading and trailing underscores.

  Some uses:

    def stuff(params=None, **kwparams):
      # `params' defines the standard way of passing parameters, which is
      # via a Parameters object.
      # `kwparams' determine a quick way of temporarily overriding a parameter
      # value.
      prm = Parameters(kwparams, params, global_defaults)
      for step in prm.steps:
         ...

  Reserved members:
  * _no_null_ = (True/False, default False) look for non-null values in all
    the parameter lists until one is found.
  * _list_ = (list) the list of parameter dicts to search from.
  * _prm_ = (dict) the most overriding list of parameters.
  """
  def __init__(self, *_override_dicts_, **_opts_):
    """
    Again, keyword arguments passed here will become the most overriding options.
    """
    prm = _opts_
    self.__dict__["_no_null_"] = ifelse(_opts_.get("_no_null_"), True, False)
    self.__dict__["_prm_"] = prm
    paramlist = (prm,) + _override_dicts_ #+ tuple(deflist))
    self.__dict__["_list_"] = [ p for p in paramlist if p != None ]
  def __getattr__(self, key):
    """Allows options to be accessed in attribute-like manner, like:
        opt.niter = 3
    instead of
        opt['niter'] = 3
    """
    if self._no_null_:
      for ov in self._list_:
        if key in ov and ov[key] != None: return ov[key]
    else:
      for ov in self._list_:
        if key in ov: return ov[key]
    # Otherwise:
    return object.__getattribute__(self, key)
  def __setattr__(self, key, value):
    """This method always sets the value on the object's dictionary.
    Values set will override any values set in the input parameter lists."""
    self._prm_[key] = value
  def __contains__(self, key):
    if self._no_null_:
      for ov in self._list_:
        if key in ov and ov[key] != None: return True
    else:
      for ov in self._list_:
        if key in ov: return True
    return False
  def __getitem__(self, key):
    if self._no_null_:
      for ov in self._list_:
        if key in ov and ov[key] != None: return ov[key]
    else:
      for ov in self._list_:
        if key in ov: return ov[key]
    raise KeyError, "Cannot find parameter `%s'" % key
  def __setitem__(self, key, value):
    self._prm_[key] = value
  # TODO in the future for iterative accesses:
  # -- not that essential because we know the name of
  # the parameters we want to get:
  #def __iter__(self):
  #  return self._prm_.__iter__
  #def _iteritems_(self):
  #  return self._prm_.iteritems()
  def _update_(self, srcdict):
    self._prm_.update(srcdict)
  def _create_(self, kwparams="_opts_", userparams="opts", *defaults):
    """Creates a new Parameters() object for standardized function-level
    parameter lookup.
    This routine *must* be called by the function where we want to access these
    parameters, and where some parameters are to be overriden via function arguments,
    etc.

    The order of lookup is definite:
    *

    class Something(object):
      def __init__(self, ...):
        self.opts = Parameters()
        self.opts.cleanup = True # example
    
      def doit(self, src=None, info=None,
               _defaults_=dict(src="source.txt", info="INFO.txt", debug=1),
               **_opts_):
      # FIXME: use self-introspection to reduce kitchen-sink params here:
      p = self.opts._create_()
      #   ^ This will create an equivalent of:
      # Parameters(locals(), _opts_, _opts_.get('opts'), self.opts, _defaults)
    """
    # Look up the stack of the calling function in order to retrieve its
    # local variables
    from inspect import stack
    caller = stack()[1][0] # one frame up; element-0 is the stack frame

    # local variables will be the first to look for
    localvars = caller.f_locals
    contexts = [ localvars ]
    # then _opts_ excess-keyword parameters (see example of doit() above)
    if kwparams in localvars:
      _opts_ = localvars[kwparams]
      contexts.append(_opts_)
    else:
      _opts_ = {}
    # then opts, an explicitly-defined argument carrying set of parameters
    if userparams in localvars:
      opts = localvars[userparams]
      contexts.append(opts)
    else:
      opts = {}
      if userparams in _opts_:
        contexts.append(_opts_[userparams])

    # then this own Parameters data will come here:
    contexts.append(self)

    # then any defaults
    contexts += [ d for d in defaults ]

    # Now construct the Parameters() class for this calling function:
    return Parameters(*contexts)


