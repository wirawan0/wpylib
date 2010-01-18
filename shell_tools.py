# $Id: shell_tools.py,v 1.2 2010-01-18 20:55:44 wirawan Exp $
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


def errchk(cmd, args, retcode):
  if retcode == 0: return

  print >>sys.stderr, "Error executing ", cmd, " ".join(args)
  if retcode < 0:
    err = "Command %s was terminated by signal %d" % (cmd, -retcode)
  else:
    err = "Command %s returned %d" % (cmd, retcode)
  raise RuntimeError, err

def run(prg, args):
  retcode = subprocess.call((prg,) + args)
  errchk(prg, args, retcode)
  return 0


# coreutils

def cp(*args):
  run('cp', args)

def mkdir(*args):
  run('mkdir', args)

def mv(*args):
  run('mv', args)

