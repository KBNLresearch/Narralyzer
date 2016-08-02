#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-
"""
    narralyzer.utils
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    Misc utilities to support Narralyzer.

    :copyright: (c) 2016 Koninklijke Bibliotheek, by Willem-Jan Faber.
    :license: GPLv3, see licence.txt for more details.
"""

import sys
reload(sys)
sys.setdefaultencoding('utf-8')

import codecs
import cPickle
import gzip
import json
import os
import time

from lang_lib import Language


current_path = os.path.realpath(__file__)

# Path to test data
TEST_DATA = current_path + '../test_data/'

# Path to put output files (parsed / zipped books)
OUTPUT = current_path + '../out/'


def load_test_book(fname, force=True, return_json=False, verbose=True):
    '''
        >>> book = load_test_book('dutch_book_gbid_20060.txt', verbose=False)
        >>> from pprint import pprint
        >>> pprint(book.get('stats'))
        {'avg_length': 97, 'max': 827, 'min': 1}
    '''
    fname = os.path.basename(fname)
    ofname = os.path.join(OUTPUT, fname.replace('.txt', 'pickle.gz'))
    fname = os.path.join(TEST_DATA, fname)

    if not os.path.isfile(ofname) and not force:
        # Open and read the test-book.
        fh = codecs.open(fname, 'r', encoding='utf-8')
        book = fh.read().replace('\n', ' ')
        fh.close()

        # Tag each sentence.
        t = time.time()
        lang = Language(book)
        lang.parse()
        if verbose:
            print("Took %s to parse %s bytes" % (str(round(time.time() - t)),
                                                 str(len(book))))

        # Store the result to a compressed pickle file.
        fh = gzip.GzipFile(ofname, 'wb')
        fh.write(cPickle.dumps(lang.result))
        fh.close()
        result = lang.result
    else:
        # Load the tagged sentences from a compressed pickle file.
        fh = gzip.GzipFile(ofname, 'rb')
        raw_data = ""
        data = fh.read()

        while data:
            raw_data += data
            data = fh.read()

        langlib_result = cPickle.loads(raw_data)
        fh.close()
        result = langlib_result

    if return_json:
        return json.dumps(result)
    return result

if __name__ == "__main__":
    if len(sys.argv) >= 2 and 'test' in " ".join(sys.argv):
        import doctest
        doctest.testmod(verbose=True)

    from pprint import pprint
    book = load_test_book('dutch_book_gbid_20060.txt')
    pprint(book.get('stats'))
