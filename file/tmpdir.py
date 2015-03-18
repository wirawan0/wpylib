#
# wpylib.file.tmpdir module
# Utility for creating a script-wide temporary directory.
#
# Wirawan Purwanto
# Created: 20140802
#
"""
wpylib.file.tmpdir
Utility for creating a script-wide temporary directory.

This module is part of wpylib project.

The temporary directory (tempdir) is created only once when
the main function, tmpdir(), is called.
This tempdir is supposed to be used as the root directory
for all other temporary files throughout the lifetime of the script.
When this script exists, the tempdir will be deleted with all
the files/subdirs therein with a forced `rm -rf' invocation.

The tmpdir routine has a fairly standard set of sequence of root dir
candidates.
User-defined roots can also be added (taking precedence over standard set)
via TMPDIR_ROOTS list.
But this must be added before the first tmpdir() function call.


"""

import os
import os.path
import sys
import tempfile

from warnings import warn
from wpylib import shell_tools as sh

_g = globals()
_g.setdefault("TMPDIR", None)
_g.setdefault("TMPDIR_CLEANUP", True)
_g.setdefault("TMPDIR_ROOTS", [])
del _g


def tmpdir():
  """Main function to create a temporary directory (when first called)
  and return the created temporary directory name.
  For subsequent calls, the same temporary directory name is given again.
  """
  from wpylib.file.file_utils import is_writable
  import atexit
  global TMPDIR, TMPDIR_ROOTS
  if TMPDIR != None: return TMPDIR
  tmproot = None
  # FIXME: site-specific hooks probably need to be set somewhere
  for d in list(TMPDIR_ROOTS) + [ os.getenv("TMP"), os.getenv("TMPDIR"), "/tmp", "/var/tmp" ]:
    if d != None and os.path.isdir(d) and is_writable(d):
      tmproot = d
      break
  if not tmproot:
    warn("Cannot find suitable temporary directory root, using current directory.",
         RuntimeWarning)
    tmproot = os.getcwd()
  TMPDIR = tempfile.mkdtemp(prefix=("%s/pytmp-%d" % (tmproot, os.getpid())))

  def tmpdir_exitfunc():
    global TMPDIR
    global TMPDIR_CLEANUP
    #print "TMPDIR_CLEANUP = ", TMPDIR_CLEANUP
    if TMPDIR != None and os.path.isdir(TMPDIR):
      if TMPDIR_CLEANUP:
        try:
          sh.rm("-rf", TMPDIR)
        except:
          try:
            sh.ls("-al", TMPDIR)
          except:
            pass
          warn("Failed to remove temporary directory %s" % TMPDIR)
      else:
        pass
        sys.stderr.write("wpylib.file.tmpdir: temp dir not cleaned up: %s\n" % TMPDIR)
  atexit.register(tmpdir_exitfunc)

  return TMPDIR
