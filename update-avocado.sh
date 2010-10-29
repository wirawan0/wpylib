#!/bin/bash
rsync -av . avo:/home/wirawan0/lib/python/wpylib/. -f '+ *.py' -f '- CVS/' -f '+ /**/' -f '- *'
