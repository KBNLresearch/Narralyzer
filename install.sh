#!/bin/bash

#
# If you run into troubles try this: 
# 
# sudo apt-get install -y build-essesntials libdb-dev virtualenv python2.7 libxml2-dev libxslt1-dev
#
# (Or leave a ping here: 


# Tika will take care of most input document conversion.
TIKA="http://apache.cs.uu.nl/tika/tika-app-1.13.jar"

# Stanford NER will be used to extract NER's from input documents.
STANFORD_CORE="http://nlp.stanford.edu/software/stanford-corenlp-full-2015-12-09.zip"
STANFORD_DE="http://nlp.stanford.edu/software/stanford-german-2016-01-19-models.jar"
STANFORD_EN="http://nlp.stanford.edu/software/stanford-english-corenlp-2016-01-10-models.jar"
STANFORD_FR="http://nlp.stanford.edu/software/stanford-french-corenlp-2016-01-14-models.jar"
STANFORD_SP="http://nlp.stanford.edu/software/stanford-spanish-corenlp-2015-10-14-models.jar"

function get_if_not_there () {
    URL=$1
    if [ ! -f `basename $URL` ]; then
        echo "Fetching $URL..."
        wget_output=$(wget -q "$URL")
        if [ $? -ne 0 ]; then
            echo "Error while fetching $URL, time to exit."
            exit -1;
        fi
    else
        echo "Not fetching $URL, `basename "$URL"` allready there."
    fi

}

function fetch_stanford_core {
    get_if_not_there $STANFORD_CORE
    if [ -f `basename $STANFORD_CORE` ]; then
        unzip -q -n `basename "$STANFORD_CORE"`
        rm `basename "$STANFORD_CORE"`
        ln -s `find -name \*full\* -type d` core
    fi
}

function fetch_stanford_lang_models {
    get_if_not_there $STANFORD_DE 
    get_if_not_there $STANFORD_EN 
    get_if_not_there $STANFORD_FR
    get_if_not_there $STANFORD_SP 
    find . -name \*.jar -exec unzip -q -o '{}' ';'
    rm *.jar
}

is_python2_7_avail() {
    is_avail=$(which python2.7 | wc -l)
    if [ "$is_avail" = "0" ]; then
        echo "Python 2.7 is not available, helas. sudo apt-get install python2.7"
        exit -1
    fi
    echo "Python 2.7 is available."
}

is_python2_7_avail() {
    is_avail=$(which virtualenv | wc -l)
    if [ "$is_avail" = "0" ]; then
        echo "virtualenv is not available, helas. sudo-apt-get install virtualenv"
        exit -1
    fi
    echo "Virtualenv is available."
}


#
#
#

if [ ! -d 'stanford' ]; then
    mkdir stanford && cd stanford
else
    cd stanford
fi
    
full=$(find -name \*full\* | wc -l)
if [ "$full" = "0" ];then
    fetch_stanford_core
else
    echo "Not fetching stanford-core, allready there."
fi

if [ ! -d 'models' ]; then
    mkdir models && cd models
    fetch_stanford_lang_models
    cd ..
else
    cd ..
fi

pip install -U pip setuptools

#is_python2_7_avail

#if [ ! -d 'env' ]; then
#    echo "Creating new virtualenv using python2.7 in ./env"
#    virtualenv -p python2.7 ./env
#
#    echo "Entering virtualenv, to leave: deactivate"
#    source env/bin/activate
#
#    echo "Installing the following packages via pip:"
#    cat requirements.txt
#    pip install -r requirements.txt
#fi


#if [ ! -d 'tika' ]; then
#    mkdir tika && cd tika
#    get_if_not_there $TIKA
#    unzip -q -n `basename "$TIKA"`
#    rm `basename "$TIKA"`
#fi
