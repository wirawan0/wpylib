# $Id: interactive_tools.py,v 1.2 2011-07-18 15:48:52 wirawan Exp $
#
# wpylib.interactive_tools
# Created: 20091204
# Wirawan Purwanto
#
# Simple and dirty tools for interactive python mode
#

import atexit
import inspect
import os
import sys

MSGLOG = sys.stderr


def get_global_namespace_(global_ns):
  """Internal routine to get global namespace from another function
  in this module.
  BEWARE the limitation! This function is rather fragile and must be
  called such that the stack order is like this (in descending
  order):

     * global module statement ...
     * a function from this module
     * this function
  """
  import pprint
  if global_ns == None:
    # Use introspection to fetch the global namespace of the calling
    # function:
    from inspect import stack
    caller_info = stack()[2]  # by default, _two_ level up
    caller_frame = caller_info[0]  # get the frame record
    g = caller_frame.f_globals
  else:
    g = global_ns

  try:
    builtin_ns = g['__builtins__']
  except:
    builtin_ns = None  # this should not ever happen!

  if False: # for debugging only
    pprint.pprint(stack())
    print "caller_info = ",
    pprint.pprint(caller_info)
    pprint (sorted(g.keys()))
    pprint (g['__builtins__'])
  return (g, builtin_ns)

def detect_interactive(global_ns=None):
  """Detects if we are in an interactive python session.
  """

  """The detection scheme is rather complex one because each mode has its
  own way of flagging that it is ``interactive''.

  See some discussions in:
    http://stackoverflow.com/questions/1212779/detecting-when-a-python-script-is-being-run-interactively

  These are some known cases:
  * For ipython, see if "__IPYTHON__" is defined in the user's global
    namespace.
  * For "python -i" invocation, sys.flags.interactive will be set to True.
  * For vanilla "python" invocation with no argument, then sys.ps1
    variable exists.
  """
  (g, b) = get_global_namespace_(global_ns)
  if "__IPYTHON__" in g or hasattr(b, "__IPYTHON__"):
    return {
      'session': 'ipython',
    }
  elif sys.flags.interactive:
    return {
      'session': 'python -i',
    }
  elif hasattr(sys, 'ps1'):
    return {
      'session': 'python',
    }
  else:
    return False


def init_interactive(use_readline=True, global_ns=None):
  """Perform standard initialization for my scripts.
  Some options can be given to tweak the environment.

  Under ipython
  """
  # ERROR: this still does not work. we need to execute the statements
  # in the global (base) namespace, not in this function's namespace.

  (g, b) = get_global_namespace_(global_ns)
  int_info = detect_interactive(g)

  if use_readline:
    # Assume interactive python, create a completer if it hasn't been
    # loaded. This is needed for e.g. sciclone, jaguar with no ipython
    # there.
    if 'rlcompleter' not in sys.modules \
        and 'IPython.ipy_completers' not in sys.modules:
      try:
        import readline
      except ImportError:
        print >>MSGLOG, "Module readline not available."
      else:
        print "Loading classic readline/rlcompleter."
        import rlcompleter
        readline.parse_and_bind("tab: complete")
 
        _histfile = os.path.join(os.environ["HOME"], ".pyhistory")
        # read history, if it exists
        if os.path.exists(_histfile):
          readline.read_history_file(_histfile)
        # register saving handler
        atexit.register(readline.write_history_file, _histfile)
        del _histfile


  # Interestingly, under ipython the sys.argv is only "correct" to extract
  # the program name at the first loading of the script.
  # So we must capture that:
  if int_info['session'] == 'ipython' and 'ARGV' not in g:
    g['ARGV'] = sys.argv
    try:
      g['MYSELF'] = os.path.abspath(sys.argv[0])
    except:
      pass
  elif int_info['session'] in ('python', 'python -i'):
    g.setdefault('MYSELF', sys.argv[0])
    g.setdefault('ARGV', sys.argv)

#print "_-helo"
