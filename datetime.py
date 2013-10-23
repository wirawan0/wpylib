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

def utime_to_iso(t, local=True):
  """Converts UNIX time (seconds since Epoch) to ISO-formatted time string.

  In order to ease time computation/conversion,
  we will use numeric TZ shift (+/-HH:MM) instead of
  letter TZ code (EDT, EST, GMT, etc).
  """
  from time import localtime, gmtime, strftime, timezone
  if local:
    tt = localtime(t)
    dtz = -timezone + tt.tm_isdst * 3600
    # hopefully dtz is divisible by 60
    # It would be silly for a gov't to make its time
    # differ by seconds to GMT!
    dsec = abs(dtz) % 60
    dmin = abs(dtz // 60) % 60
    dhr = dtz // 3600
    if dsec == 00:
      sdtz = " %+03d:%02d" % (dhr, dmin)
    else:
      sdtz = " %+03d:%02d:%02d" % (dhr, dmin, dsec)
  else:
    tt = gmtime(t)
    sdtz = " +00:00"
  # Numeric timezone offset is created by hand
  # because I don't want to use %Z, nor do I want to use
  # "%z" (which did not work in python)
  return strftime("%Y-%m-%d %H:%M:%S", tt) + sdtz
