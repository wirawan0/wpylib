#
# wpylib.file.tee module
# File-manipulation utilities: tee output splitter
#
# Wirawan Purwanto
# Created: 20120514
#
# Routines put here are commonly used in my own scripts.
# They are not necessarily suitable for general-purpose uses; evaluate
# your needs and see if they can them as well.
#
#
"""
wpylib.file.tee module
File-manipulation utilities: tee output splitter

This module is part of wpylib project.
"""

class tee_output(object):
  """
  Tee class for output file streams.
  Supports file-like objects and auto-opened files (if the argument
  is a string).

  See also: http://shallowsky.com/blog/programming/python-tee.html
  """
  def __init__(self, *files, **opts):
    fd = []
    auto_close = []
    mode = opts.get("mode", "w")
    for f in files:
      if isinstance(f, basestring):
        F = open(f, mode=mode)
        fd.append(F)
        auto_close.append(True)
      else:
        fd.append(f)
        auto_close.append(False)
    self.fd = fd
    self.auto_close = auto_close

  def __del__(self):
    self.close()

  def close(self):
    for (auto,f) in zip(self.auto_close,self.fd):
      if auto:
        f.close()
      else:
        f.flush()
    self.fd = []
    self.auto_close = []

  def write(self, s):
    for f in self.fd:
      f.write(s)

  def flush(self):
    for f in self.fd:
      f.flush()

