#!/usr/bin/env bash

#
# File: run-tests.sh
#
# This file is part of the Narralyzer package.
# see: http://lab.kb.nl/tool/narralyzer

# Little wrapper to datestamp outgoing messages.
function inform_user() {
    msg="$1"
    timestamp=`date "+%Y-%m-%d %H:%M"`
    echo "$timestamp: Narralyzer start_stanford.sh $msg"
}

function run_test() {
    fname="$1"
    inform_user "Running doctests for: $fname"
    python2.7 "$fname" test || exit -1
}


(
inform_user "Starting Stanford."
. start_stanford.sh waitforstartup

inform_user "Crawling into virtualenv."
. env/bin/activate

run_test "./narralyzer/stanford_ner_wrapper.py"
run_test "./narralyzer/lang_lib.py"
run_test "./narralyzer/utils.py"
) || exit -1
