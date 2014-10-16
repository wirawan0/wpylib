#
# wpylib.datetime0_idt
# Created: 20141015
# Wirawan Purwanto
#
# Simple date/time stamp using 64-bit integer.
# This module is an internal module; the exported name will
# be put in wpylib.datetime module.
#

"""
wplib.datetime0_idt module

Simple date/time stamp using 64-bit integer.
The primary motivation of creating this class is to store date/time
information in the most compact way, while keeping the ease of
human readability.

The internal format is very simple:

YYYYMMDDhhmmssfff

where:
 - YYYY = year (0 < YYYY <= 9999)
 - MM   = month (1 <= MM <= 12)
 - DD   = day
 - hh   = hour (0 <= hh < 24)
 - mm   = minutes
 - ss   = seconds
 - fff  = milliseconds

The time is always expressed in terms of UTC to eliminate ambiguity of
time zone, daylight savings time, etc.
CAVEAT: The resolution of the time is only on the order of millisecond.

This is a 17-decimal-digit integer, which fits in a 64-bit range (9.22e+18).

"""

from wpylib.params import struct


class idatetime(object):
  """Simple 8-byte integer representation of a date/time stamp.
  """
  def __init__(self, idt=None):
    if idt != None:
      self.idt = idt

  def validate(self):
    raise NotImplementedError

  def split_values(self):
    """Splits the compact datetime into components.
    Warning: the values are NOT validated.
    """
    idt = self.idt
    s = str(idt)
    R = struct()
    #R.YYYY, R.MM, R.DD, R.hh, R.mm, R.ss, R.fff # names are too cryptic
    # Use same member names as in datetime (in sofar it is possible):
    R.year, R.month, R.day, R.hour, R.minute, R.second, R.millisecond = map(int, [
      s[:-13],    # year
      s[-13:-11], # month
      s[-11:-9],  # day
      s[-9:-7],   # hour
      s[-7:-5],   # min
      s[-5:-3],   # sec
      s[-3:]      # millisec
    ])
    R.microsecond = R.millisecond * 1000
    return R

  def to_datetime(self):
    """Converts the object value to standard python datetime object.
    """
    from datetime import datetime
    R = self.split_values()
    dt = datetime(R.year, R.month, R.day, R.hour, R.minute, R.second, R.microsecond)
    '''
    idt = self.idt
    s = str(idt)
    YYYY, MM, DD, hh, mm, ss, ms = map(int, [
      s[:-13],    # year
      s[-13:-11], # month
      s[-11:-9],  # day
      s[-9:-7],   # hour
      s[-7:-5],   # min
      s[-5:-3],   # sec
      s[-3:]      # millisec
    ])
    dt = datetime(YYYY, MM, DD, hh, mm, ss, fff*1000)
    '''
    return dt

  def str_iso8601(self):
    """Outputs the object according to ISO-8601 combined date/time format.
    No time zone is shown."""
    R = self.split_values()
    fmt = "%(year)04d-%(month)02d-%(day)02dT%(hour)02d:%(minute)02d:%(second)02d.%(millisecond)03d"
    return fmt % R


