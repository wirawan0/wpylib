#
# wpylib.math.random module
# Created: 20130814
# Wirawan Purwanto
#

import numpy

class rng_base(object):
  """Base class for random number generator."""

# Standard classes
from wpylib.math.random.rng_lcg48 import lcg48
