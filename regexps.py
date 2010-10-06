# -*- python -*-
#
# $Id: regexps.py,v 1.1 2010-10-06 16:37:42 wirawan Exp $
#
# Created: 20101006
# Wirawan Purwanto
#
"""

Various convenience regular expression tools.

"""

import re


class regex(object):
  """Single-state regex matcher.
  For quick and dirty matching (single-use, disposable).
  This is intended to make python scripts a bit more convenient to
  use for regexp-intensive matches, just like perl.

  Examples:

      rx = regex(r'deltau = ([0-9.]+)')
      rx2 = regex(r'deltau2 = ([0-9.]+)')
      ...
      for text in f:
        if rx % text:  # equal to rx.search(text)
          deltau = float(rx[1])
        if rx2 ^ text: # equal to rx.match(text)
          deltau2 = float(rx2[1])

  Note that the regex object must appear as the *LEFT* operand of the
  string being scanned.

  """
  def __init__(self, pat, flags=0):
    self.rx = re.compile(pat, flags)

  # The following names are the same as standard python re compiled object:
  def match(self, s, flags=0):
    self.m = self.rx.match(s, flags)
    return self.m
  def search(self, s, flags=0):
    self.m = self.rx.search(s, flags)
    return self.m

  # Experimental: using operators instead of names
  # No user-defined flags are possible in this case.
  def __xor__(self, s):
    """Match the string to the regex at the beginning."""
    self.m = self.rx.match(s)
    return self.m
  def __mod__(self, s):
    """Match the string to the regex at the any position.
    Too bad python does not have ~= like perl, so we use the
    quirky % or == here."""
    self.m = self.rx.search(s)
    return self.m
  __eq__ = __mod__

  def __getitem__(self, i):
    """Returns the i-th group from the last match operation."""
    return self.m.group(i)
