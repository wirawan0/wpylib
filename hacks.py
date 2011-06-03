#
# $Id: hacks.py,v 1.1 2011-06-03 21:31:59 wirawan Exp $
#
# Created: 20110603
# Wirawan Purwanto
#
# Low-level python hacks to allow smooth operation of python
# codes.
#
#
import sys
import new

def make_unbound_instance_method(method):
  """Generates an unbound instance method from a possibly bound
  instance method."""
  return new.instancemethod(method.im_func, None, method.im_class)
