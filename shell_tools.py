# $Id: shell_tools.py,v 1.8 2010-10-25 14:41:39 wirawan Exp $
#
# wpylib.shell_tools
# Created: 20100106
# Wirawan Purwanto
#
# Simple and dirty tools like those I usually use in my shell
# scripts.
#

import glob
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

def dirname2(path):
  """Returns the directory part of a path.
  The difference from os.path.dirname is that if the directory
  part is empty, it is converted to '.' (the current directory)."""
  d = os.path.dirname(path)
  if d == '': d = '.'
  return d

def file_exists_nonempty(path):
  """Determines whether a given path is a regular file of
  nonzero size."""
  return os.path.isfile(path) and os.stat(path).st_size > 0

def provide_link(dest, src):
  """Checks if file `dest' exists. If it does not, provide for it by means
  of a softlink from `src'."""
  if not os.path.exists(dest):
    # strip trailing /'s just in case it exists
    os.symlink(src, dest.rstrip("/"))


# Globbing utilities:

def sorted_glob(pathname):#, cmp=None, key=None, reverse=None):
  """Returns a sorted list of file names matching glob pattern `pathname'.
  Added here to accomodate older python that do not have sorted() function."""
  rslt = glob.glob(pathname)
  rslt.sort() #cmp=cmp, key=key, reverse=reverse)
  return rslt

# Environment variable utilities:

def env_push(name, new_value):
  """Temporarily modifies the value of an environment variable; saving the
  original one in the function return value.
  The original value can be restored to the environment variable by calling
  env_pop.

  Example:

      oldpath = push_env('TOOL_HELPER', '/usr/bin/less')
      execvp(os.P_WAIT, 'some_tool', ('some_tool', 'some_arg'))
      pop_env('TOOL_HELPER', oldpath)
  """
  old_value = os.environ.get(name, None)
  os.environ[name] = new_value
  return old_value

def env_pop(name, old_value):
  """Restores the original value of an environment variable that was modified
  temporarily by env_push."""
  if old_value == None:
    del os.environ[name]
  else:
    os.environ[name] = old_value

def getenv(*names, **opts):
  """Tries to get a value from a list of environment variables.
  The first found one will be used; if none is found, then a default will
  be tried (use `default' parameter to specify this).
  If no default is found, then a KeyError exception will be raised.
  """
  for n in names:
    if n in os.environ:
      return os.environ[n]
  if "default" in opts:
    return opts["default"]
  else:
    raise KeyError, \
      "Cannot find value among environment variables: %s" % (str(names))

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


"""
pipe_out and pipe_in defines unidirectional pipes for external programs.
Note the unconventional meaning: `pipe_in' means we drive the program with
python input as the stdin, `pipe_out' means we run the program and read in
the output into python.
"""


if has_subprocess:

  def run(prg, args):
    retcode = subprocess.call((prg,) + tuple(args))
    errchk(prg, args, retcode)
    return 0

  def system(cmdline):
    """Similar to os.system(), except that errors are caught.
    cmdline *must* be a string."""
    retcode = subprocess.call(cmdline, shell=True)
    errchk(cmdline, (), retcode)
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

  class pipe_in:
    """Executes a shell command, piping in the stdin from python for driving.
    This is the reverse of pipe_out.
    Commands are given through file-like write() or writelines() methods."""
    def __init__(self, args, shell=False):
      self.px = subprocess.Popen(args, stdin=subprocess.PIPE, shell=shell)
      self.args = args
    def write(self, line):
      self.px.stdin.write(line)
    def writelines(self, lines):
      for line in lines:
        self.write(line)
    def flush(self):
      self.px.stdin.flush()
    def close(self):
      self.px.stdin.close()

else:

  def run(prg, args=()):
    # Python < 2.4 does not have subprocess, so we use spawnvp
    retcode = os.spawnvp(os.P_WAIT, prg, (prg,) + tuple(args))
    errchk(prg, args, retcode)
    return 0

  def system(cmdline):
    """Similar to os.system(), except that errors are caught."""
    retcode = os.system(cmdline)
    errchk(cmdline, (), retcode)
    return 0

  def pipe_out(args, split=False, shell=False):
    """Executes a shell command, piping out the stdout to python for parsing.
    This is my customary shortcut for backtick operator.
    The result is either a single string (if split==False) or a list of strings
    with EOLs removed (if split==True)."""
    if shell or isinstance(args, basestring):
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

  def pipe_in(args, shell=False):
    """Executes a shell command, piping in the stdin from python for driving.
    This is the reverse of pipe_out.
    Commands are given through file-like write() or writelines() methods."""
    if shell or isinstance(args, basestring):
      # BEWARE: args should be a string in this case
      p = os.popen(args, "w")
    else:
      args = quote_cmdline(args)
      p = os.popen(args, "w")
      return p


# coreutils

coreutils = """
base64 basename
cat chcon chgrp chmod chown cksum comm cp csplit cut
date dd df dir dircolors dirname du
echo env expand expr
factor false fmt fold
groups
head hostid
id install
join
link
ln logname ls
md5sum mkdir mkfifo mknod mv
nice nl nohup
od
paste pathchk pinky pr printenv printf ptx pwd
readlink rm rmdir runcon
seq sha1sum sha224sum sha256sum sha384sum sha512sum shred shuf sleep sort split stat stty sum sync
tac tail tee test touch touch tr true tsort tty
uname unexpand uniq unlink users
vdir
wc who whoami
yes
""".split()

# and other common utilities

CMD = coreutils
CMD += [ 'grep', 'less' ]
CMD += [ 'sh', 'bash' ]
CMD += [ 'gawk', 'sed', ]
CMD_NAME = {}
for n in CMD:
  CMD_NAME[n] = n
  s = """def %(cmd)s(*args): run(CMD_NAME['%(cmd)s'], args)"""
  exec s % {'cmd': n }

def import_commands(namespace, cmds=None):
  """Safely import shell commands to a given namespace.
  We should avoid importing names that belong to built-in functions,
  therefore we added that check below."""
  if cmds == None: cmds = CMD
  #print namespace.keys()
  #print namespace["__builtins__"]
  my_namespace = globals()
  dir = my_namespace['__builtins__']['dir']
  #print dir(namespace["__builtins__"])
  # Never clobber the built-in names:
  try:
    exclusions = dir(namespace["__builtins__"])
  except:
    exclusions = []

  for n in cmds:
    if n not in exclusions:
      n_act = my_namespace[n]
      namespace.setdefault(n, n_act)

"""
def cp(*args):
  run('cp', args)

def mkdir(*args):
  run('mkdir', args)

def mv(*args):
  run('mv', args)
"""

