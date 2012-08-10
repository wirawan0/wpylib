# -*- python -*-
#
# wpylib.py.stdout_capture
# Created: 20110809
# Wirawan Purwanto
#
# Hack tools for capturing sys.stdout in a function call.
#
"""
wpylib.py.stdout_capture

Capture tool for sys.stdout output, for interactive uses (primarily,
so that the output from sys.stdout is recorded to an ipython log file).

Original-source: `ipython_common.py`.
"""

import sys

class StdoutCapture(object):
  """Capture tool for sys.stdout output, for interactive uses (primarily,
so that the output from sys.stdout is recorded to an ipython log file).

  """
  class outfile_proxy(object):
    """A thin proxy for output file.
    The actual object, self.obj, *MUST* be set below."""
    def __init__(self):
      pass
    def write(self, stuff):
      self.obj.write(stuff)
    def flush(self):
      self.obj.flush()
    def close(self):
      pass

  def __init__(self):
    pass

  @property
  def stdout(self):
    """A stdout proxy that works with StdoutCapture."""
    if not hasattr(self, "my_stdout_proxy"):
      self.my_stdout_proxy = self.outfile_proxy()
      self.my_stdout_proxy_created = 1
    return self.my_stdout_proxy

  def Capture(self, proc, *args, **argkw):
    '''Captures sys.stdout while running proc (and its child subroutines).
    Returns a `printstr` object which, if displayed "as is" on an
    interactive python shell, would be logged in the log file as well.
    '''
    from StringIO import StringIO
    from wpylib.interactive_tools import printstr

    needs_stdout_redir = not hasattr(StdoutCapture, "_StdoutCapture_save_stdout")
    my_stdout_proxy_created = getattr(self, "my_stdout_proxy_created", 0)

    if needs_stdout_redir:
      #print "stdout not redirected yet"
      sys.stdout.flush()
      temp_stdout = StringIO()
      StdoutCapture._StdoutCapture_save_stdout = sys.stdout
      sys.stdout = temp_stdout

      if my_stdout_proxy_created:
        # delete it so it won't be touched later
        delattr(self, "my_stdout_proxy_created")
      if hasattr(self, "my_stdout_proxy"):
        self.my_stdout_proxy.obj = temp_stdout

    rslt1 = None # print output
    rslt2 = None # function output
    try:
      #print >> sys.stderr, "calling proc"
      rslt2 = proc(*args, **argkw)
      #print >> sys.stderr, "end proc"
    finally:
      #print >> sys.stderr, "finally proc"
      if needs_stdout_redir:
        rslt1 = temp_stdout.getvalue()
        sys.stdout = StdoutCapture._StdoutCapture_save_stdout
        delattr(StdoutCapture, "_StdoutCapture_save_stdout")
        #print >> sys.stderr, "stdout redirected back"
        #sys.stdout.flush()
        temp_stdout.close()

        # clean up the stdout proxy:
        if my_stdout_proxy_created:
          # delete it so it won't be touched later
          delattr(self, "my_stdout_proxy")

        if rslt2 != None:
          rslt = printstr("".join([rslt1, "\n", repr(rslt2)]))
          rslt.rslt = rslt2  # for user to fetch later
        else:
          rslt = printstr(rslt1)
        return rslt
      else:
        return rslt2

  def __call__(self, proc, *args, **argkw):
    return self.Capture(proc, *args, **argkw)

  @staticmethod
  def test_Capture(arg):
    """Test routine for capture.
    Example usage:

    >>> cap = StdoutCapture()
    >>> cap.Capture(cap.test_Capture, 5)"""
    print "sys.stdout object is:", repr(sys.stdout)
    a = 0
    for i in range(arg):
      print "i = ", i, " I want ", ("a" * i)
      a+=i
    return a
