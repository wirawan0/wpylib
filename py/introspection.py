# -*- python -*-
#
# wpylib.py.introspection
# Created: 20150819
# Wirawan Purwanto
#
# Advanced introspection tools for python
#

def name_rlookup(val, namespace, prefix=None, rx_match=None, lookup="dict", comp="=="):
  """Reverse lookup of variable/object name.
  This function yields the list of object names in the namespace whose
  respective values are equal to `val`.

  This is useful for example to reverse-lookup an object's name, but only in
  restricted contexts (e.g. when the value to look for is unique).

  Input:

  * `val`:: Value to compare against (or to search the key/name for)

  * `namespace`:: The namespace object, which can be a dict-like object or an
    object whose attributes can be enumerated using dir() function.

  * `prefix` or `rx_match`:: Only one can be given to narrow the scope of the names
    to search from.
    The two cannot be given at once; `prefix` will take precedence in that case.

  *  `lookup`:: The namespace lookup method can be 'dict' (for dict-like value lookup)
     or 'attr' (for attribute-like lookup).

  * `comp`:: The value comparison method: either a '==' or 'is' string, to use that
    python operator in the comparison; or use a custom 2-argument function that takes
    two input values to compare and returns True (False) if the two values match
    (don't match).
  """
  # Imported 20150819
  # Original subroutine name: search_var_name (from Cr2_analysis_cbs.py).
  if lookup == "dict":
    names = namespace.keys()
  elif lookup in ("attr", "attribute", "class"):
    # attribute lookup
    names = dir(namespace)
  else:
    raise ValueError, "Invalid `lookup` argument"

  if prefix is not None:
    names_filt = [ n for n in names if n.startswith(prefix) ]
  elif rx_match is not None:
    # TODO later: for my regexp object?
    if True:
      if isinstance(rx_match, basestring):
        names_filt = [ n for n in names if re.search(rx_match, n) ]
      else:
        # assume a re.RegexObject-like object:
        names_filt = [ n for n in names if rx_match.search(n) ]
  else:
    names_filt = names
  names_match = []

  if callable(comp):
    # TODO: make sure it is a 2-arg function
    pass
  elif comp == "==":
    comp = lambda v, val: (type(v) is type(val)) and (v == val)
  elif comp == "is":
    comp = lambda v, val: (type(v) is type(val)) and (v is val)
  else:
    raise ValueError, "Invalid `comp` argument"

  if lookup == "dict":
    for n in names_filt:
      try:
        v = namespace[n]
      except:
        continue
      if comp(v, val):
        names_match.append(n)
  else:
    for n in names_filt:
      try:
        v = getattr(namespace, n)
      except:
        continue
      if comp(v, val):
        names_match.append(n)
  return names_match

