# $Id: datetime.py,v 1.1 2011-09-01 15:34:03 wirawan Exp $
#
# wpylib.datetime
# Created: 20110901
# Wirawan Purwanto
#

"""
wpylib.datetime

Frequently used date/time related tools.
Do not confuse this with python's core datetime module, which
is not being replaced by this module!
"""

import sys
import time


def date8():
  return time.strftime("%Y%m%d")

