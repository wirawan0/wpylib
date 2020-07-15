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
except ImportError:
  # This is really-really old. It should not matter anymore unless you
  # run on ultra-archaic systems that has Python < 2.4
  if "has_subprocess" not in globals():
    sys.stderr.write("subprocess module does not exist, using older interfaces.\n")
    sys.stderr.flush()
  has_subprocess = False


# To help with Python version incompatibilities
__py_ver_maj = sys.version_info.major
__py_ver = (sys.version_info.major, sys.version_info.minor)


# Files, directories, and filename utilities

def mcd(subdir):
  # Assuming we have GNU coreutils' mkdir
  mkdir("-p", subdir)
  os.chdir(subdir)

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
    raise KeyError(
      "Cannot find value among environment variables: %s" % (str(names))
    )

# Low-level utilities:

def errchk(cmd, args, retcode):
  """Checking for error after the invocation of an external command."""
  if retcode == 0: return

  sys.stderr.write("Error executing " + cmd + " " + join(args) + "\n")
  sys.stderr.flush()
  if retcode < 0:
    err = "Command %s was terminated by signal %d" % (cmd, -retcode)
  else:
    err = "Command %s returned %d" % (cmd, retcode)
  raise RuntimeError(err)


def quote_cmdline(seq):
  """Quotes the strings in seq for feeding to shell.
  This is a severe protection to prevent:
  - variable, command, or other substitutions
  - shell expansions (parameter, wildcard)
  - word splitting
  - invocation of shell builtin (!!!)
  """
  # Compared to other implementations:
  # - Python 2.6's subprocess.py has list2cmdline, but I don't like it because
  #   it still allows the shell to interpret wildcards. We have to quote wildcards
  #   (*, [], {}, ?) and $ as well.
  # - Python 3.3 has shlex.quote that performs similarly.
  # The reverse operation can be done via shlex standard module.
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

  def pipe_out(args, split=False, shell=False,
               text=True, encoding=None, errors=None,
               **popen_args):
    """Executes a shell command, piping out the stdout to python for parsing.
    This is my customary shortcut for backtick operator, and by default it is
    meant for text processing--therefore, the default `text=True`.
    The result is either a single string (if `split==False`) or a list of strings
    with EOLs removed (if `split==True`).

    The `text` argument is honored on Python 3.7+ only."""
    extra_args = dict(
      stdout=subprocess.PIPE,
      shell=shell
    )
    if __py_ver_maj >= 3:
      if __py_ver >= (3,7):
        extra_args["text"] = text
      else:
        extra_args["universal_newlines"] = text
      extra_args["encoding"] = encoding
      extra_args["errors"] = errors
    else:
      extra_args["universal_newlines"] = text
    extra_args.update(popen_args)

    retval = subprocess.Popen(args, **extra_args).communicate()[0]
    if not split:
      return retval
    else:
      return retval.splitlines()

  class pipe_in(object):
    """Executes a shell command, piping in the stdin from python for driving.
    This is the reverse of pipe_out.
    Input data are given through file-like write() or writelines() methods.
    The `text` argument is honored on Python 3+ only."""
    def __init__(self, args, shell=False, text=True):
      extra_args = dict(
        stdin=subprocess.PIPE,
        shell=shell
        )
      if sys.version_info.major >= 3:
        extra_args["text"] = text

      self.px = subprocess.Popen(args, **extra_args)
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

  # Python < 2.4 does not have subprocess, so we use spawnvp
  # (April 2020) BEWARE THAT THIS SECTION IS LARGELY UNSUPPORTED.
  # Many newer options are not implemented here.

  def run(prg, args=()):
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


class logged_runner(object):
  """Wrapper for wpylib.shell_tools.run() function.
  Includes a customizable logging of the external command invocation."""
  # Imported 20140802 from my check-git-vs-cvs.py tool. Original class name: Runner.
  log_prefix = "run: "
  def __init__(self, log=None):
    if log == None:
      from wpylib.iofmt.text_output import text_output
      log = text_output(sys.stdout)
    self.log = log
  def log_run(self, prg, args):
    """Logs the run command."""
    self.log("%s%s%s\n" % (self.log_prefix, prg, "".join([ " %s" % a for a in args ])))
  def __call__(self, prg, args):
    self.log_run(prg, args)
    return sh.run(prg, args)
  def nofail(self, prg, args):
    """Like wpylib.shell_tools.run(), but does not raise exception."""
    self.log_run(prg, args)
    retcode = subprocess.call((prg,) + tuple(args))
    if retcode != 0:
      self.log("%sretcode=%d\n" % (self.log_prefix, retcode))
    return retcode



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
  exec(s % {'cmd': n })

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

