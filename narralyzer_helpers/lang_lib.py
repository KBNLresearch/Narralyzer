#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

import sys
import importlib
import string

from langdetect import detect
from numpy import mean
from Queue import Queue
from segtok.segmenter import split_multi
from stanford_ner_wrapper import stanford_ner_wrapper
from threading import Thread

# TODO Move this to a seperate config module.
STANFORD_NER_SERVERS = {'de': 9990,
                        'en': 9991,
                        'nl': 9992,
                        'sp': 9993}


class Language:
    '''
    The ``Narralyzer.lang_lib`` module,
    part of the Narralyzer project,

    Licence info: licence.txt

    About
    -----
    The module combines the power of several awesome Python/Java projects,
    see overview of most relevant projects below.

    Using ``lang_lib.Language``
    ------------------
    >>> lang = Language(("Willem Jan Faber just invoked lang_lib.Language, while wishing he was in West Virginia."))
    Using detected language 'en' to parse input text.
    >>> lang.parse()

    URL + Project / Function within Narralyzer:

    http://stanfordnlp.github.io/CoreNLP/
    Stanford CoreNLP / Find named entities.
                       Provide (NER) language models.

    http://www.cnts.ua.ac.be/conll2002/ner/data/
    Conference on Computational Natural Language Learning (CoNLL-2002) /
                        Provide Dutch language model.

    http://www.clips.ua.ac.be/pattern
    CLiPS Pattern / Sentiment analysis.
                    Part-of-speech tagging.

    http://fnl.es/segtok-a-segmentation-and-tokenization-library.html
    Segtok / Sentencte segmentation.

    Source code: https://github.com/KBNLresearch/Narralyzer
    '''
    sentences = {}
    stanford_port = 9990

    use_threads = True
    nr_of_threads = 10

    use_stats = True

    def __init__(self, text=False, lang=False, use_langdetect=True):
        if not text:
            msg = "Did not get any text to look at."
            print(msg)
            sys.exit(-1)

        if len(text) < 9:
            msg = ("Input text is way to small " +
                   "to say someting credible about it.")
            print(msg)
            sys.exit(-1)

        detected_lang = False
        if use_langdetect and not lang:
            try:
                detected_lang = detect(text)

                if detected_lang not in STANFORD_NER_SERVERS:
                    msg = ("Detected language (%s) is not (yet) ",
                           "supported.\n" % detected_lang)
                    print(msg)

                msg = ("Using detected language '%s'" +
                       "to parse input text." % detected_lang)

                print(msg)
                lang = detected_lang
            except:
                msg = "Could not automaticly detect language."
        elif use_langdetect and lang:
            msg = "Skipping language detection, \
                   user specified %s as language" % lang
            print(msg)

        if not lang or lang not in STANFORD_NER_SERVERS:
            msg = "Did not find suitable language to parse text in."
            print(msg)
            sys.exit(-1)

        self.stanford_port = STANFORD_NER_SERVERS.get(lang)

        pattern = False
        try:
            pattern = importlib.import_module('pattern.' + lang)
        except:
            msg = ("Requested language is not (yet) supported" +
                   ", failed to import pattern.%s" % lang)
            print(msg)
            sys.exit(-1)

        self._pattern_parse = pattern.parse
        self._pattern_sentiment = pattern.sentiment
        self._pattern_tag = pattern.tag

        self.result = {"text": text,
                       "lang": lang,
                       "sentences": {},
                       "stats": {}}

    def parse(self):
        for count, sentence in enumerate(split_multi(self.result["text"])):
            self.result["sentences"][count] = {"string": sentence,
                                               "pos": [],
                                               "sentiment": [],
                                               "stanford": [],
                                               "count": count}

        if self.use_threads:
            self._threaded_parser()
        else:
            self._parser()

        if self.use_stats:
            self.stats_all()

    def _parser(self):
        for count, sentence in enumerate(self.result["sentences"].values()):
            sentence = sentence.get("string")
            result = self._parse_singleton(sentence, count)
            for item in result:
                self.result["sentences"][count][item] = result[item]

    def _threaded_parser(self):
        work_queue = Queue()
        result_queue = Queue()

        for count, sentence in enumerate(self.result["sentences"].values()):
            work_queue.put({"string": sentence.get("string"),
                            "count": sentence.get("count")})

        nr_of_threads = self.nr_of_threads
        if len(self.result["sentences"]) <= self.nr_of_threads:
            nr_of_threads = len(self.result["sentences"])

        threads = []
        for worker in range(nr_of_threads):
            process = Thread(target=self._parse_queue,
                             args=(work_queue, result_queue))
            process.daemon = True
            process.start()
            threads.append(process)

        for thread in threads:
            thread.join()

        try:
            result = result_queue.get_nowait()
        except:
            msg = "Thread did not recieve input from queue, bye!"
            print(msg)
            result = False

        while result:
            count = result.get('count')
            for item in result:
                if item == 'count':
                    continue
                self.result["sentences"][count][item] = result.get(item)
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
                                               job.get('count'))
                done_queue.put(result)
            except:
                done = True

    def _parse_singleton(self, sentence, count):
        result = {"count": count,
                  "pos": False,
                  "sentiment": False,
                  "stanford": False,
                  "stats": False}

        if len(sentence) < 2:
            return result

        result["sentiment"] = self._pattern_sentiment(sentence)
        result["stanford"] = stanford_ner_wrapper(sentence, self.stanford_port)

        pos = []
        for word, pos_tag in self._pattern_tag(sentence):
            pos.append({"string": word, "tag": pos_tag})

        result["pos"] = pos

        return result

    def stats_pos(self):
        pass

    def stats_ner(self):
        pass

    @staticmethod
    def stats_sentence(sentence):
        ascii_letters = count = digits = lowercase = \
         printable = uppercase = unprintable = 0

        for count, char in enumerate(sentence):
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

        stats = {"ascii_lowercase": ascii_letters,
                 "count": count + 1,  # a='123'; for i in enumerate(a): print(i)
                 "digits": digits,
                 "lowercase": lowercase,
                 "printable": printable,
                 "uppercase": uppercase,
                 "unprintable": unprintable}

        return stats

    def stats_all(self):
        max_len = min_len = 0  # Min and max sentence length.
        avg = []  # Caluclate average sentence length.
        for sentence in self.result["sentences"].values():
            # Caluclate the stats per sentence.
            sentence_stats = self.stats_sentence(sentence.get("string"))
            avg.append(sentence_stats.get("count"))

            if sentence_stats.get("count") > max_len:
                max_len = sentence_stats.get("count")

            if sentence_stats.get("count") < min_len:
                min_len = sentence_stats.get("count")

            if min_len == 0:
                min_len = sentence_stats.get("count")

            self.result["sentences"][sentence.get("count")]["stats"] = sentence_stats

        # Caluclate the total stats.
        avg_sentence_length = int(round(mean(avg)))

        stats = {}
        stats["avg_length"] = avg_sentence_length
        stats["max"] = max_len
        stats["min"] = min_len

        self.result["stats"] = stats


def _test_NL():
    '''
    >>> lang = Language("Later gaf Christophorus Columbus in een brief aan Ferdinand en Isabella de opdracht de buit te verstoppen en de haven af te branden. Toen Columbus uit de haven van Tunis voer zag hij de soldaten van Isabella naderen.")
    Using detected language 'nl' to parse input text.
    >>> lang.use_threads = False
    >>> lang.parse()
    >>> from pprint import pprint
    >>> pprint (lang.result)
    '''
    lang = Language("Later gaf Christophorus Columbus in een brief aan Ferdinand en Isabella de opdracht de buit te verstoppen en de haven af te branden. Toen Columbus uit de haven van Tunis voer zag hij de soldaten van Isabella naderen.", "nl")
    lang.use_threads = False
    lang.parse()
    from pprint import pprint
    pprint(lang.result)

if __name__ == '__main__':
    # import doctest
    # doctest.testmod()

    _test_NL()
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
