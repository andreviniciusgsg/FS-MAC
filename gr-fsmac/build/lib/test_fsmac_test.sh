#!/bin/sh
export VOLK_GENERIC=1
export GR_DONT_LOAD_PREFS=1
export srcdir=/Users/andre.gomes/temp/FS-MACplus/gr-fsmac/lib
export GR_CONF_CONTROLPORT_ON=False
export PATH=/Users/andre.gomes/temp/FS-MACplus/gr-fsmac/build/lib:$PATH
export DYLD_LIBRARY_PATH=/Users/andre.gomes/temp/FS-MACplus/gr-fsmac/build/lib:$DYLD_LIBRARY_PATH
export PYTHONPATH=$PYTHONPATH
test-fsmac 
