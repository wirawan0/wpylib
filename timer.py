# $Id: timer.py,v 1.1 2010-09-27 19:41:15 wirawan Exp $
#
# timer.py
# Simple timer and possibly other timing-related routine
#
# Wirawan Purwanto
# Created: 20081022
#
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

