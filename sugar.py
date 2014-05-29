#!/usr/bin/ipython -pylab
#
# $Id: sugar.py,v 1.9 2011-03-10 20:16:58 wirawan Exp $
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
import weakref

def is_iterable(x):
  """Checks if an object x is iterable.
  It checks only for the presence of __iter__, which must exist for
  container objects.
  Note: we do not consider non-containers such as string and unicode as
  `iterable'; this behavior is intended.
  """
  return hasattr(x, "__iter__")

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
  """Returns a shallow copy of the subset of a given dict (or a dict-like
  object) with a given set of keys.
  The return object is a dict.
  No keys may be missing from Dict.

  Example: if d = {'abc': 12, 'def': 7, 'ghi': 32, 'jkl': 98 }
  then dict_slice(d, 'abc', 'ghi') will yield {'abc': 12, 'ghi': 32 }
  """
  return dict([ (k, Dict[k]) for k in keys ])

def dict_islice(Dict, *keys):
  """Returns a shallow copy of the subset of a given dict (or an otherwise
  hashable object) with a given set of keys.
  The return object is a dict.
  This is similar to dict_slice, except that missing keys in
  Dict will be ignored.
  """
  # This is fancy but we require Dict to have keys() function:
  #return dict([ (k, Dict[k]) for k in (set(keys) & set(Dict.keys())) ])
  # use this one instead, which is milder requirement:
  return dict([ (k, Dict[k]) for k in keys if (k in Dict) ])

def dict_join(*dicts):
  """Join multiple dicts into one, updating duplicate keys from left-to-right
  manner.
  Thus the items from the rightmost dict will take precedence."""

  rslt = {}
  for d in dicts:
    rslt.update(d)
  return rslt

def dict_defval(p, key, val):
  """For a dict-like object, sets a default value for the given key,
  if that has not been defined in the object."""
  if key not in p: p[key] = val

def dict_defvals(p, q):
  """For a dict-like object, sets multiple default values for the given keys
  (q is an input dict containing the defaults)."""
  for qk in q:
    dict_defval(p, qk, q[qk])

def list_join(*L):
  r = []
  for i in L:
    r += i
  return r


def zip_gen(*L):
  """Generator version of the built-in zip() function.
  Used so that the all the loop iterations are not invoked before
  the main `for' statement is invoked (e.g. if memory is a concern
  when generating the list--this method does not generate any list).
  Performance could be slightly slower than the original zip function,
  though."""
  L_iters = [ i.__iter__() for i in L ]
  while True:
    yield tuple([ L1.next() for L1 in L_iters ])


class ranges_type:
  """This class is to provide dirty magic to specify piecewice slices
  of one-dimensional ranges.
  To this end, use the `ranges' instance already defined in this module.
  Example:

     >>> ranges[1]
     [1]

     >>> ranges[1, 4, 7, 9]
     [1, 4, 7, 9]

     >>> ranges[1:7, 9:11]
     [1, 2, 3, 4, 5, 6, 9, 10]

     >>> rr[1,4,7,9,[2,3,2]]      # it even works like this!
     [1, 4, 7, 9, 2, 3, 2]

  The key is, anything 1-D will be flattened out. So be careful.
  Slices must have defined starting and ending points.
  Undefined step will be reinterpreted as unit incremental step.
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


class Parameters(dict):
  """A standardized way to define and/or pass parameters (with possible
  default values) among routines.
  This provides a very flexible lookup scheme for a parameter with a given name.
  It scans through the namescopes (dicts) in a deterministic and sequential
  order, returning the first one found.
  This, hopefully, gets rid of kitchen-sink parameter passing, at least from
  programmer's point of view.

  WARNING: This object is derived from python dict with ALL method names removed,
  so as to avoid collosion of these names with user-defined parameters with the
  same name.
  Names reserved by this class begin and end with an underscore.
  Names reserved by python begin and end with two underscores.
  So, avoid specifying parameters with both leading and trailing underscores.
  WARNING: Be careful modifying this class; endless recursive calls are
  possible.


  Some uses:

    def stuff(params=None, **kwparams):
      # `params' defines the standard way of passing parameters, which is
      # via a Parameters object.
      # `kwparams' determine a quick way of temporarily overriding a parameter
      # value.
      prm = Parameters(kwparams, params, global_defaults)
      for step in prm.steps:
         ...

  Parameters can also be updated in this way:

    a = Parameters(...)
    updates = {'nblk': 7, 'nbasis': 32}
    a += updates

  or, to call a function with a combination of parameters:

  Reserved private members of the Parameters object:
  * _no_null_ = (True/False, default False) look for non-null (non-"None") values
    in all the parameter lists until one is found.
  * _list_ = (list) the list of parameter dicts to search from.
  * _kwparam_ = (string, default "_opts_") the default name of the function argument
    that will hold excess named arguments.
    Used in _create_() function below.
    If this is set to None, we will not use this feature.
  * _userparam_ = (string, default "_p") the default name of the function argument
    that will contain Parameters-like object given by the user.
    Used in _create_() function below.
    If this is set to None, we will not use this feature.

  The most overriding list of parameters, as provided via excess key=value
  arguments in creating this Parameters object, are stored in "self".
  """

  class _self_weakref_:
    """A minimal proxy object, just enough to get a weakref to the 'self' object
    below to be accesible via a few dict-like lookup mechanisms.
    Also needed to avoid recursive `in' and [] get operators below."""
    def __init__(self, obj):
      self.ref = weakref.ref(obj)
    def __contains__(self, key):
      return dict.__contains__(self.ref(), key)
    def __getitem__(self, key):
      return dict.__getitem__(self.ref(), key)

  def __init__(self, *_override_dicts_, **_opts_):
    """
    Creates a new Parameters() object.
    The unnamed arguments are taken to be dict-like objects from which we will
    search for parameters.
    We silently ignore `None' values which are passed in this way.
    Parameters will be searched in left-to-right order of these dict-like
    objects.
    Then the keyword-style arguments passed on this constructor will become
    the most overriding options.

    The dict-like objects must contain the following functionalities:
    * for key in obj:
        ...
      (in other words, the __iter__() method).
    * key in obj
    * obj[key]
    That's it!

    Example:
      defaults = { 'walltime': '6:00:00', 'nwlk': 100 }
      # ...
      p = Parameters(defaults, walltime='7:00:00', nblk=300)

    Then when we want to use it:
      >> p.nwlk
      100
      >> p.walltime
      '7:00:00'
      >> p.nblk
      300

    Options:
    * _no_null_ = if True, look for the first non-None value.
    * _flatten_ = will flatten the key-value pairs.
      Note that this may make the Parameters object unnecessarily large in memory.
      Additionally, this means that the updates in the contents of the dicts
      passed as the _override_dicts_ can no longer be reflected in this object
      because of the shallow copying involved here.
    * _kwparam_
    * _userparam_
    At present, the `flatten' attribute will not be propagated to the child
    Parameters objects created by this parent object.
    """

    # Remove standard dict procedure names not beginning with "_":
    for badkw in self.__dict__:
      if not badkw.startswith("_"):
        del self.__dict__[badkw]
    # Store the user-defined overrides in its own container:
    dict.clear(self)
    if _opts_.get('_flatten_', False):
      for p in _override_dicts_:
        dict.update(self, p)
      dict.update(self, _opts_)
    else:
      dict.update(self, _opts_)
      # WARNING: Using weakref proxy is important:
      # - to allow clean deletion of Parameters() objects when not needed
      # - to avoid recursive 'in' and 'get[]' operators.
      paramlist = (Parameters._self_weakref_(self),) + _override_dicts_ #+ tuple(deflist))
      #paramlist = (self,) + _override_dicts_ #+ tuple(deflist))
      self.__dict__["_list_"] = [ p for p in paramlist if p != None ]
    self.__dict__["_kwparam_"] = _opts_.get("_kwparam_", "_opts_")
    self.__dict__["_userparam_"] = _opts_.get("_userparam_", "_p")
    self.__dict__["_no_null_"] = ifelse(_opts_.get("_no_null_"), True, False)
    # Finally, filter out reserved keywords from the dict:
    for badkw in ("_kwparam_", "_userparam_", "_no_null_", "_flatten_"):
      #if badkw in self: del self[badkw] -- recursive!!!
      if dict.__contains__(self,badkw): del self[badkw]
  def _copy_(self):
    """Returns a copy of the Parameters() object."""
    return Parameters(_no_null_=self._no_null_,
                      _kwparam_=self._kwparam_,
                      _userparam_=self._userparam_,
                      *self._list_[1:],
                      **self)
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
    # Otherwise: -- but most likely this will return attribute error:
    return dict.__getattribute__(self, key)
  def __setattr__(self, key, value):
    """This method always sets the value on the object's dictionary.
    Values set will override any values set in the input parameter lists."""
    self[key] = value
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
  #def __setitem__(self, key, value):  # -- inherited from dict
  #  self._prm_[key] = value

  # TODO in the future for iterative accesses:
  # -- not that essential because we know the name of
  # the parameters we want to get:
  #def __iter__(self):  # -- inherited from dict
  #  """Returns the iterator over key-value pairs owned by this object.
  #  This does NOT return key-value pairs owned by the _override_dicts_.
  #  """
  #  return self._prm_.__iter__()
  #def _iteritems_(self):
  #  return self._prm_.iteritems()
  def _update_(self, srcdict):
    """Updates the most overriding parameters with key-value pairs from
    srcdict.
    Srcdict can be either a dict-derived object or a Parameters-derived
    object."""
    dict.update(self, srcdict)
  def __add__(self, srcdict):
    """Returns a copy of the Parameters() object, with the most-overriding
    parameters updated from the contents of srcdict."""
    rslt = self._copy_()
    rslt._update_(srcdict)
    return rslt
  def _create_(self, kwparam=None, userparam=None, *defaults):
    """Creates a new Parameters() object for standardized function-level
    parameter lookup.
    This routine *must* be called by the function where we want to access these
    parameters, and where some parameters are to be overriden via function
    arguments, etc.

    The order of lookup is definite:
    * local variables of the calling subroutine will take precedence
    * the excess keyword-based parameters, 
    * user-supplied Parameters-like object, which is 
    * the dicts (passed in the `defaults' unnamed parameter list) is searched
      *last*.
      I suggest that this is used only as a last-effort safety net.
      Ideally, the creating Parameters object itself should contain the
      'factory defaults', as shown in the example below.

    class Something(object):
      def __init__(self, ...):
        # self.opts holds the factory default
        self.opts = Parameters()
        self.opts.cleanup = True # example
    
      def doit(self, src=None, info=None,
               _defaults_=dict(src="source.txt", info="INFO.txt", debug=1),
               **_opts_):
        # FIXME: use self-introspection to reduce kitchen-sink params here:
        p = self.opts._create_(_defaults_)
        #   ^ This will create an equivalent of:
        # Parameters(locals(), _opts_, _opts_.get('opts'), self.opts, _defaults)
        # Now use it:
        if p.cleanup:
          ... do something
    """
    # Look up the stack of the calling function in order to retrieve its
    # local variables
    from inspect import stack
    caller = stack()[1][0] # one frame up; element-0 is the stack frame

    if kwparam == None: kwparam = self._kwparam_
    if userparam == None: userparam = self._userparam_

    # local variables will be the first scope to look for
    localvars = caller.f_locals
    contexts = [ localvars ]
    # then _opts_ excess-keyword parameters (see example of doit() above)
    if kwparam in localvars:
      _opts_ = localvars[kwparam]
      contexts.append(_opts_)
    else:
      _opts_ = {}
    # then opts, an explicitly-defined argument which contain a set of parameters
    if userparam in localvars:
      opts = localvars[userparam]
      contexts.append(opts)
    else:
      opts = {}
      if userparam in _opts_:
        contexts.append(_opts_[userparam])

    # then this own Parameters data will come here:
    contexts.append(self)

    # then any last-minute defaults
    contexts += [ d for d in defaults ]

    # Now construct the Parameters() class for this calling function:
    return Parameters(_kwparam_=kwparam, _userparam_=userparam, *contexts)

  #def __dict__(self):
  #  return self._prm_
