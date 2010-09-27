#!/bin/bash
rsync -av . jaguar:/ccs/home/wirawan0/wpylib/. -f '+ *.py' -f '+ /*/' -f '- *' 
