# -*- python -*-
#
# wpylib.py.introspection
# Created: 20150819
# Wirawan Purwanto
#
# Advanced introspection tools for python
#

def name_rlookup(val, namespace, prefix=None, rx_match=None, lookup="dict"):
  """Reverse lookup of variable/object name.

  Yields the list of object names in the namespace whose respective values are
  equal to `val`.

  This is useful for example to reverse-lookup an object's name, but only in
  restricted contexts (e.g. when the value to look for is unique).
  """
  # Imported 20150819
  # Original subroutine name: search_var_name (from Cr2_analysis_cbs.py).
  if lookup == "dict":
    names = namespace.keys()
  else:
    # attribute lookup
    names = dir(namespace)
  if prefix != None:
    names_filt = [ n for n in names if n.startswith(prefix) ]
  elif rx_match != None:
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
  type_val = type(val)
  if lookup == "dict":
    for n in names_filt:
      try:
        v = namespace[n]
      except:
        continue
      if type(v) == type_val and v == val:
        names_match.append(n)
  else:
    for n in names_filt:
      try:
        v = getattr(namespace, n)
      except:
        continue
      if type(v) == type_val and v == val:
        names_match.append(n)
  return names_match

