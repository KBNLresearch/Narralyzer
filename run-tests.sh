#!/usr/bin/env bash

. start_stanford.sh
. env/bin/activate
python2.7 ./narralyzer/lang_lib.py test
python2.7 ./narralyzer/stanford_ner_wrapper.py test
