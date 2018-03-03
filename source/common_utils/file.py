# coding: utf-8
import os
import codecs
import logging


def save_file(dir_name, filename, data):
    if dir_name and not os.path.exists(dir_name):
        os.makedirs(dir_name)
    fn = os.path.join(dir_name, filename)
    logging.debug('Saved file: %s' % fn)
    with open(fn, 'wb') as f:

        f.write(data)
    return fn


def write_to_file(file_name, txt):
    with codecs.open(file_name, "w", "utf-8") as f:
        f.write(txt)


def add_to_file(file_name, txt):
    with codecs.open(file_name, "a", "utf-8") as f:
        f.write(txt)