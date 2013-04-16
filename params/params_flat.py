# $Id: params_flat.py,v 1.6 2011-09-19 20:06:45 wirawan Exp $
#
# wpylib.params.params_flat module
# Created: 20100930
# Wirawan Purwanto

import inspect  # for self-introspection of call stack
import weakref
from wpylib.sugar import ifelse

"""
This module specializes in handling parameters that are defined in
a 'flat' namespace, i.e. no nested name scoping.

NOTE:

I might explore the idea of nested parameter space later, should a need
for that arise.
This nested space is much more complicated, and will require
copy-on-write kind of support to reduce recursively copying parameters
whenever the set of parameters is passed from one subroutine to another.

"""

class ActiveReadValue(object):
  """Special class to mark a Parameters' member `active', i.e., executable.
  When this member is accessed in a `read' manner, the function will be
  executed with the containing Parameters object as the sole argument.
  When this member is accessed in a `write' manner, however, the usual
  replacement of value will take place.

  This is useful for macro processing, automatically computed values, etc.

  Example of use:

  PP = Parameters(root="/usr/local/lib", basename="libfoo", ext=".so.3", \
                  fullpath=ActiveReadValue(lambda p : \
                    os.path.join(p.root, p.basename + p.ext)))

  print PP.fullpath  # gives "/usr/local/lib/libfoo.so.3"
  PP.ext = ".a"
  print PP.fullpath  # gives "/usr/local/lib/libfoo.a"
  """
  def __init__(self, function):
    if not hasattr(self, "__call__"):
      raise TypeError, \
        ("Initializing ActiveReadValue object with a non-callable argument")
    self._function = function
  def __call__(self, p):
    return self._function(p)



class Parameters(dict):
  """A standardized way to define and/or pass parameters (with possible
  default values) among routines.

  This class provides a very flexible lookup scheme for a parameter with
  a given name.
  It scans through the namescopes (dicts) in a deterministic and sequential
  order, returning the first one found.
  This, hopefully, gets rid of kitchen-sink parameter passing, at least from
  programmer's point of view.

  WARNING: This object is derived from python dict with ALL method names removed, (#FIXME# Not true yet)
  so as to avoid collision of these names with user-defined parameters with the
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
    #FIXME# ^^^ right now this does not operate in-place, but
    #FIXME# returns a new Parameters object, which may not be desirable

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
    def __iter__(self):
      return dict.__iter__(self.ref())

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
    * _flatten_ = will flatten the key-value pairs from the overriding dicts
      into the self object.
      Note that this may make the Parameters object unnecessarily large in memory.
      Additionally, this means that the updates in the contents of the dicts
      passed as the _override_dicts_ can no longer be reflected in this object
      because of the shallow copying involved here.
      At present, the `_flatten_' attribute will not be propagated to the child
      Parameters objects created by this parent object.
    * _kwparam_ = the name of the excess argument dict to look for in the
      function argument list (default: `_opts_').
    * _userparam_ = the name of the explicitly defined user-defined parameter
      (of a dict type) in the function argument list (default: `_p').
    * _localvars_ = set to true to include function local variables by their names
      in the lookup chain of the new Parameters object created by _create_()
      method below.
      See the documentation in _create_() method for cautionary notes.
    """

    # Remove standard dict procedure names not beginning with "_":
    for badkw in self.__dict__:
      if not badkw.startswith("_"):
        del self.__dict__[badkw]
    # Store the user-defined overrides in its own container:
    dict.clear(self)
    if _opts_.get('_flatten_', False):
      #FIXME# if p is a Parameters object, then we must recursively flatten it too
      for p in _override_dicts_[::-1]:
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
    self.__dict__["_localvars_"] = ifelse(_opts_.get("_localvars_"), True, False)
    # Finally, filter out reserved keywords from the dict:
    for badkw in ("_kwparam_", "_userparam_", "_no_null_", "_flatten_", \
      "_localvars_"):
      #if badkw in self: del self[badkw] -- recursive!!!
      if dict.__contains__(self,badkw): del self[badkw]
  def _copy_(self):
    """Returns a (shallow) copy of the Parameters() object."""
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
        try:
          v = ov[key]
          if v == None: continue
        except KeyError:
          pass
        else:
          # (NOTE.1)
          # Execute the value activation here so if it raises a KeyError
          # exception, it won't be misconstrued as the parameter name lookup
          # failure in the try block above.
          return self._ActiveReadValue_(v)
    else:
      for ov in self._list_:
        try:
          v = ov[key]
        except KeyError:
          pass
        else:
          # See (NOTE.1)
          return self._ActiveReadValue_(v)
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
        try:
          v = ov[key]
          if v == None: continue
        except KeyError:
          pass
        else:
          # See (NOTE.1)
          return self._ActiveReadValue_(v)
    else:
      for ov in self._list_:
        try:
          v = ov[key]
        except KeyError:
          pass
        else:
          # See (NOTE.1)
          return self._ActiveReadValue_(v)
    raise KeyError, "Cannot find parameter `%s'" % key
  #def __setitem__(self, key, value):  # -- inherited from dict
  #  self._prm_[key] = value
  def _ActiveReadValue_(self, val):
    """Private subroutine for evaluating `active' members."""
    #FIXME# Value overrides specified in enclosing Parameters object instance
    # cannot be searched from this (enclosed) instance.
    if isinstance(val, ActiveReadValue):
      return val(self)
    else:
      return val

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
  def _get_(self, key, default=None):
    """Nested version of dict.get for this Parameters object."""
    try:
      return self[key]
    except KeyError:
      return default

  def _all_keys_(self, sort=True):
    """Returns a list of all keys containing in the parameter space.

    Warning: This can be an expensive operation!"""
    K = set()
    _list_ = self.__dict__["_list_"]
    for D in _list_:
      try:
        K.update(D.keys())
      except:
        K.update(D.ref().keys())
    K_list = [ k for k in K ]
    if sort:
      K_list.sort()
    return K_list

  def _flatten_(self, sort=True):
    """Returns a flatten dict of all the (most overriding) key-value pairs
    in the parameter space.

    Warning: This can be an expensive operation!"""
    K = dict()
    _list_ = self.__dict__["_list_"]
    for D in _list_[::-1]:
      #FIXME# if D is a Parameters object then we must recursively flatten it too
      K.update([ (k,D[k]) for k in D ])
    return K

  def _update_(self, srcdict):
    """Updates the most overriding parameters with key-value pairs from
    srcdict.
    Srcdict can be either a dict-derived object or a Parameters-derived
    object.
    WARNING: As for now the additional dicts in the search list are *not*
    updated into the "self" dict.
    """
    dict.update(self, srcdict)
  def _append_(self, *dicts):
    """Appends dictionary search path to this Parameters object.
    """
    self.__dict__["_list_"] += list(dicts)
  def _prepend_(self, *dicts, **_options_):
    """Prepends dictionary search path to this Parameters object.
    This will not override the first dict, which is its own dictionary object.
    If you really want to do that (BEWARE, know what you are doing!),
    you will have to specify override_me=True in the argument.
    """
    _list_ = self.__dict__["_list_"]
    if not _options_.get("override_me", False):
      self.__dict__["_list_"] = [ _list_[0] ] + list(dicts) + _list_[1:]
    else:
      self.__dict__["_list_"] = list(dicts) + _list_
  def __add__(self, srcdict):
    """Returns a copy of the Parameters() object, with the most-overriding
    parameters updated from the contents of srcdict."""
    # FIXME: this operation looks counterintuitive; may want to consider
    # using "<<" alternate operator naming if we ever, ever use this.
    # (And similarly, "<<=".
    rslt = self._copy_()
    rslt._update_(srcdict)
    return rslt
  __or__ = __add__  # DON'T!
  def _create_(self, *defaults, **_options_):
    """Creates a new Parameters() object for standardized function-level
    parameter lookup.
    This routine *must* be called by the function where we want to use these
    parameters, and their values can be overridden via function
    arguments, etc.

    The order of the lookup is deterministic:
    * local variables of the calling subroutine will take precedence
      (if _localvars_ is set to True)
    * the excess keyword-based parameters (given by pre-set variable name,
      which by default is "_opts_")
    * user-supplied Parameters-like object, which by default is the
      keyword-based parameter "_p")
    * the dicts (passed in the `defaults' unnamed parameter list) is searched
      *last*.
      I suggest that this is used only as a last-effort safety net.
      Ideally, the creating Parameters object itself should contain the
      'factory defaults', as shown in the example below.

    class Something(object):
      def __init__(self, ...):
        # self.opts holds the factory default
        self.opts = Parameters()
        self.opts.cleanup = True # an example parameter

      def doit(self, src=None, info=None,
               _defaults_=dict(src="source.txt", info="INFO.txt", debug=1),
               **_opts_):
        # FIXME: use self-introspection to reduce kitchen-sink params here:
        p = self.opts._create_(_defaults_)
        #   ^ This will create an equivalent of:
        # Parameters(_opts_, _opts_.get('_p'), self.opts, _defaults_)
        # Now use it:
        if p.cleanup:
          self.do_the_cleanup() # ... do something

    * Options accepted by the _create_ function are:
      - _kwparam_ (string) = name of excess-parameter dict.
        Default: None; refer back to the object's _kwparam_ attribute.
      - _userparam_ (string) = name of explicitly-given parameter dict
        Default: None; refer back to the object's _userparam_ attribute.
      - _localvars_ (boolean) = whether to include the local vars in the
        lookup chain. Default: None; refer back to the object's
        _localvars_ attribute.

    Cautions for using `_localvar_` option:
    1) The default is False because it can be very confusing!
       We just have no control on what local variables would be involved
       in a function and the sheer potential of creating vars with the same name
       as the value we want to look up---all will open up to infinite possibility
       of surprises.
    2) At present, the value of the `_localvars_' option will not be
       propagated to the Parameters objects created by this parent
       object.
    3) Only local variables defined up to the calling of the _create_() method
       will be captured.
       Any new local variables or update to the variable values will not be
       reflected in the Parameters object created by this method.
       (See params_flat_test.py, test2 and test2b routines.)
    """
    # Look up the stack of the calling function in order to retrieve its
    # local variables
    from inspect import stack
    caller = stack()[1][0] # one frame up; element-0 is the stack frame
    _kwparam_ = _options_.get("_kwparam_", None)
    _userparam_ = _options_.get("_userparam_", None)
    _localvars_ = _options_.get("_localvars_", None)

    if _kwparam_ == None: _kwparam_ = self._kwparam_
    if _userparam_ == None: _userparam_ = self._userparam_
    if _localvars_ == None: _localvars_ = self._localvars_

    # local variables will be the first scope to look for
    localvars = caller.f_locals
    #print "?? localvars = ", _localvars_
    if _localvars_:
      contexts = [ localvars ]
    else:
      contexts = []
    # then _opts_ excess-keyword parameters (see example of doit() above)
    if _kwparam_ in localvars:
      _opts_ = localvars[_kwparam_]
      if _opts_ != None:
        # add this minimal check for a dict-like behavior rather
        # than encountering a strange error later
        if not hasattr(_opts_, "__getitem__") or not hasattr(_opts_, "__contains__"):
          raise TypeError, \
            ("The keyword parameter (variable/parameter `%s' in function `%s')" +
             " is not a dict-like object)") \
            % (_kwparam_, caller.f_code.co_name)
        contexts.append(_opts_)
    else:
      _opts_ = {}
    # then opts, an explicitly-defined argument which contain a set of parameters
    if _userparam_ in localvars:
      opts = localvars[_userparam_]
      if opts != None:
        # add this minimal check for a dict-like behavior rather
        # than encountering a strange error later
        if not hasattr(opts, "__getitem__") or not hasattr(opts, "__contains__"):
          raise TypeError, \
            ("The user parameter (variable/parameter `%s' in function `%s')" +
             " is not a dict-like object)") \
            % (_userparam_, caller.f_code.co_name)
        contexts.append(opts)
    else:
      if _userparam_ in _opts_:
        opts = _opts_[_userparam_]
        if opts != None:
          # add this minimal check for a dict-like behavior rather
          # than encountering a strange error later
          if not hasattr(opts, "__getitem__") or not hasattr(opts, "__contains__"):
            raise TypeError, \
              ("The user parameter (variable/parameter `%s' in function `%s')" +
               " is not a dict-like object)") \
              % (_userparam_, caller.f_code.co_name)
          contexts.append(opts)

    # then this own Parameters data will come here:
    contexts.append(self)

    # then any last-minute defaults
    contexts += [ d for d in defaults ]

    # Now construct the Parameters() class for this calling function:
    return Parameters(_kwparam_=self._kwparam_, _userparam_=self._userparam_, *contexts)

  #def __dict__(self):
  #  return self._prm_


