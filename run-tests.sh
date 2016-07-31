#!/usr/bin/env bash

. start_stanford.sh
python2.7 ./narralyzer/lang_lib.py test
python2.7 ./narralyzer/stanford_ner_wrapper.py test
