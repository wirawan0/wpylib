# $Id: timer.py,v 1.2 2010-09-27 19:54:26 wirawan Exp $
#
# timer.py
# Simple timer and possibly other timing-related routine
#
# Wirawan Purwanto
# Created: 20081022
#
# 20081022: Created as pyqmc.utils.timer .
# 20100927: Moved to wpylib.timer .
#

"""
Simple timer utility.

This module is part of wpylib project.
"""

import sys
import time

class timer:
  '''A small timer class.'''
  def start(self):
    self.tm1 = time.clock()
  def stop(self):
    self.tm2 = time.clock()
    return (self.tm2 - self.tm1)
  def length(self):
    return self.tm2 - self.tm1


class block_timer(object):
  """Timer for a code block in python.
  For use with python 2.5+ 'with' statement.
  See: http://preshing.com/20110924/timing-your-code-using-pythons-with-statement

  To use this:

      with block_timer() as t:
        <code>

  Fancy options are available to record the timing result, specified when
  initializing the new object:

  * report=block_timer.writeout_file :: writes out the timing result to a file
  * report=block_timer.writeout_dict :: saves the timing result to a dict-like element
  """
  @staticmethod
  def writeout_file(out):
    return lambda tm: out.write("Total execution time = %s secs\n" % (tm,))
  @staticmethod
  def writeout_dict(rec, key):
    def wrt_dict(tm):
      rec[key] = tm
    return wrt_dict
    #return lambda tm: rec.__setitem__(key, tm)

  @classmethod
  def bt_file(cls, fobj):
    """An object factory to report the timing to a text file.
    """
    if isinstance(fobj, basestring):
      from wpylib.iofmt.text_output import text_output
      out = text_output(fobj)
    else:
      out = fobj
    return cls(report=block_timer.writeout_file(out))

  @classmethod
  def bt_dict(cls, rec, key):
    return cls(report=block_timer.writeout_dict(rec, key))

  def __init__(self, report=None):
    if report is None: report = block_timer.writeout_file(sys.stdout)
    self.report = report

  def __enter__(self):
    self.start = time.clock()
    return self

  def __exit__(self, *args):
    self.end = time.clock()
    self.interval = self.end - self.start
    self.report(self.interval)
