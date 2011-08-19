""" -*- python -*-
FOO.py

A skeleton for ipython interactive script

"""

import datetime
import numpy
import os
import os.path
import sys
import re

import wpylib.shell_tools as sh
from wpylib.interactive_tools import init_interactive

from wpylib.params import struct
from wpylib.params import flat as params
from wpylib.sugar import ifelse
from wpylib.iofmt.text_input import text_input
from wpylib.iofmt.text_output import text_output
from wpylib.math.linalg import matmul

#import pyqmc.matrices.gms as gms

init_interactive()

_g = globals()

'''# -- for GAFQMC-targeted scripts
if "GAFQMC" not in _g:
  GAFQMC = os.environ['GAFQMC']
  sys.path.append(os.path.join(GAFQMC, 'scripts'))

# Now include the GAFQMC-specific modules here:
#import V2b_inspect
'''
