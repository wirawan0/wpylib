# -*- python -*-
#
# $Id: debugging.py,v 1.1 2011-08-31 18:25:07 wirawan Exp $
#
# Created: 20100909
# Wirawan Purwanto
#
# Debugging tools for python
#

import re

def fmtstr_find_missing_arguments(fmtstr, args):
  """Finds what named arguments are not supplied."""
  missing = {}
  for kw1 in re.findall("%\([^)]+\)", fmtstr):
    kw = kw1[2:-1]
    if kw not in args:
      missing[kw] = missing.get(kw,0) + 1
  missing2 = missing.keys()
  missing2.sort()
  return missing2
