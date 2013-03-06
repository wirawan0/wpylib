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
  """Returns a standard 8-digit representation of the current date."""
  return time.strftime("%Y%m%d")

def time_diff(time1, time2):
  """Returns the time difference (time1 - time2) in seconds."""
  from time import mktime
  return mktime(time1) - mktime(time2)

def shift_time(t, dt, localtime=True):
  """Shifts a time data by an amount in dt (specified in seconds)."""
  if isinstance(t, time.struct_time):
    t1 = time.mktime(t) + dt
  else:
    t1 = t + dt
  if localtime:
    return time.localtime(t1)
  else:
    return time.gmtime(t1)

