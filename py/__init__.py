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

"""
wpylib.py module
Collection of low-level pythonic hacks

Instance method hacks
---------------------

make_unbound_instance_method::
make_unbound_method::

One possible reason of using these routines is to provide an
alterable calling point with different implementations--somewhat like
virtual methods, but something that can be changed dynamically
on-the-fly.
NOTE: The trick provided by wpylib.py.im_ref.im_ref class is
a better way to accomplish the same thing.


"""

def make_unbound_instance_method(method):
  """Generates an unbound instance method from a possibly bound
  instance method.
  """
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


def make_weakly_bound_method(method, instance):
  """Creates a bound instance method, where the instance is weakly
  referred.

  This trick is necessary if the bound method is to be attached
  to that instance's attribute list (e.g. via instance.__dict__),
  because otherwise a circular reference occurs:

     bound_method -> instance -> bound_method (via __dict__)

  CAVEAT: Know what you are doing! In general, this is a haram trick.
  We circumvent the standard class type-safety mechanism in python here:
  if the `method` actually belongs to a completely unrelated class,
  this routine still accepts it and allow the function to be called.
  """
  # NOTE: This is an identical trick to wpylib.py.im_ref.xbound_im_ref;
  # the latter (the OO interface) is better because
  # it does not need function closure, and that the object data is
  # easier to diagnose.
  from weakref import ref
  instance_ref = ref(instance)
  instance_cls = instance.__class__
  try:
    im_func, im_class = method.im_func, method.im_class
    #im_method = new.instancemethod(im_func, None, instance_cls)
  except AttributeError:
    im_func = method
    # Assume this is a function defined outside a class, which is then
    # injected into this instance.
    # The first argument must be the usual `self` argument.
    return lambda *args, **kwargs: method(instance_ref(), *args, **kwargs)

  return lambda *args, **kwargs: im_func(instance_ref(), *args, **kwargs)


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


