
import numpy


def test_array_hstack1():
  # 20150520
  from numpy import array
  from wpylib.array_tools import array_hstack

  print("test_array_hstack1::")

  A1 = array([[1.5, 2.3, 1.7],
              [3.5, 1.0, 9.7],
              [4.5, 3.0, 0.5],
              [5.0, 8.1, 2.4]])
  A2 = array([12.1, 21.5, 47.1, 32.1])
  A3 = array([1.1, 2.5, 7.7, 6.6])
  A123 = array_hstack((A1, A2, A3))

  A123_refs = array([[  1.5,   2.3,   1.7,  12.1,   1.1],
                     [  3.5,   1. ,   9.7,  21.5,   2.5],
                     [  4.5,   3. ,   0.5,  47.1,   7.7],
                     [  5. ,   8.1,   2.4,  32.1,   6.6]])
  print(A123)
  assert numpy.all(A123 == A123_refs)


def test_array_vstack1():
  # 20150520
  from numpy import array
  from wpylib.array_tools import array_vstack

  print("test_array_vstack1::")

  A1 = array([[1.5, 2.3, 1.7],
              [3.5, 1.0, 9.7],
              [4.5, 3.0, 0.5],
              [5.0, 8.1, 2.4]])
  A2 = array([12.1, 21.5, 47.1])
  A3 = array([1.1, 2.5, 7.7])
  A123 = array_vstack((A1, A2, A3))

  A123_refs = array([[  1.5,   2.3,   1.7],
                     [  3.5,   1. ,   9.7],
                     [  4.5,   3. ,   0.5],
                     [  5. ,   8.1,   2.4],
                     [ 12.1,  21.5,  47.1],
                     [  1.1,   2.5,   7.7]])

  print(A123)
  assert numpy.all(A123 == A123_refs)


if __name__ == '__main__':
  test_array_vstack1()
