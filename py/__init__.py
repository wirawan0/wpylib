# $Id: __init__.py,v 1.2 2011-08-31 18:26:18 wirawan Exp $
#
# wpylib.py module
# Created: 20110608
# Wirawan Purwanto
#
# Module space for advanced tools requiring low-level python hacks.
#

import sys
import new


def make_unbound_instance_method(method):
  """Generates an unbound instance method from a possibly bound
  instance method."""
  return new.instancemethod(method.im_func, None, method.im_class)


def make_unbound_method(method):
  """Generates an unbound instance method from a possibly bound
  instance method, or even user-defined function.
  This is useful for injecting external, completely unrelated function
  as an instance procedure into a class, without having to subclass
  the whole thing.
  CAVEAT: This is a haram trick. Know what you are doing."""
  try:
    return new.instancemethod(method.im_func, None, method.im_class)
  except AttributeError:
    # Assume this is a static method or user-defined external method
    # injected into this class.
    return method


def function_name(f):
  """Returns the given name of a function (or callable object)."""
  try:
    # Regular function
    return f.func_name
  except:
    pass
  try:
    # Instance method
    return "%s.%s" % (f.im_class, f.im_func.func_name)
  except:
    pass
  # Callable class instance:
  return f.__class__.__name__


