#!/bin/bash
rsync -av . jaguar-ext:/ccs/home/wirawan0/wpylib/. -f '+ *.py' -f '- CVS/' -f '+ /**/' -f '- *'
