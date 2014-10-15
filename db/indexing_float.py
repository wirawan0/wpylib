#
# wpylib.db.indexing_float
# Utilities for indexing based on floating-point values
#
# Wirawan Purwanto
# Created: 20130301
#

"""\
wpylib.db.indexing_float
Utilities for indexing based on floating-point values
"""

import numpy
import sys


def _debug_gen_float_indices1(localvars, debug):
  from wpylib.params.params_flat import Parameters as params
  L = params(localvars)
  if debug > 50:
    print "a_sorted         = ", L.a_sorted[1:]
    print "a_diff           = ", L.a_diff
    print "a_avg_abs        = ", L.a_avg_abs
    print "a_rdiff          = ", L.a_rdiff
    print
    #print "rdiff_idx_sorted =   ", L.rdiff_idx_sorted  #   numpy.array(L.rdiff_idx_sorted, dtype=float)
    print "rdiff_idx_sorted =  ", " ".join([ "%11d" % i for i in L.rdiff_idx_sorted ])
    print "too_close        =  ", " ".join([ "%11d" % int(i) for i in (L.a_rdiff[L.rdiff_idx_sorted] < L.rdiff_threshold) ])
    print "a_rdiff(sort)    = ", L.a_rdiff[L.rdiff_idx_sorted]
    print "a(sort)          = ", L.a_sorted[1:][L.rdiff_idx_sorted]
    print

def _debug_gen_float_indices2(localvars, debug):
  from wpylib.params.params_flat import Parameters as params
  L = params(localvars)
  if debug > 50:
    print
    print "a_rdiff aft      = ", L.a_rdiff
    print "num unique vals  = ", L.n_all_unique_vals
    print "num already uniq = ", len(L.a_already_unique)
    print "unique_vals      = ", L.unique_vals[0:L.n_all_unique_vals]
    print "unique_vals(sort)= ", numpy.sort(L.unique_vals[0:L.n_all_unique_vals])

def _debug_gen_float_indices_found_duplicates(localvars, debug):
  from wpylib.params.params_flat import Parameters as params
  L = params(localvars)
  if debug > 100:
    print "i=", L.i_found, " fused range is ", L.i1, ":", L.i+1
    print " rdiff", L.orig_rdiff
    print "  idx ", L.i1, L.i, ", arr ", L.a_fused_sect
    print "  avg ", L.avg

def _debug_gen_float_indices_results(localvars, debug):
  from wpylib.params.params_flat import Parameters as params
  L = params(localvars)
  if debug > 50:
    print
    print "rslt_vals        = ", L.rslt_vals
    print "unique_map       = ", L.unique_map



def generate_float_indices(arr, rdiff_threshold, debug=0):
  """Consolidates floating point values to `unique' values whose relative
  differences are greater than a specified threshold (rdiff_threshold).
  Values that are so close together will fused to their average.

  The input must be a one-dimensional array or list or a list-like iterable.
  """
  from wpylib.db.result_base import result_base
  sample = numpy.array([arr[0]])
  a_sorted = numpy.empty(len(arr)+1, dtype=sample.dtype)
  a_sorted[1:] = arr
  a_sorted[1:].sort(kind='heapsort')
  a_sorted[0] = a_sorted[1] # dummy data
  a_diff = numpy.diff(a_sorted)  # == a_sorted[1:] - a_sorted[:-1]
  a_avg_abs = (numpy.abs(a_sorted[1:]) + numpy.abs(a_sorted[:-1])) * 0.5
  # FIXME: handle case where a_avg_abs is truly ZERO -> in this case
  # the abs should be 1.
  a_rdiff = numpy.abs(a_diff) / a_avg_abs
  # hack the first rdiff since this element *must* always be present,
  # so this trick marks it as "unique":
  a_rdiff[0] = rdiff_threshold*100
  # free up the memory:
  if not debug:
    a_diff = None
    a_avg_abs = None
  # Elements whose rdiff < rdiff_cutoff should be consolidated.
  # Since there is no easy way to find these elements in bulk,
  # I resort to "sorting": :(
  rdiff_idx_sorted = numpy.argsort(a_rdiff, kind='mergesort')

  _debug_gen_float_indices1(locals(), debug)

  imax = len(rdiff_idx_sorted)
  # unique_map: mapping from original indices to unique indices
  unique_map = {}
  # unique_set: set of unique-ized elements, excluding those that
  # are distinct by their numerical distances
  unique_vals = numpy.empty((len(arr),), dtype= sample.dtype) # max len
  n_unique_vals = 0
  rslt = None
  for (last_idx,i) in enumerate(rdiff_idx_sorted):
    if a_rdiff[i] > rdiff_threshold:
      # Stop, all the rest of the values are unique.
      break
    elif a_rdiff[i] == -1:
      continue
    else:
      # If two values are adjacent (e.g. in this case
      # a_sorted[i] and a_sorted[i+1] -- note the dummy value
      # at element 0), there may be more than one values like that,
      # so we need to take care of that too.
      # This is why the lower bound of the indices below is "i1"
      # while the upper is "i".
      i_found = i
      i1 = i

      while i1 > 0 and a_rdiff[i1-1] <= rdiff_threshold: i1 -= 1
      i += 1
      while i < imax and a_rdiff[i] <= rdiff_threshold: i += 1
      orig_rdiff = a_rdiff[i1-1:i].copy()
      a_rdiff[i1-1:i] = -1

      a_fused_sect = a_sorted[i1:i+1]
      avg = numpy.mean(a_fused_sect)
      unique_vals[n_unique_vals] = avg
      for a in a_fused_sect:
        unique_map[a] = n_unique_vals
      n_unique_vals += 1

      _debug_gen_float_indices_found_duplicates(locals(), debug)

  # unique_vals will contain the unique elements.
  # - Then, copy over the rest elements who are already unique
  # - Also, complete the value-to-index lookup
  a_already_unique = [ a_sorted[i+1] for i in rdiff_idx_sorted[last_idx:] if a_rdiff[i] != -1 ]
  n_all_unique_vals = n_unique_vals + len(a_already_unique)
  unique_vals[n_unique_vals:n_all_unique_vals] = a_already_unique
  _debug_gen_float_indices2(locals(), debug)

  dn = 0
  for i in rdiff_idx_sorted[last_idx:]:
    if a_rdiff[i] == -1: continue
    a = a_sorted[i+1]
    unique_map[a] = n_unique_vals + dn
    dn += 1

  # Sort the indices based on the unique value
  rslt_sort_idx = unique_vals[:n_all_unique_vals].argsort(kind='heapsort')
  rslt_sort_ridx = dict((b,a) for (a,b) in enumerate(rslt_sort_idx))

  # Update the value-to-index lookup and return the sorted index array
  for a in unique_map.keys():
    #unique_map[a] = rslt_sort_idx[unique_map[a]]
    unique_map[a] = rslt_sort_ridx[unique_map[a]]
  rslt_vals = unique_vals[rslt_sort_idx]

  _debug_gen_float_indices_results(locals(), debug)

  return result_base(
    # list of unique indices, sorted in ascending order:
    vals=rslt_vals,
    # mapping from less-unique values to the index of the new (unique-ized) new , sorted in ascending order
    index_mapping=unique_map,
  )

