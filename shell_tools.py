# $Id: shell_tools.py,v 1.3 2010-01-20 17:25:54 wirawan Exp $
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


def pipe_out(args, split=False, shell=False):
  """Executes a shell command, piping out the stdout to python for parsing.
  This is my customary shortcut for backtick operator.
  The result is either a single string (if split==False) or a list of strings
  with EOLs removed (if split==True)."""
  retval = subprocess.Popen(args, stdout=subprocess.PIPE, shell=shell).communicate()[0]
  if not split:
    return retval
  else:
    return retval.splitlines()


# coreutils

def cp(*args):
  run('cp', args)

def mkdir(*args):
  run('mkdir', args)

def mv(*args):
  run('mv', args)

