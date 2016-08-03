#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-
'''
    narralyzer.config
    ~~~~~~~~~~~~~~~~~

    Handle misc config variables.

    :copyright: (c) 2016 Koninklijke Bibliotheek, by Willem-Jan Faber.
    :license: GPLv3, see licence.txt for more details.
'''

import sys
reload(sys)
sys.setdefaultencoding('utf-8')

from sys import argv, exit
from os import path, environ, getenv
from ConfigParser import ConfigParser

try:
    from narralyzer.util import logger as logger
except:
    from utils import logger

class Config():
    """
    Configuration file dict.
    """
    config = {
        'config_file': 'conf/config.ini',
        'models': {},
        'root': None,
        'supported_languages': []
    }


    def __init__(self):
        if self.config.get('root', None) is None:
            root = path.join(path.dirname(path.abspath(__file__)))
            root = path.join(root, '..')
            self.config['root'] = path.abspath(root)

        root = self.config['root']
        logger("My basepath={0}".format(root))
        config_file = path.join(root, self.config.get('config_file'))

        if not path.isfile(config_file):
            print("Could not open config file: {0}".format(path.abspath(config_file)))
            exit(-1)

        self.config['config_file'] = config_file
        config = ConfigParser()
        config.read(config_file)

        for section in config.sections():
            if section.startswith('lang_'):
                language = section.replace('lang_', '')
                port = config.get(section, 'port')
                stanford_ner = config.get(section, 'stanford_ner')
                self.config['models'][language] = {
                        'port': port,
                        'stanford_ner': stanford_ner}
            if section == 'main':
                stanford_ner_path = config.get(section, 'stanford_ner_path')

        for language in self.config.get('models'):
            self.config["supported_languages"].append(language)

    def get(self, variable):
        result = self.config.get(variable, None)
        if isinstance(result, list):
            return " ".join(result).upper()
        return result

    def __repr__(self):
        result = "Using config file:\n\t{0}\nAvailable config parameters:\n\t{1}\n\t{2}".format(
                self.config.get('config_file'),
                "supported_languages",
                "root"
                )
        return result

if __name__ == "__main__":
    config = Config()

    if len(argv) > 1:
        result = config.get(argv[1])
        if result is None:
            msg = "Config key {0} unknown."
            logger(msg)
            exit(-1)
        else:
            print(result)
    else:
        print(config)
