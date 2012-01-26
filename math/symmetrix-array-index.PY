# 20100427

"""
Symmetric array layout (lower diagonal, Fortran column-major ordering):
i >= j

     ----> j
  |  (1,1)
i |  (2,1)   (2,2)
  v  (3,1)   (3,2)   (3,3)
       :       :       :
     (N,1)   (N,2)   (N,3) ... (N,N)

The linear index goes like this:

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

"""
Update 20120124:

Faster LDdec is possible.
The jskip formula can be written in similar fashion to
the 'UD' array format, as shown below.

The endpoint of the array index is N(N+1)/2 .
The (negative) offset of the j index from the rightmost column is
dj = (N + 1 - j).
Note: dj is 1 on the rightmost column.

So, the jskip is given by:

N(N+1)/2 - (N+1-j)(N+2-j) / 2 =
  = [ N**2 + N - ( N**2 + 3N - 2jN + 2 - 3j + j**2 ) ] / 2
  = ( -2N + 2jN - 2 + 3j - j**2 ) / 2
  = (j-1)N + (j-2)(j-1)/2
  >>> the same formula as before.

We can now make a similar analysis as in UD case to make a j_guess
formula:

  j_guess = int( N+1 - sqrt((N(N+1)/2 - ij) * 2) )

Note that:
  ij = N(N+1)/2 - (N+1-j)(N+2-j)/2 + i-j+1

Now focus on this expression:

  xj := ( N(N+1)/2 - ij) * 2
      = (N+1-j)*(N+2-j) - 2*(i+1-j)

So the maximum value of xj (for i=j) is:

  xj_max = (N+1-j)*(N+2-j) - 2
         = (N+1-j)**2 + (N+1-j) - 2

  xj_min = (N+1-j)*(N+2-j) - 2*(N+1-j)
         = (N+1-j)**2 - (N+1-j)

Again, these values satisfy the inequality

  (N-j)**2 < xj_min <= xj_max < (N+2-j)**2

Thus translates to
  N-j <= int(sqrt(xj)) <= N+1-j

or
  j <= j_guess <= j+1
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


# These are the reference implementation:

def LD(i,j,N):
  """python equivalent of gafqmc_LD on nwchem-gafqmc integral
  dumper module.
  Translates a lower-diagonal index (ii >= jj) to linear index
  0, 1, 2, 3, ...
  This follows python convention; thus 0 <= i < N, and so also j.

  """
  # iskip is row traversal, jskip is column traversal.
  # (iskip+jskip) is the final array index.
  if i >= j:
    ii = i
    jj = j
  else:
    ii = j
    jj = i

  iskip = ii - jj # + 1
  jskip = (jj)*N - (jj-1)*(jj)//2  # for 0-based
  return iskip + jskip

def LD1(i,j,N):
  """python equivalent of gafqmc_LD on nwchem-gafqmc integral
  dumper module.
  Translates a lower-diagonal index (ii >= jj) to linear index
  0, 1, 2, 3, ...
  This follows Fortran convention; thus 1 <= i <= N, and so also j.

  """
  # iskip is row traversal, jskip is column traversal.
  # (iskip+jskip) is the final array index.
  if i >= j:
    ii = i
    jj = j
  else:
    ii = j
    jj = i

  iskip = ii - jj + 1
  jskip = (jj-1)*N - (jj-2)*(jj-1)//2  # for 1-based
  return iskip + jskip


def LDdec(ij, N):
  """Back-translates linear index 0, 1, 2, 3, ... to a lower-diagonal
  index pair (ii >= jj).
  This is not optimal, but it avoids storing an auxiliary array
  that is easily computable. Plus, this function is supposed to
  be called rarely.
  """
  jskip = 0
  for j in xrange(N):
    if jskip + (N - j) > ij:
      jj = j
      ii = ij - jskip + j
      return (ii,jj)
    jskip += N - j

  raise ValueError, "LDdec(ij=%d,N=%d): invalid index ij" % (ij,N)

def LDdec1(ij, N):
  """Back-translates linear index 1, 2, 3, ... to a lower-diagonal
  index pair (ii >= jj).
  This is not optimal, but it avoids storing an auxiliary array
  that is easily computable. Plus, this function is supposed to
  be called rarely.
  """
  jskip = 0
  for j in xrange(1, N+1):
    if jskip + (N + 1 - j) >= ij:
      jj = j
      ii = ij - jskip + j - 1
      return (ii,jj)
    jskip += (N + 1 - j)

  raise ValueError, "LDdec1(ij=%d,N=%d): invalid index ij" % (ij,N)

def LDdec1_v2(ij, N):
  """Version 2, avoiding loop, but adding sqrt() function
  """
  from numpy import sqrt
  LDsize = N*(N+1) // 2
  j = N + 1 - int( sqrt((LDsize - ij) * 2) )
  jskip = (j-1)*N - (j-2)*(j-1)//2
  if ij > jskip:
    pass # correct already
  else:
    j = j - 1
    jskip = (j-1)*N - (j-2)*(j-1)//2
  i = ij - jskip + j - 1
  return (i,j)

# end reference implementation

def test_LD_enc_dec(N):
  """Simple test to check LD encoding and decoding correctness.
  For python-style indexing (0 <= i < N, similarly for j)."""
  for i in xrange(N):
    for j in xrange(N):
      ij = LD(i,j,N)
      (ii,jj) = LDdec(ij,N)
      print "%3d %3d | %6d | %3d %3d" % (i,j, ij, ii,jj)


def test_LD_enc_dec_diagonal(N):
  """Simple test to check LD encoding and decoding correctness.
  For python-style indexing (0 <= i < N, similarly for j).
  For diagonal element only
  """
  from numpy import sqrt
  LDsize = N * (N+1) / 2
  for i in xrange(N):
      j = i
      ij = LD(i,j,N)
      (ii,jj) = LDdec(ij,N)
      jj2 = int( sqrt(((LDsize) - ij) * 2) )
      print "%3d %3d | %6d ( %6d %6d ) | %3d %3d // %3d %3d" % (
        i,j,
        ij,
        ij-LDsize, -2*(ij-LDsize),
        ii,jj,
        -1, jj2)
      #                      ^^ distance from end of array

def Hack2_LD_enc_dec(N):
  """Simple test to check LD encoding and decoding correctness.
  For python-style indexing (0 <= i < N, similarly for j)."""
  from numpy import sqrt
  LDsize = N * (N+1) / 2
  for j in xrange(N):
    for i in xrange(j,N):
      ij = LD(i,j,N)
      (ii,jj) = LDdec(ij,N)
      jj2 = ( sqrt(((LDsize) - ij) * 2) )
      j_guess = int(N + 1 - jj2)  # for some reason this is the one that works for 0-based index
      ok1 = (jj <= j_guess)
      ok2 = (j_guess <= jj+1)
      ok = ((jj <= j_guess) and (j_guess <= jj+1))
      #print "%3d %3d | %6d | %3d %3d" % (i,j, ij, ii,jj)
      if not ok:
        # Verified OK empirically till N=1000.
        print "%3d %3d | %6d   %6d  | %3d %3d // %8.4f %3d  %c %d %d" % (
          i,j,
          ij, (LDsize-ij) * 2,
          ii,jj,
          jj2, j_guess, ("." if ok else "X"), ok1,ok2)

def Hack3_LD_enc_dec(N, print_all=False):
  """Simple test to check LD encoding and decoding correctness.
  For Fortran-style indexing (1 <= i <= N, similarly for j)."""
  from numpy import sqrt
  LDsize = N * (N+1) / 2
  for j in xrange(1,N+1):
    for i in xrange(j,N+1):
      ij = LD1(i,j,N)
      (ii,jj) = LDdec1(ij,N)
      (ii,jj) = LDdec1_v2(ij,N)
      jj2 = ( sqrt(((LDsize) - ij) * 2) )
      j_guess = N + 1 - int(jj2)
      OK = (ii==i and jj==j)
      ok1 = (jj <= j_guess)
      ok2 = (j_guess <= jj+1)
      ok = ((jj <= j_guess) and (j_guess <= jj+1))
      #print "%3d %3d | %6d | %3d %3d" % (i,j, ij, ii,jj)
      if print_all or not (OK and ok):
        # Verified OK empirically till N=1000.
        print "%3d %3d | %6d   %6d  | %3d %3d  %c  // %8.4f %3d  %c %d %d" % (
          i,j,
          ij, (LDsize-ij) * 2,
          ii,jj, ("." if OK else "X"),
          jj2, j_guess, ("." if ok else "X"), ok1,ok2)



###############################################################################


"""
UPPER DIAGONAL IMPLEMENTATION

j >= i
Should be easier (?)
Symmetric array layout (lower diagonal, Fortran column-major ordering):


     ----> j
  |  (1,1)   (1,2)   (1,3) ... (1,N)
i |          (2,2)   (2,3) ... (2,N)
  v                  (3,3) ... (3,N)
                            :    :
                               (N,N)

The linear index goes like this:
       1       2       4   ... N*(N+1)/2-4
               3       5   ... N*(N+1)/2-3
                       6   ... N*(N+1)/2-2
                            :  N*(N+1)/2-1
                               N*(N+1)/2

# For 1-based indices:

iskip = i - j    (easy)
jskip = j * (j+1) / 2

In the large j limit, jskip is approximately 0.5*j**2 .
This means that the j can be 'guessed' by:
  j_guess = int( sqrt(ij * 2) )
          = int( sqrt(j * (j + 1) + (i - j)*2) )
          = int( sqrt(j**2 + 2*i - j) )

Remember that i <= j, so j_guess ranges from (inclusive endpoints):

  j_guess_min = int( sqrt(j**2 - j + 2) )
  j_guess_max = int( sqrt(j**2 + j) )

Note: since

  sqrt((j-1)**2) = sqrt(j**2 - 2j + 1)
  sqrt((j+1)**2) = sqrt(j**2 + 2j + 1)

this means that, for all j > 0,
  j_guess_min >= j-1
  j_guess_max = j

So only those two j values matter.
Once we get the j, we can get the i value easily.

# For 0-based indices:

iskip = i - j    (easy)
jskip = (j+1) * (j+2) / 2 - 1
"""

def UD(i,j,N):
  """Translates a lower-diagonal index (ii <= jj) to linear index
  0, 1, 2, 3, ...
  This follows python convention; thus 0 <= i < N, and so also j.

  """
  # iskip is row traversal, jskip is column traversal.
  # (iskip+jskip) is the final array index.
  if i <= j:
    ii = i
    jj = j
  else:
    ii = j
    jj = i

  iskip = ii - jj # + 1
  jskip = (j+1) * (j+2) // 2 - 1  # for 0-based
  return iskip + jskip

def UDdec(ij, N):
  """Back-translates linear index 0, 1, 2, 3, ... to a lower-diagonal
  index pair (ii <= jj).
  This is not optimal, but it avoids storing an auxiliary array
  that is easily computable. Plus, this function is supposed to
  be called rarely.
  Derived from the 1-based version (UDdec1) below.
  """

  jskip = 0
  for j in xrange(1,N+1):
    jskip = j * (j+1) // 2
    if ij < jskip:
      i = ij - jskip + j
      return (i,j-1)


def UD1(i,j,N):
  """The 1-based version of UD
  """
  # iskip is row traversal, jskip is column traversal.
  # (iskip+jskip) is the final array index.
  if i <= j:
    ii = i
    jj = j
  else:
    ii = j
    jj = i

  iskip = ii - jj
  jskip = (j) * (j+1) // 2  # for 1-based
  return iskip + jskip

def UDdec1(ij, N):
  """Back-translates linear index 1, 2, 3, ... to a lower-diagonal
  index pair (ii <= jj).
  This is not optimal, but it avoids storing an auxiliary array
  that is easily computable. Plus, this function is supposed to
  be called rarely.
  """
  jskip = 0
  for j in xrange(1,N+1):
    jskip = j * (j+1) // 2
    if ij < jskip + 1:
      """
      ij = iskip + jskip
      -> iskip = ij - jskip = i - j
      -> i = ij - jskip + j
      """
      i = ij - jskip + j
      return (i,j)

  raise ValueError, "UDdec1(ij=%d,N=%d): invalid index ij" % (ij,N)


def UDdec1_v2(ij, N):
  """Back-translates linear index 1, 2, 3, ... to a lower-diagonal
  index pair (ii <= jj).
  Version 2, avoiding loop at a cost of doing sqrt() call.
  """
  from numpy import sqrt
  j = int(sqrt(ij*2+1))
  jskip = j * (j+1) // 2
  if ij < jskip + 1:
    pass # correct already
  else:
    j = j + 1
    jskip = j * (j+1) // 2
  i = ij - jskip + j
  return (i,j)

def UDdec1_v3(ij, N):
  """Back-translates linear index 1, 2, 3, ... to a lower-diagonal
  index pair (ii <= jj).
  Version 3, avoiding loop at a cost of doing sqrt() call.
  """
  from numpy import sqrt
  j = int(sqrt(ij*2))  # +1 not needed?
  jskip = j * (j+1) // 2
  if ij < jskip + 1:
    pass # correct already
  else:
    j = j + 1
    jskip = j * (j+1) // 2
  i = ij - jskip + j
  return (i,j)


def test_UD_enc_dec(N):
  """Simple test to check UD encoding and decoding correctness.
  For python-style indexing (0 <= i < N, similarly for j)."""
  # Success for N = 5, 8
  for j in xrange(N):
    for i in xrange(0,j+1):
      ij = UD(i,j,N)
      (ii,jj) = UDdec(ij,N)
#      print "%3d %3d | %6d | %3d %3d" % (i,j, ij, ii,jj)
      print "%3d %3d | %6d | %3d %3d   >> %1s" % (i,j, ij, ii,jj, ("v" if i==ii and j==jj else "X"))

def test_UD_enc_dec1(N):
  """Simple test to check UD encoding and decoding correctness.
  For python-style indexing (0 <= i < N, similarly for j)."""
  for j in xrange(1,N+1):
    for i in xrange(1,j+1):
      ij = UD1(i,j,N)
      (ii,jj) = UDdec1(ij,N)
      print "%3d %3d | %6d | %3d %3d   >> %1s" % (i,j, ij, ii,jj, ("v" if i==ii and j==jj else "X"))

def hack1_UD_enc_dec1(N):
  """Simple test to check UD encoding and decoding correctness.
  For Fortran-style indexing (1 <= i <= N, similarly for j)."""
  from numpy import sqrt
  ok = True
  for j in xrange(1,N+1):
    for i in xrange(1,j+1):
      ij = UD1(i,j,N)
      (ii,jj) = UDdec1(ij,N)
      #iii = i
      #jjj = int(sqrt(ij*2+1))
      #(iii,jjj) = UDdec1_v2(ij,N)  # -- tested OK empirically till N=1000
      (iii,jjj) = UDdec1_v3(ij,N) # also tested OK empirically till N=1000
      if not (i==iii and j==jjj):
        ok=False
        print "%3d %3d | %6d %6d | %3d %3d  : %3d %3d >> %1s" % (
          i,j,
          ij, ij*2,
          ii,jj,
          iii, jjj,
          ("v" if i==iii and j==jjj else "X"))
  print ("ok" if ok else "NOT OK")


