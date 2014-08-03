# $Id: text_output.py,v 1.3 2011-09-02 15:07:47 wirawan Exp $
#
# wpylib.iofmt.text_output module
# Quick-n-dirty text output utilities
#
# Wirawan Purwanto
# Created: 20110511
#
# Routines put here are commonly used in my own scripts.
# They are not necessarily suitable for general-purpose uses; evaluate
# your needs and see if they can them as well.
#
# 20110426: Created as Logger class in my check-git-vs-cvs.py tool.
# 20110511: Moved to wpylib.iofmt.text_output .
#
"""
Simple text-based output writer.
This is supposedly the converse of text_input, but with different
capabilities.

This module is part of wpylib project.
"""

import sys

class text_output(object):
  """A simple text output.
  For use as a convenience tool like this:

    def subroutine(..., out=sys.stdout):
      from pyqmc.iofmt.text_output import text_output
      o = text_output(out)
      o("Line1\n")
      o("Line2\n")
      o("part of Line3: ")
      for x in [2,3,4]:
        o(" this is subpart %s" % x)
      o("\n")

  The text_output object is file-like for write-only purposes,
  and can be wrapped by yet another text_output object.

  The object's `_output' attribute can be set to whatever action
  (object method) you like to use (e.g. via subclassing), or
  by defining a stand-alone function that accepts "self" as the
  first argument.
  The set_write_func() function *must* be called for this purpose.

  To mute the output completely, set the `out' argument to None when
  creating the object.

  Caveat:
  * If the file-like object is closed, then we will do nothing
    for the rest of the __call__ invocation.
  """

  """---------------------------------------------------------------------
  Private members:
  * _autoopen -- boolean to indicate privately owned file object
  * _output -- method to output the stuff
  * out -- the output

  Internal notes:
  * A carefully thought hack is required to allow interchangeable
    "_output" method below.
    Here is my collected wisdom:
    - We can't define __call__ as a class attribute, like this:

          self.__call__ = self.write

      It won't work when the object is called: i.e. the following will cause
      an exception with "__call__" method not found:

          self("blah\n")

    - We shouldn't use the following either:

          self._output = self.write

      because the _output has an im_self member, which is a strong reference
      to self.
      This circular dependence causes the object (self) to never vanish when
      it is supposed to.

    - Some options are available out there to introduce a "weak" object
      method (e.g. WeakMethod, http://code.activestate.com/recipes/81253/)
      but it is too much for what we want to accomplish here.

    What I chose below is the *most* liberal choice which allow unbound
    function (with "self" as the first argument) to become the
    standard _output routine using slight .
    This is the best and most flexible, in my opinion, rather than imposing
    extra restrictions.
  ---------------------------------------------------------------------"""

  def __init__(self, out=sys.stdout, flush=False, mode="w"):
    """Initializes the text output.
    Options:
    - flush: if true, will flush every time the default action is invoked.
    """
    #print sys.getrefcount(self)
    self.out = None
    self.open(out, mode=mode)
    #print sys.getrefcount(self)
    if flush:
      self.set_write_func(self.write_flush)
    else:
      self.set_write_func(self.write)
    #print sys.getrefcount(self)
  def __del__(self):
    #print "Deleting object %s, file %s" % (self, self.out)
    self.close()
  def __enter__(self):
    return self
  def __exit__(self, type, value, traceback):
    self.close()
  def set_write_func(self, method):
    """Sets the default '_output' function to a python bound method.
    Always use this method, instead of setting self._output directly!

    NOTE:
    This is intentionally sloppy (no im_class or im_self checks),
    so that it can be used to perform DIRTY hack,such as allowing an
    arbitrary function (bound function from another unrelated class, or
    unbound function) to be attached as the output function."""
    if hasattr(method, "im_func"):
      self._output = method.im_func
    else:
      # assume that method is a stand-alone callable object
      # that can accept "self" as the first argument
      self._output = method
  def open(self, out=sys.stdout, mode="w"):
    self.close()
    self._autoopen = False
    if out == None:
      self.out = None
    elif self.is_file_like(out):
      self.out = out
    else: # assume a string (a filename)
      self.out = open(out, mode)
      self.outfilename = out
      self._autoopen = True
  def close(self):
    """Closes the text_output's output object.
    At least, flushes everything at the end of the output's association
    with this text_output object.
    """
    if self.out:
      if self._autoopen:
        #print "Closing file " + self.out.name
        self.out.close() # depends on existing close() method
      else:
        self.out.flush()
      self.out = None

  @staticmethod
  def is_file_like(obj):
    return isinstance(obj, file) \
      or (hasattr(obj, "write") and hasattr(obj, "flush"))

  def __call__(self, *_list, **_args):
    """Unfortunately __call__ cannot be a usual class attribute.
    So we have to use a thin dispatcher here."""
    self._output(self, *_list, **_args)

  # Original I/O routine is preserved by _* method name
  # FIXME: A better optimization can be introduced needed if
  # self.out is yet another text_output instance.
  # But beware of possible method polymorphism if you do this. (!!!)
  def _write(self, s):
    if self.out != None: self.out.write(s)
  def _flush(self):
    if self.out != None: self.out.flush()
  def _write_flush(self, s):
    if self.out != None:
      self.out.write(s)
      self.out.flush()
  # The logger itself is a file-like object, too:
  write = _write
  flush = _flush
  write_flush = _write_flush


def test1():
  O = text_output("/tmp/test1abc.txt", flush=1)
  O("this is a test\n")
  O("--------------\n")
