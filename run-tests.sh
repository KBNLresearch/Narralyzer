#!/usr/bin/env bash

# This file is part of narralyzer
# http://www.narralyzer.com/

. start_stanford.sh
while true; do nc -w 1 127.0.0.1 9991 && break; sleep 1; echo "."; done
while true; do nc -w 1 127.0.0.1 9992 && break; sleep 1; echo "."; done
. env/bin/activate
python2.7 ./narralyzer/lang_lib.py test || exit -
python2.7 ./narralyzer/stanford_ner_wrapper.py test || exit -
