#!/bin/sh
export VOLK_GENERIC=1
export GR_DONT_LOAD_PREFS=1
export srcdir=/home/gnuradio/FS-MAC/gr-fsmac/lib
export GR_CONF_CONTROLPORT_ON=False
export PATH=/home/gnuradio/FS-MAC/gr-fsmac/build/lib:$PATH
export LD_LIBRARY_PATH=/home/gnuradio/FS-MAC/gr-fsmac/build/lib:$LD_LIBRARY_PATH
export PYTHONPATH=$PYTHONPATH
test-fsmac 
