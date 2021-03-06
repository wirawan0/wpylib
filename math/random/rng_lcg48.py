#
# wpylib.math.random.rng_lcg48 module
# Created: 20130814
# Wirawan Purwanto
#

"""
wpylib.math.random.rng_lcg48 module
Implementation of 48-bit Linear Congruential pseudorandom number generator

This RNG is used only for testing and regression purposes.

This module contains a python implementation of the Fortran 'rannyu' function
(including the hardcoded seed library).
"""

from wpylib.math.random import rng_base

class lcg48(rng_base):
  """Linear congruential pseudorandom number generator.
  By default this implements the `rannyu' routine."""
  m = 34522712143931  # 11**13
  # This is "seed 1" in the legacy rannyu seed library.
  L = 127
  n = 11863279
  seed_index = 1
  div_two_48 = 2.0**(-48)
  def __call__(self):
    L_new = (self.m * self.L + self.n) & 0xFFFFFFFFFFFF
    self.L = L_new
    if L_new == 0:
      return self.div_two_48
    else:
      return L_new * self.div_two_48
  def update_seed(self, Ln):
    if len(Ln) == 2:
      (self.L, self.n) = (Ln[0], Ln[1])
      self.seed_index = None
    elif len(Ln) == 3:
      (self.seed_index, self.L, self.n) = (Ln[0], Ln[1], Ln[2])
    else:
      raise TypeError, "Unsupported seed type."
  def use_seed_lib(self, index):
    self.m = 34522712143931  # 11**13
    self.update_seed(rannyu_seed_lib[index])


class rannyu(lcg48):
  """Simulation of Fortran rannyu method with support for normal
  (Gaussian) PDF."""
  def __init__(self, seed=None):
    if seed==None:
      seed = numpy.random.randint(102)+1
    self.use_seed_lib(seed)
  def normal(self, size):
    rslt = numpy.empty(size)
    size = numpy.product(rslt.shape)
    for i in xrange(size):
      rslt.flat[i] = GaussianRandom(self)
    return rslt


def GaussianRandom(rnd):
  """Same implementation as in my perl or Fortran code.
  rnd is a random number generator object (i.e. the rannyu object)."""
  from numpy import sqrt, log
  if not hasattr(rnd, "_gr_next_rnd"):
    while True:
      x = 2.0 * rnd() - 1.0
      y = 2.0 * rnd() - 1.0
      r2 = x*x + y*y
      if 0.0 < r2 < 1.0: break

    z = sqrt(-2.0 * log(r2) / r2)
    rnd._gr_next_rnd = z * x  # v
    return z * y   # u
  else:
    v = rnd._gr_next_rnd
    del rnd._gr_next_rnd
    return v


def mkint48(N):
  """Generates a 48-bit number from four integers.
  Used for encoding conversion for legacy rannyu library."""
  return N[3] + (N[2] << 12) + (N[1] << 24) + (N[0] << 36)


def split48(value):
  """Splits a 48-bit integer into a 4-tuple of 12-bit integers.
  """
  i4 = value & 0xFFF
  value >>= 12
  i3 = value & 0xFFF
  value >>= 12
  i2 = value & 0xFFF
  value >>= 12
  i1 = value & 0xFFF
  return (i1,i2,i3,i4)


rannyu_seed_lib = [
  (), # 0 is not used
  (1, 127, 11863279),
  (2, 127, 11863259),
  (3, 127, 11863253),
  (4, 127, 11863249),
  (5, 127, 11863237),
  (6, 127, 11863213),
  (7, 152656382984915, 11863279),
  (8, 152656382984915, 11863259),
  (9, 152656382984915, 11863253),
  (10, 152656382984915, 11863249),
  (11, 152656382984915, 11863237),
  (12, 152656382984915, 11863213),
  (13, 127, 11863207),
  (14, 127, 11863183),
  (15, 152656382984915, 11863207),
  (16, 152656382984915, 11863183),
  (17, 152656382984915, 11863171),
  (18, 152656382984915, 11863153),
  (19, 152656382984915, 11863151),
  (20, 152656382984915, 11863133),
  (21, 152656382984915, 11863123),
  (22, 152656382984915, 11863121),
  (23, 152656382984915, 11863109),
  (24, 152656382984915, 11863099),
  (25, 127, 11863171),
  (26, 127, 11863153),
  (27, 127, 11863151),
  (28, 127, 11863133),
  (29, 127, 11863123),
  (30, 127, 11863121),
  (31, 127, 11863109),
  (32, 127, 11863099),
  (33, 152656382984915, 11863073),
  (34, 127, 11863073),
  (35, 152656382984915, 11863067),
  (36, 127, 11863067),
  (37, 152656382984915, 11863057),
  (38, 127, 11863057),
  (39, 152656382984915, 11863039),
  (40, 127, 11863039),
  (41, 152656382984915, 11863037),
  (42, 127, 11863037),
  (43, 127, 11863031),
  (44, 127, 11863021),
  (45, 127, 11862997),
  (46, 127, 11862989),
  (47, 127, 11862979),
  (48, 127, 11862959),
  (49, 127, 11862919),
  (50, 127, 11862911),
  (51, 127, 11862881),
  (52, 127, 11862869),
  (53, 127, 11862857),
  (54, 127, 11862841),
  (55, 127, 11862839),
  (56, 127, 11862803),
  (57, 127, 11862791),
  (58, 127, 11862761),
  (59, 127, 11862713),
  (60, 127, 11862013),
  (61, 127, 11862007),
  (62, 127, 11861987),
  (63, 127, 11861959),
  (64, 127, 11861953),
  (65, 127, 11861923),
  (66, 127, 11861819),
  (67, 127, 11861803),
  (68, 127, 11861791),
  (69, 127, 11861749),
  (70, 127, 11861713),
  (71, 127, 11861711),
  (72, 127, 11861701),
  (73, 152656382984915, 11863031),
  (74, 152656382984915, 11863021),
  (75, 152656382984915, 11862997),
  (76, 152656382984915, 11862989),
  (77, 152656382984915, 11862979),
  (78, 152656382984915, 11862959),
  (79, 152656382984915, 11862919),
  (80, 152656382984915, 11862911),
  (81, 152656382984915, 11862881),
  (82, 152656382984915, 11862869),
  (83, 152656382984915, 11862857),
  (84, 152656382984915, 11862841),
  (85, 152656382984915, 11862839),
  (86, 152656382984915, 11862803),
  (87, 152656382984915, 11862791),
  (88, 152656382984915, 11862761),
  (89, 152656382984915, 11862713),
  (90, 152656382984915, 11862013),
  (91, 152656382984915, 11862007),
  (92, 152656382984915, 11861987),
  (93, 152656382984915, 11861959),
  (94, 152656382984915, 11861953),
  (95, 152656382984915, 11861923),
  (96, 152656382984915, 11861819),
  (97, 152656382984915, 11861803),
  (98, 152656382984915, 11861791),
  (99, 152656382984915, 11861749),
  (100, 152656382984915, 11861713),
  (101, 152656382984915, 11861711),
  (102, 152656382984915, 11861701),
]

