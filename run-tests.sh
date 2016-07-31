#!/usr/bin/env bash
<<<<<<< HEAD
=======

timeout 1 bash -c 'cat < /dev/null > /dev/tcp/localhost/9991'
while [ $? == "1" ]; do
    timeout 1 bash -c 'cat < /dev/null > /dev/tcp/localhost/9991'
    sleep 1
    echo "Stanford not ready, waiting to boot.."
done



timeout 1 bash -c 'cat < /dev/null > /dev/tcp/localhost/9990'
while [ $? == "1" ]; do
    sleep 1
    echo "Stanford not ready, waiting to boot.."
    timeout 1 bash -c 'cat < /dev/null > /dev/tcp/localhost/9990'
done

>>>>>>> 2f971bf0e11bc863b2b41b470ce1623a2463a7fb
. start_stanford.sh
sleep 60
. env/bin/activate
python2.7 ./narralyzer/lang_lib.py test
python2.7 ./narralyzer/stanford_ner_wrapper.py test
