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


class utime_to_iso_proc(object):
  """Converts UNIX time (seconds since Epoch) to ISO-formatted time string.

  In order to ease time computation/conversion,
  we will use numeric TZ shift (+/-HH:MM) instead of
  letter TZ code (EDT, EST, GMT, etc).

  The full ISO-8601 format is like this:

    YYYY-MM-DDThh:mm:ss.fffffffff+AA:BB

  where
  * YYYY-MM-DD = year, month, date
  * hh:mm:ss.fff = hour, minute, second, fraction of the second
  * AA:BB = time shift due to time zone

  But some variants are valid:
  * YYYY-MM-DD hh:mm    (GNU ls timestyle 'long-iso')
  * YYYY-MM-DD hh:mm.ss.fffffffff +AA:BB    (GNU ls timestyle 'full-iso')

  There are some built-in formats in this subroutine.
  They can be tweaked further (adding new formats is OK; but changing
  existing ones are not recommended).

  The format string will undergo two passes:
  * first pass, via strftime
  * second pass, if '%' still exists in the string, expansion using 'opts'
    computed variables.

  Identifiers for second pass must be named, and must use '%%(NAME)s' kind of
  format with double percent sign.

  References:
  * http://www.cl.cam.ac.uk/~mgk25/iso-time.html
  * http://en.wikipedia.org/wiki/ISO_8601
  * http://www.sqlite.org/lang_datefunc.html  (subheading "Time Strings")
  """
  map_fmt_iso = {
    0: "%Y-%m-%d %H:%M:%S %%(TZ)s",  # original default of this routine
    'default': "%Y-%m-%d %H:%M:%S %%(TZ)s",  # original default of this routine
    # Global formats
    'iso8601': "%Y-%m-%dT%H:%M:%S.%%(NANOSECS)s%%(ZTZ)s", # formal ISO-8601
    # GNU-specific formats
    'gnu long-iso': "%Y-%m-%d %H:%M",
    'gnu full-iso': "%Y-%m-%d %H:%M:%S.%%(NANOSECS)s %%(TZ)s",
    # My custom formats
    'idtstamp': "%Y-%m-%dT%H:%M:%S.%%(MILLISECS)s",
  }
  def __init__(self, fmt=0):
    from copy import copy
    # Make a copy so we don't clobber the original class:
    self.map_fmt_iso = copy(self.map_fmt_iso)
    self.fmt = fmt

  def __call__(self, t=None, local=True, fmt=None):
    from time import time, localtime, gmtime, strftime, timezone
    if fmt == None: fmt = self.fmt
    if t == None:
      t = time()
    # The time, the nanosecond part:
    t_ns = int((t - int(t)) * 1e+9)
    opts = {
      'NANOSECS': ("%09.0f" % t_ns),
      'MICROSECS':  ("%06.0f" % (t_ns // 1000)),
      'MILLISECS':  ("%03.0f" % (t_ns // 1000000)),
    }
    if local:
      tt = localtime(t)
      # dtz = Delta time due to Time Zone
      dtz = -timezone + tt.tm_isdst * 3600
      # hopefully dtz is divisible by 60
      # It would be silly for a gov't to make its time
      # differ by seconds to GMT!
      dsec = abs(dtz) % 60
      dmin = abs(dtz // 60) % 60
      dhr = dtz // 3600
      if dsec == 00:
        opts['TZ'] = "%+03d:%02d" % (dhr, dmin)
      else:
        optz['TZ'] = "%+03d:%02d:%02d" % (dhr, dmin, dsec)
      opts['ZTZ'] = opts['TZ']
    else:
      tt = gmtime(t)
      opts['TZ'] = "+00:00"
      opts['ZTZ'] = "Z"
    # Numeric timezone offset is created by hand
    # because I don't want to use %Z, nor do I want to use
    # "%z" (which did not work in python)
    fmt = self.map_fmt_iso.get(fmt, fmt)
    rslt1 = strftime(fmt, tt)
    if "%" in rslt1:
      rslt2 = rslt1 % opts
      return rslt2
    else:
      return rslt1

utime_to_iso = utime_to_iso_proc()
