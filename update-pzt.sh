#!/bin/bash
rsync -av . pzt:/home/wirawan0/local/lib/python/wpylib/. -f '+ *.py' -f '- CVS/' -f '+ /**/' -f '- *' 
