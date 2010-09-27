#!/bin/bash
rsync -av . avo:/home/wirawan0/lib/python/wpylib/. -f '+ *.py' -f '+ *.basis' -f '+ /**/' -f '- *' 
