# $Id: interactive_tools.py,v 1.1 2010-01-22 18:46:27 wirawan Exp $
#
# wpylib.interactive_tools
# Created: 20091204
# Wirawan Purwanto
#
# Simple and dirty tools for interactive python mode
#

import sys

def init_interactive():
  # ERROR: this still does not work. we need to execute the statements
  # in the global (base) namespace, not in this function's namespace.

    # Assume interactive python, create a completer if it hasn't been
    # loaded. This is needed for e.g. sciclone, jaguar with no ipython
    # there.
    if 'rlcompleter' not in sys.modules \
       and 'IPython.ipy_completers' not in sys.modules:
      try:
        import readline
      except ImportError:
        print "Module readline not available."
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
