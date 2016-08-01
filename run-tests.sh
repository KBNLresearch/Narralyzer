#!/usr/bin/env bash

#
# File: run-tests.sh
#
# This file is part of the Narralyzer package.
# see: http://github.com/WillemJan/Narralyzer
#

# Little wrapper to datestamp outgoing messages.
function inform_user() {
    msg="$1"
    timestamp=`date "+%Y-%m-%d %H:%M"`
    echo "$timestamp: Narralyzer start_stanford.sh $msg"
}


(
inform_user "Starting Stanford."
. start_stanford.sh waitforstartup

inform_user "Crawling into virtualenv."
. env/bin/activate

inform_user "Running doctests for: ./narralyzer/lang_lib.py"
python2.7 ./narralyzer/lang_lib.py test || exit -1

inform_user "Running doctests for: ./narralyzer/stanford_ner_wrapper.py"
python2.7 ./narralyzer/stanford_ner_wrapper.py test || exit -1
) || exit -1
