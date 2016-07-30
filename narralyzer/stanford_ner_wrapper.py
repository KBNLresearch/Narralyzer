#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-
"""
    narralyzer.stanford_ner_wrapper
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    Implements tiny wrapper for Stanford CoreNLP NER.

    Hint's on setting up a high-preformance NER-farm.
    http://stanfordnlp.github.io/CoreNLP/corenlp-server.html#dedicated-server

    :copyright: (c) 2016 Koninklijke Bibliotheek, by Willem Jan Faber.
    :license: GPLv3, see licence.txt for more details.
"""


import logging
import lxml.html
import socket
import sys

from contextlib import contextmanager
from django.utils.encoding import smart_text

log = logging.basicConfig(stream=sys.stdout, level=logging.INFO)


@contextmanager
def _tcpip4_socket(host, port):
    """Open a TCP/IP4 socket to designated host/port.
    This code originates from 'pip install ner',
    but the module itself was broken, so took usefull code
    and improved on it.
    """

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(50)

    try:
        sock.connect((host, port))
        yield sock
    finally:
        try:
            sock.shutdown(socket.SHUT_RDWR)
        except socket.error:
            log.error("Socket error %s %s" % (host, str(port)))
            pass
        except OSError:
            log.error("OSEerror %s %s" % (host, str(port)))
            pass
        finally:
            sock.close()


def stanford_ner_wrapper(text, port, host='localhost'):
    """
    >>> res = stanford_ner_wrapper("Paris Hilton is bang dat terreurgroepen of individuen het op haar hebben gemunt. Ik ben een bekend persoon en zou zeker een doelwit kunnen zijn, zegt de socialite in een interview met Diario De Ibiza.", 9991)
    >>> from pprint import pprint;pprint(res)
    {'ners': [{'string': 'Paris Hilton', 'tag': 'location'},
              {'string': 'Diario De Ibiza', 'tag': 'organization'}],
     'raw_ners': [{'string': 'Paris Hilton', 'tag': 'location'},
                  {'string': 'Diario De Ibiza', 'tag': 'organization'}],
     'raw_response': u'<LOCATION>Paris Hilton</LOCATION> is bang dat terreurgroepen of individuen het op haar hebben gemunt. Ik ben een bekend persoon en zou zeker een doelwit kunnen zijn, zegt de socialite in een interview met <ORGANIZATION>Diario De Ibiza</ORGANIZATION>.'}
    >>> res = stanford_ner_wrapper("Paris Hilton is bang dat terreurgroepen of individuen het op haar hebben gemunt. Ik ben een bekend persoon en zou zeker een doelwit kunnen zijn, zegt de socialite in een interview met Diario De Ibiza.", 9992)
    >>> from pprint import pprint;pprint(res)
    {'ners': [{'string': 'Paris Hilton', 'tag': 'per'},
              {'string': 'Diario De Ibiza', 'tag': 'per'}],
     'raw_ners': [{'string': 'Paris', 'tag': 'b-per'},
                  {'string': 'Hilton', 'tag': 'i-per'},
                  {'string': 'Diario', 'tag': 'b-per'},
                  {'string': 'De Ibiza', 'tag': 'i-per'}],
     'raw_response': u'<B-PER>Paris</B-PER> <I-PER>Hilton</I-PER> is bang dat terreurgroepen of individuen het op haar hebben gemunt. Ik ben een bekend persoon en zou zeker een doelwit kunnen zijn, zegt de socialite in een interview met <B-PER>Diario</B-PER> <I-PER>De Ibiza</I-PER>.'}

    >>> res = stanford_ner_wrapper("Prof. Albert Einstein vertoeft op het oogenblik te Londen, en gisteravond was hij in Savoy Hotel eeregast aan een diner, gegeven door de Ort and Oze Societies. De voorzitter van de Engelsche sectie dier Vereeniging is Lord • Rothschild ; de voorzitter van de Duitsche sectie is prof. Einstein.  Lord Rothschild presideerde het diner; aan zijn rechterhand zat de beroemdste geleerde van onzen tyd, aan zijn linkerhand de beroemdste dichter, Bernard Shaw. Rechts van Einstein zat Wells.  Het was een gastmaal voor het intellect en z|jn dames.  Ik wil er geen verslag van geven, maar my bepalen tot enkele aanteekeningen.", 9991)
    >>> from pprint import pprint;pprint(res)
    {'ners': [{'string': 'Albert Einstein', 'tag': 'person'},
              {'string': 'Londen', 'tag': 'person'},
              {'string': 'Savoy Hotel', 'tag': 'location'},
              {'string': 'Vereeniging', 'tag': 'location'},
              {'string': 'Einstein', 'tag': 'person'},
              {'string': 'Bernard Shaw', 'tag': 'person'},
              {'string': 'Rechts van Einstein', 'tag': 'person'},
              {'string': 'Wells', 'tag': 'person'}],
     'raw_ners': [{'string': 'Albert Einstein', 'tag': 'person'},
                  {'string': 'Londen', 'tag': 'person'},
                  {'string': 'Savoy Hotel', 'tag': 'location'},
                  {'string': 'Vereeniging', 'tag': 'location'},
                  {'string': 'Einstein', 'tag': 'person'},
                  {'string': 'Bernard Shaw', 'tag': 'person'},
                  {'string': 'Rechts van Einstein', 'tag': 'person'},
                  {'string': 'Wells', 'tag': 'person'}],
     'raw_response': u'Prof. <PERSON>Albert Einstein</PERSON> vertoeft op het oogenblik te <PERSON>Londen</PERSON>, en gisteravond was hij in <LOCATION>Savoy Hotel</LOCATION> eeregast aan een diner, gegeven door de Ort and Oze Societies. De voorzitter van de Engelsche sectie dier <LOCATION>Vereeniging</LOCATION> is Lord \u2022 Rothschild ; de voorzitter van de Duitsche sectie is prof. <PERSON>Einstein</PERSON>.  Lord Rothschild presideerde het diner; aan zijn rechterhand zat de beroemdste geleerde van onzen tyd, aan zijn linkerhand de beroemdste dichter, <PERSON>Bernard Shaw</PERSON>. <PERSON>Rechts van Einstein</PERSON> zat <PERSON>Wells</PERSON>.  Het was een gastmaal voor het intellect en z|jn dames.  Ik wil er geen verslag van geven, maar my bepalen tot enkele aanteekeningen.'}


    >>> res = stanford_ner_wrapper("Prof. Albert Einstein vertoeft op het oogenblik te Londen, en gisteravond was hij in Savoy Hotel eeregast aan een diner, gegeven door de Ort and Oze Societies. De voorzitter van de Engelsche sectie dier Vereeniging is Lord • Rothschild ; de voorzitter van de Duitsche sectie is prof. Einstein.  Lord Rothschild presideerde het diner; aan zijn rechterhand zat de beroemdste geleerde van onzen tyd, aan zijn linkerhand de beroemdste dichter, Bernard Shaw. Rechts van Einstein zat Wells.  Het was een gastmaal voor het intellect en z|jn dames.  Ik wil er geen verslag van geven, maar my bepalen tot enkele aanteekeningen.", 9992)
    >>> from pprint import pprint;pprint(res)
    {'ners': [{'string': 'Albert Einstein', 'tag': 'per'},
              {'string': 'Londen', 'tag': 'loc'},
              {'string': 'Savoy Hotel', 'tag': 'loc'},
              {'string': 'Ort and Oze Societies', 'tag': 'misc'},
              {'string': 'Engelsche', 'tag': 'misc'},
              {'string': 'Vereeniging', 'tag': 'loc'},
              {'string': u'Lord \u2022 Rothschild', 'tag': 'per'},
              {'string': 'Duitsche', 'tag': 'misc'},
              {'string': 'Einstein', 'tag': 'loc'},
              {'string': 'Lord Rothschild', 'tag': 'per'},
              {'string': 'Bernard Shaw', 'tag': 'per'},
              {'string': 'Einstein', 'tag': 'loc'},
              {'string': 'Wells', 'tag': 'per'}],
     'raw_ners': [{'string': 'Albert', 'tag': 'b-per'},
                  {'string': 'Einstein', 'tag': 'i-per'},
                  {'string': 'Londen', 'tag': 'b-loc'},
                  {'string': 'Savoy', 'tag': 'b-loc'},
                  {'string': 'Hotel', 'tag': 'i-loc'},
                  {'string': 'Ort', 'tag': 'b-misc'},
                  {'string': 'and Oze Societies', 'tag': 'i-misc'},
                  {'string': 'Engelsche', 'tag': 'b-misc'},
                  {'string': 'Vereeniging', 'tag': 'b-loc'},
                  {'string': 'Lord', 'tag': 'b-per'},
                  {'string': u'\u2022 Rothschild', 'tag': 'i-per'},
                  {'string': 'Duitsche', 'tag': 'b-misc'},
                  {'string': 'Einstein', 'tag': 'b-loc'},
                  {'string': 'Lord', 'tag': 'b-per'},
                  {'string': 'Rothschild', 'tag': 'i-per'},
                  {'string': 'Bernard', 'tag': 'b-per'},
                  {'string': 'Shaw', 'tag': 'i-per'},
                  {'string': 'Einstein', 'tag': 'b-loc'},
                  {'string': 'Wells', 'tag': 'b-per'}],
     'raw_response': u'Prof. <B-PER>Albert</B-PER> <I-PER>Einstein</I-PER> vertoeft op het oogenblik te <B-LOC>Londen</B-LOC>, en gisteravond was hij in <B-LOC>Savoy</B-LOC> <I-LOC>Hotel</I-LOC> eeregast aan een diner, gegeven door de <B-MISC>Ort</B-MISC> <I-MISC>and Oze Societies</I-MISC>. De voorzitter van de <B-MISC>Engelsche</B-MISC> sectie dier <B-LOC>Vereeniging</B-LOC> is <B-PER>Lord</B-PER> <I-PER>\u2022 Rothschild</I-PER> ; de voorzitter van de <B-MISC>Duitsche</B-MISC> sectie is prof. <B-LOC>Einstein</B-LOC>.  <B-PER>Lord</B-PER> <I-PER>Rothschild</I-PER> presideerde het diner; aan zijn rechterhand zat de beroemdste geleerde van onzen tyd, aan zijn linkerhand de beroemdste dichter, <B-PER>Bernard</B-PER> <I-PER>Shaw</I-PER>. Rechts van <B-LOC>Einstein</B-LOC> zat <B-PER>Wells</B-PER>.  Het was een gastmaal voor het intellect en z|jn dames.  Ik wil er geen verslag van geven, maar my bepalen tot enkele aanteekeningen.'}
    """
    for s in ("\f", "\n", "\r", "\t", "\v"):  # strip whitespaces
        text = text.replace(s, '')
    text += "\n"  # ensure end-of-line

    with _tcpip4_socket(host, port) as s:
        if not isinstance(text, bytes):
            text = text.encode('utf-8')
        s.sendall(text)

        tagged_text = s.recv(10*len(text))

    result = tagged_text.decode("utf-8")

    ner = {"raw_response": result,
           "raw_ners": [],
           "ners": []}

    result = "<xml>%s</xml>" % result
    res = lxml.html.fromstring(result)

    for item in res.iter():
        if item.tag == 'xml':
            continue
        ner["raw_ners"].append({"string": item.text,
                                "tag": item.tag})

    counter = 0
    ners = []
    for item in ner["raw_ners"]:
        if item.get("tag")[0] == 'i':
            if counter and len(ners) >= counter - 1:
                ners[counter - 1]["string"] += ' ' + item.get("string")
        else:
            tag = item.get("tag")
            if "-" in tag:
                tag = tag.split('-')[1]
            ners.append({"string": item.get("string"),
                         "tag": tag})
            counter += 1
    ner["ners"] = ners
    return ner


if __name__ == '__main__':
    import doctest
    doctest.testmod()

    if len(sys.argv) >= 2 and 'profile' in " ".join(sys.argv):
        from gutenberg.acquire import load_etext
        from gutenberg.cleanup import strip_headers
        from pycallgraph import PyCallGraph
        from pycallgraph.output import GraphvizOutput

        text = smart_text(strip_headers(load_etext(17685)).strip())
        with PyCallGraph(output=GraphvizOutput()):
            stanford_ner_wrapper(text, 9992)
