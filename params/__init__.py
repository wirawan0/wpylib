# $Id: __init__.py,v 1.2 2011-03-10 19:22:37 wirawan Exp $
#
# wpylib.params module
# Created: 20100930
# Wirawan Purwanto

"""Parameter-related stuff.

Exported names:

* flat - flat parameter namespace (but with a sequence of dicts/namespaces
  to look value from).
* struct - struct-like container. Do not confuse with python's built-in
  'struct' class!
"""

from wpylib.params.params_flat import Parameters as flat
from wpylib.params.params_struct import Struct as struct

