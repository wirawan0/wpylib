# $Id: shell_tools.py,v 1.1 2010-01-08 18:43:06 wirawan Exp $
#
# wpylib.shell_tools
# Created: 20100106
# Wirawan Purwanto
#
# Simple and dirty tools like those I usually use in my shell
# scripts.
#

import os
import subprocess
import sys

def mcd(subdir):
  # Assuming we have GNU coreutils' mkdir
  cmd = ["mkdir", "-p", subdir]
  try:
    retcode = subprocess.call(cmd, shell=False)
    if retcode == 0:
      os.chdir(subdir)
      return

    print >>sys.stderr, "mcd " + subdir + ": ",
    if retcode < 0:
      print >>sys.stderr, "mkdir was terminated by signal", -retcode
    else:
      print >>sys.stderr, "mkdir returned", retcode
    raise RuntimeError, "Directory creation failure"
  except OSError, e:
    print >>sys.stderr, "mcd failed:", e
    raise


