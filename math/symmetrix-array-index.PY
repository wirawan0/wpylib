# 20100427

"""
Symmetric array layout (lower diagonal, Fortran column-major ordering):


     ----> j
  |  (1,1)
i |  (2,1)   (2,2)
  v  (3,1)   (3,2)   (3,3)
       :       :       :
     (N,1)   (N,2)   (N,3) ... (N,N)

In linear form:

       1
       2      N+1
       3      N+2     2N
       :       :       :
       N     N+N-1



iskip = i - j + 1   (easy)

jskip determination
  i     jskip        jskip
        (cumulant)   (total)
  1        0
  2        N
  3        N-1
  4        N-2
  ...
  j        N-(j-2)   (j-1)N - (j-2)(j-1)/2
  ...


Note:

    {m}
    SUM a = 1 + 2 + ... + m = m(m+1)/2
   {a=1}
"""

import numpy

def test_jskip_1(N, M):
  jskip1 = 0
  jskip2 = 0
  for m in xrange(1, M+1):
    if m == 1:
      cum = 0
    else:
      cum = N - (m-2)
    jskip2 = (m-1)*N - (m-2)*(m-1)/2
    jskip1 += cum
    print "%5d %5d %5d %5d" % (m, cum, jskip1, jskip2)


def copy_over_array(N, arr_L):
  rslt = numpy.zeros((N,N))
  for i in xrange(N):
    for j in xrange(N):
      if j > i: continue
      ii = i+1 # Fortranize it
      jj = j+1 # Fortranize it
      jskip = (jj-1)*N - (jj-2)*(jj-1)/2
      iskip = ii - jj + 1
      ldiag_index = iskip + jskip - 1 # -1 for C-izing again
      # indices printed in Fortran 1-based indices
      print "%5d %5d %5d %5d %5d" % (ii,jj,iskip,jskip,ldiag_index+1)
      rslt[i,j] = arr_L[ldiag_index]
  return rslt
