#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

import importlib
import segtok.segmenter
import string
import sys

from django.utils.encoding import smart_text
from langdetect import detect
from numpy import mean
from Queue import Queue
from stanford_ner_wrapper import stanford_ner_wrapper
from threading import Thread

STANFORD_NER_SERVERS = {
    'de': 9990,
    'en': 9991,
    'nl': 9992,
    'sp': 9993,
}

class Language:
    sentences = {}
    stanford_ner = {}
    stanford_port = 9990

    text = u'Later gaf Christophorus Columbus in \
    een brief aan Ferdinand en Isabella. Toen \
    Columbus uit de haven van Tunis voer.'

    result_stats = {"ner": {},
                    "sentences": {},
                    "input_string": {}}

    result = {"input_string": text,
              "sentences": sentences,
              "stats": result_stats}

    use_threads = True
    use_langdetect = True


    def __init__(self, lang=False, text=False):
        if text:
            self.text = text

        if use_langdetect:
            detected_lang = detect(self.text)

            if not str(detected_lang) == str(lang):
                print("Requested language: %s is not the same as detected language: %s." % (lang, detected_lang))
                print("Ignoring language detection result.")
                lang = detected_lang

            if not lang in STANFORD_NER_SERVERS:
                print("Requested language: %s not available.")
                sys.exit(-1)
            else:
                self.stanford_port = STANFORD_NER_SERVERS.get(lang, 'en')

        try:
            pattern = importlib.import_module('pattern.' + lang)
        except:
            print("Nice try, but the requested language is not supported, sorry!")

        self._pattern_parse = pattern.parse
        self._pattern_sentiment = pattern.sentiment
        self._pattern_tag = pattern.tag

    def parse(self):
        for sentence_count, sentence in enumerate(
                segtok.segmenter.split_multi(self.text.replace('\n', ' '))):
            self.sentences[sentence_count] = ({"string": sentence,
                                               "pos": [],
                                               "sentiment": [],
                                               "stanford": [],
                                               "nr": sentence_count})

        if self.use_threads:
            self._threaded_parser()
        else:
            self._parser()

    def _parser(self):
        for sentence_count, sentence in enumerate(self.sentences.values()):
            sentence = sentence.get("string")
            result = self._parse_singleton(sentence, sentence_count)
            if not result:
                continue
            for item in result:
                self.sentences[sentence_count][item] = result[item]

    def _threaded_parser(self):
        work_queue = Queue()
        result_queue = Queue()

        for sentence_count, sentence in enumerate(self.sentences.values()):
            work_queue.put({"string": sentence.get("string"),
                            "nr" : sentence.get("nr")})
        if len(self.sentences) < 10:
            num_workers = len(self.sentences)
        else:
            num_workers = 10

        workers = []
        for worker in range(num_workers):
            p = Thread(target=self._parse_queue,
                       args=(work_queue, result_queue))
            p.daemon = True
            p.start()
            workers.append(p)

        for worker in workers:
            worker.join()

        result = result_queue.get_nowait()
        while result:
            nr = result.get('nr')
            for item in result:
                if item == 'nr':
                    continue
                self.sentences[nr][item] = result.get(item)
            try:
                result = result_queue.get_nowait()
            except:
                result = False

    def _parse_queue(self, work_queue, done_queue):
        done = False
        while not done:
            try:
                job = work_queue.get_nowait()
                result = self._parse_singleton(job.get('string'),
                                               job.get('nr'))
                done_queue.put(result)
            except:
                done = True

    def _parse_singleton(self, sentence, sentence_count):
        if len(sentence) < 2:
            # Skip sentence that are too short.
            return False

        pos = []
        sentiment = self._pattern_sentiment(sentence)
        stanford = stanford_ner_wrapper(sentence, self.stanford_port)

        for word, pos_tag in self._pattern_tag(sentence):
            pos.append({"string": word, "tag": pos_tag})

        retval = {"nr": sentence_count,
                  "pos": pos,
                  "sentiment": sentiment,
                  "stanford": stanford}

        return retval

    def stats(self):
        nr_of_sentences = len(self.sentences)
        self.result_stats["sentences"]["count"] = nr_of_sentences

        avg = []

        ascii_letters = digits = lowercase = \
            printable = uppercase = unprintable = 0

        for sentence in self.sentences.values():
            avg.append(len(sentence.get('string')))
            for char in sentence:
                if char in string.printable:
                    printable += 1
                    if char in string.digits:
                        digits += 1
                    elif char in string.ascii_letters:
                        ascii_letters += 1
                        if char in string.ascii_lowercase:
                            lowercase += 1
                        elif char in string.ascii_uppercase:
                            uppercase += 1
                else:
                   unprintable += 1

        avg_sentence_length = int(round(mean(avg)))
        self.result_stats["sentences"]["total"] = {}
        self.result_stats["sentences"]["total"] = {"ascii_letters": ascii_letters,
                                                   "digits": digits,
                                                   "lowercase": lowercase,
                                                   "printable": printable,
                                                   "uppercase": uppercase,
                                                   "unprintable": unprintable}
        self.result_stats["sentences"]["avg_length"] = avg_sentence_length


def _test_NL():
    '''
    >>> lang = Language()
    >>> lang.parse()
    >>> lang.stats()
    >>> from pprint import pprint; pprint (nl.result)

    '''

if __name__ == '__main__':
    import doctest
    doctest.testmod()


    '''

    if len(sys.argv) >= 2 and 'profile' in sys.argv[1]:
        from pycallgraph import PyCallGraph
        from pycallgraph.output import GraphvizOutput

        from gutenberg.acquire import load_etext
        from gutenberg.cleanup import strip_headers

        text = smart_text(strip_headers(load_etext(17685)).strip())
        with PyCallGraph(output=GraphvizOutput()):
            nl = NL()
            nl.text = text
            nl.parse()
            nl.stats()

    if len(sys.argv) >= 2 and 'time' in sys.argv[1]:
        import time
        import json

        from gutenberg.acquire import load_etext
        from gutenberg.cleanup import strip_headers

        gutenberg_test_id = 17685

        text = smart_text(strip_headers(load_etext(gutenberg_test_id)).strip())


        print("Timing non-threaded lang_lib")
        s = time.time()
        nl = NL()
        nl.text = text
        nl.parse()
        nl.stats()
        print("Took %s seconds" % (str(round(s - time.time()) * -1)))

        print("Timing threaded lang_lib")
        s = time.time()
        nl = NL()
        nl.use_threads = True
        nl.text = text
        nl.parse()
        nl.stats()
        print("Took %s seconds" % (str(round(s - time.time()) * -1)))

        print("Timing ner-vanilla")
        s = time.time()
        stanford_ner_wrapper(text, 9992)
        print("Took %s seconds" % (str(round(s - time.time()) * -1)))

        outfile = "../out/%s.pos_ner_sentiment.json" % gutenberg_test_id
        print("Writing output in json-format to: %s" % outfile)
        with open(outfile, "w") as fh:
            fh.write(json.dumps(nl.result))
    '''
