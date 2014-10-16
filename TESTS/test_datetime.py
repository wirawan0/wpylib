"""
Test routines for wpylib.datetime module (and related submodules).
"""

from time import localtime, gmtime, strftime

from wpylib.datetime0_idt import idatetime
from wpylib.datetime import utime_to_iso



def test_idt_01():
  """[20141016]
  Basic idatetime tests.
  """
  iidt = 20141201083724315
  idt = idatetime(iidt)
  print "integer value          = %+18d" % idt.idt
  print "iso8601 format         = %s" % idt.str_iso8601()


def test_u2i_01():
  """[20141016]
  Testing utime_to_iso subroutine.

  Output:

    unix time                           =  1413475094.058478
    time interpretation (local)         =  Thu Oct 16 11:58:14 EDT 2014
    utime_to_iso output (local)         =  2014-10-16 11:58:14 -04:00
    utime_to_iso output (local/iso8601) =  2014-10-16T11:58:14.058478116-04:00
    time interpretation (utc)           =  Thu Oct 16 15:58:14 EST 2014
    utime_to_iso output (utc)           =  2014-10-16 15:58:14 +00:00
    utime_to_iso output (utc/iso8601)   =  2014-10-16T15:58:14.058478116Z
    utime_to_iso output (utc/idtstamp)  =  2014-10-16T15:58:14.058

  """
  unix_time = 1413475094.058478
  str_time = utime_to_iso(unix_time, local=True)
  str_gmtime = utime_to_iso(unix_time, local=False)
  print "unix time                           = ", "%.16g" % unix_time

  print "time interpretation (local)         = ", strftime("%a %b %e %H:%M:%S %Z %Y", localtime(unix_time))
  print "utime_to_iso output (local)         = ", str_time
  print "utime_to_iso output (local/iso8601) = ", utime_to_iso(unix_time, local=True, fmt='iso8601')

  print "time interpretation (utc)           = ", strftime("%a %b %e %H:%M:%S %Z %Y", gmtime(unix_time))
  print "utime_to_iso output (utc)           = ", str_gmtime
  print "utime_to_iso output (utc/iso8601)   = ", utime_to_iso(unix_time, local=False, fmt='iso8601')
  print "utime_to_iso output (utc/idtstamp)  = ", utime_to_iso(unix_time, local=False, fmt='idtstamp')




