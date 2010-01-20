# $Id: shell_tools.py,v 1.4 2010-01-20 21:27:41 wirawan Exp $
#
# wpylib.shell_tools
# Created: 20100106
# Wirawan Purwanto
#
# Simple and dirty tools like those I usually use in my shell
# scripts.
#

import os
import os.path
import sys

try:
  import subprocess
  has_subprocess = True
except:
  if "has_subprocess" not in globals():
    print >>sys.stderr, "Newer subprocess module does not exist, using older interfaces."
  has_subprocess = False

def mcd(subdir):
  # Assuming we have GNU coreutils' mkdir
  mkdir("-p", subdir)
  os.chdir(subdir)


def provide_file(dest, src):
  """Checks if file `dest' exists. If it does not, provide for it by means
  of a softlink from `src'."""
  if not os.path.exists(dest):
    # strip trailing /'s just in case it exists
    os.symlink(src, dest.rstrip("/"))


# Low-level utilities:

def errchk(cmd, args, retcode):
  """Checking for error after the invocation of an external command."""
  if retcode == 0: return

  print >>sys.stderr, "Error executing ", cmd, " ".join(args)
  if retcode < 0:
    err = "Command %s was terminated by signal %d" % (cmd, -retcode)
  else:
    err = "Command %s returned %d" % (cmd, retcode)
  raise RuntimeError, err


def quote_cmdline(seq):
  """Quotes the strings in seq for feeding to shell.
  This is a severe protection to prevent:
  - variable, command, or other substitutions
  - shell expansions (parameter, wildcard)
  - word splitting
  - invocation of shell builtin (!!!)
  """
  # Python 2.6's subprocess.py has list2cmdline, but I don't like it because
  # it still allows the shell to interpret wildcards. We have to quote wildcards
  # (*, [], {}, ?) and $ as well.
  rslt = []
  for i in seq:
    inew = '"' + i.replace("\\", "\\\\").replace('"', '\\"').replace('$', '\\$').replace('`', '\\`') + '"'
    rslt.append(inew)
  return " ".join(rslt)

if has_subprocess:

  def run(prg, args):
    retcode = subprocess.call((prg,) + tuple(args))
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

else:

  def run(prg, args=()):
    # Python < 2.4 does not have subprocess, so we use spawnvp
    retcode = os.spawnvp(os.P_WAIT, prg, (prg,) + tuple(args))
    errchk(prg, args, retcode)
    return 0

  def pipe_out(args, split=False, shell=False):
    """Executes a shell command, piping out the stdout to python for parsing.
    This is my customary shortcut for backtick operator.
    The result is either a single string (if split==False) or a list of strings
    with EOLs removed (if split==True)."""
    if shell or isinstance(args, str):
      # BEWARE: args should be a string in this case
      p = os.popen(args, "r")
    else:
      args = quote_cmdline(args)
      p = os.popen(args, "r")
    retval = p.read()
    status = p.close()
    if not split:
      return retval
    else:
      return retval.splitlines()


# coreutils
# and other common utilities

CMD = ['cat', 'cp', 'head', 'grep', 'less', 'ls', 'mkdir', 'mv', 'rm', 'tail']
CMD_NAME = {}
for n in CMD:
  CMD_NAME[n] = n
  s = """def %(cmd)s(*args): run(CMD_NAME['%(cmd)s'], args)"""
  exec(s % {'cmd': n })

def import_commands(namespace, cmds=None):
  if cmds == None: cmds = CMD
  thismod = globals()
  for n in cmds:
    n_act = thismod[n]
    namespace.setdefault(n, n_act)

"""
def cp(*args):
  run('cp', args)

def mkdir(*args):
  run('mkdir', args)

def mv(*args):
  run('mv', args)
"""

