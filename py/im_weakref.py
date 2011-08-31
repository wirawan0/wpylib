# -*- python -*-
#
# $Id: im_weakref.py,v 1.1 2011-06-08 15:50:07 wirawan Exp $
#
# wpylib.py.im_weakref
# Created: 20110607
# Wirawan Purwanto
#
# Advanced hack tools for python: weakref proxy class for instance-method.
#

"""
wpylib.py.im_weakref

Complement of weakref's weak reference for an instance method
(whether bound or unbound).

Original-source: Linux Screen Reader project
Copied-from: http://mindtrove.info/python-weak-references/
Date: 20110607
"""

import weakref, new

class im_ref(object):
  '''
  Our own proxy object which enables weak references to bound and unbound
  methods and arbitrary callables. Pulls information about the function,
  class, and instance out of a bound method. Stores a weak reference to the
  instance to support garbage collection.

  @organization: IBM Corporation
  @copyright: Copyright (c) 2005, 2006 IBM Corporation
  @license: The BSD License
  '''
  def __init__(self, cb):
    try:
      try:
        self.inst = weakref.ref(cb.im_self)
      except TypeError:
        self.inst = None
      self.func = cb.im_func
      self.klass = cb.im_class
    except AttributeError:
      self.inst = None
      self.func = cb.im_func
      self.klass = None

  def __call__(self, *args, **kwargs):
    '''
    Proxy for a call to the weak referenced object. Take arbitrary params to
    pass to the callable.

    @raise ReferenceError: When the weak reference refers to a dead object
    '''
    if self.inst is not None and self.inst() is None:
      raise ReferenceError
    elif self.inst is not None:
      # build a new instance method with a strong reference to the instance
      mtd = new.instancemethod(self.func, self.inst(), self.klass)
    else:
      # not a bound method, just return the func
      mtd = self.func
    # invoke the callable and return the result
    return mtd(*args, **kwargs)

  def __eq__(self, other):
    '''
    Compare the held function and instance with that held by another proxy.

    @param other: Another proxy object
    @type other: L{Proxy}
    @return: Whether this func/inst pair is equal to the one in the other
    proxy object or not
    @rtype: boolean
    '''
    try:
      return self.func == other.func and self.inst() == other.inst()
    except Exception:
      return False

  def __ne__(self, other):
    '''
    Inverse of __eq__.
    '''
    return not self.__eq__(other)