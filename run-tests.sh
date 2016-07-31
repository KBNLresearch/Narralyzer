#!/usr/bin/env bash

timeout 1 bash -c 'cat < /dev/null > /dev/tcp/localhost/9991'
while [ $? == "1" ]; do
    timeout 1 bash -c 'cat < /dev/null > /dev/tcp/localhost/9991'
    sleep 1
    echo "Stanford not ready, waiting to boot.."
done



timeout 1 bash -c 'cat < /dev/null > /dev/tcp/localhost/9990'
while [ $? == "1" ]; do
    timeout 1 bash -c 'cat < /dev/null > /dev/tcp/localhost/9990'
    sleep 1
    echo "Stanford not ready, waiting to boot.."
done

. start_stanford.sh
. env/bin/activate
python2.7 ./narralyzer/lang_lib.py test
python2.7 ./narralyzer/stanford_ner_wrapper.py test
