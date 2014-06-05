
from copy import copy, deepcopy
from pprint import pprint
import wpylib.sugar

def def_dict_data1():
  """[20140605]
  """
  global DN1, DN2
  global DN1_orig, DN2_orig
  DN1 = {
    'A': 'executive',
    'B': {
      'member': 1,
      'properties': dict(
         names = ['Abe'],
         keys = ['0xfc133'],
      ),
    },
    'C': {
      'member': 3,
      'properties': dict(
         names = ['Connor', 'Dewey', 'Elaine'],
         keys = ['0x91', 42, -3.241],
         nest1 = {
           0: 91, 1: 32, 2: 41,
         },
      ),
    },
  }
  DN1_orig = deepcopy(DN1)

  DN2 = {
    'A': 'slave',
    'B': {
      'member': -1,
      'properties': dict(
        bother = 'pooh',
      ),
    },
    'C': {
    },
  }
  DN2_orig = deepcopy(DN2)



def test_dict_update_nested1():
  """[20140605]
  """
  from wpylib.sugar import dict_update_nested
  def_dict_data1()
  DN1 = deepcopy(DN1_orig)
  DN2 = deepcopy(DN2_orig)

  print "test_dict_update_nested1():"
  print "DN1:"
  pprint(DN1)

  print
  print "DN2:"
  pprint(DN2)

  print
  print "Update DN1 with DN2, nested:..."
  dict_update_nested(DN1, DN2)
  pprint(DN1)

  print
  print "# bother DN2:"
  DN2['B']['properties']['roo'] = 'kanga'
  pprint(DN1)

  print
  print "Update DN1 with DN2, nested: max nest = 0..."
  DN1 = deepcopy(DN1_orig)
  DN2 = deepcopy(DN2_orig)
  dict_update_nested(DN1, DN2, max_nest=0)
  print "DN1:"
  pprint(DN1)

  print
  print "# bother DN2: properties should now have 'roo = kanga' mapping"
  DN2['B']['properties']['roo'] = 'kanga'
  print "DN1:"
  pprint(DN1)

  print
  print "Update DN1 with DN2, nested: max nest = 1..."
  DN1 = deepcopy(DN1_orig)
  DN2 = deepcopy(DN2_orig)
  dict_update_nested(DN1, DN2, max_nest=1)
  print "DN1:"
  pprint(DN1)

  print
  print "# bother DN2: (clear B dict) -- DN1['B'] should not be affected"
  DN2['B'].clear()
  print "DN1:"
  pprint(DN1)



def test_dict_update_nested2():
  """[20140605]
  """
  from wpylib.sugar import dict_update_nested
  def_dict_data1()
  DN1 = deepcopy(DN1_orig)
  DN2 = deepcopy(DN2_orig)

  print "test_dict_update_nested2():"
  print "DN1:"
  pprint(DN1)

  print
  print "DN2:"
  pprint(DN2)

  print
  print "Update DN2 with DN1, nested:..."
  dict_update_nested(DN2, DN1)
  pprint(DN2)

  print
  print "Update DN2 with DN1, nested: max nest = 0..."
  DN1 = deepcopy(DN1_orig)
  DN2 = deepcopy(DN2_orig)
  dict_update_nested(DN2, DN1, max_nest=0)
  pprint(DN2)


if __name__ == "__main__":
  test_dict_update_nested1()

