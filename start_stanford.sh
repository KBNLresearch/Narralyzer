#!/bin/bash

#
# start_stanford.sh
# This file is part of the narralyzer package.
# see: http://github.com/

#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#  
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

JAVA=`which java`

# private little hack ;)
if [ $HOSTNAME == "fe2" ]; then
    JAVA=/home/aloha/java/bin/java
fi

MEM="-mx4g"

cd stanford/core/

OS=`uname`
# Some machines (older OS X, BSD, Windows environments) don't support readlink -e
if hash readlink 2>/dev/null; then
  scriptdir=`dirname $0`
else
  scriptpath=$(readlink -e "$0") || scriptpath=$0
  scriptdir=$(dirname "$scriptpath")
fi

echo java -mx5g -cp \"$scriptdir/*\" edu.stanford.nlp.pipeline.StanfordCoreNLP $*

DE_CLASSIFIER='../models//edu/stanford/nlp/models/ner/german.dewac_175m_600.crf.ser.gz'
DE_PORT=9990

EN_CLASSIFIER='../models//edu/stanford/nlp/models/ner/english.all.3class.distsim.crf.ser.gz'
EN_PORT=9991

NL_CLASSIFIER='../../models/dutch.crf.gz'
NL_PORT=9992

SP_CLASSIFIER='../models//edu/stanford/nlp/models/ner/spanish.ancora.distsim.s512.crf.ser.gz'
SP_PORT=9993

SUPPORTED_LANG="DE EN NL SP"
#SUPPORTED_LANG="NL"

for lang in $(echo $SUPPORTED_LANG | xargs);do
    port=$(eval "echo \$${lang}_PORT")
    classifier=$(eval "echo \$${lang}_CLASSIFIER")
    ($JAVA $MEM -Djava.net.preferIPv4Stack=true -cp "$scriptdir/*" edu.stanford.nlp.ie.NERServer -port $port -loadClassifier $classifier -outputFormat inlineXML) &
    echo $lang $port
done

cd -
