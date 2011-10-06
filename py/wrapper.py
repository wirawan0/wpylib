# $Id: wrapper.py,v 1.1 2011-10-06 19:15:05 wirawan Exp $
#
# wpylib.py.wrapper module
# Created: 20110608
# Wirawan Purwanto
#
# Wrapper base class.
# Used for automatic wrapping of (especially) methods to
# dispatch it to a host of object possibilities.
#


class wrapper_base(object):
  """Wrapper or proxy object to provide uniform API to other routines,
  etc.

  This class allows dirty tricks such as injecting external functions
  to accomplish certain required tasks in object-oriented manner.
  If using external procedure, it must be callable with "self" as
  its first argument.

  Reserved attributes:
  * _obj_ = the wrapped object
  * _procnames_[:] = method names to wrap automatically.
  * _obj_path_[:] = list of objects (instances) from which to look
    for the methods.
  * _set_obj_path_() = object method to define what objects to be
    included in the object path (_obj_path_).

  """
  def __init__(self, obj):
    """Creates a wrapper."""
    self._obj_ = obj
    if hasattr(self, '_set_obj_path_'):
      self._set_obj_path_()
    else:
      self._obj_path_ = [ obj ]

  def _autoset_proc_(self, procname, extproc=None):
    from wpylib.py import make_unbound_method
    from wpylib.py.im_weakref import im_ref
    from weakref import ref

    procname_ = procname + '_'
    procname_proc = procname + '_proc'
    if hasattr(self, procname_proc):
      # In case the derived-class has the procedure, we will use
      # that.
      setattr(self, procname, im_ref(getattr(self, procname_proc)))
    else:
      for o in self._obj_path_:
        if hasattr(o, procname):
          setattr(self, procname, im_ref(getattr(o, procname)))
          return
      # May implement a global fallback hook here?
      pass

