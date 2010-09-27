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

