# coding: utf-8
import os
import logging


def init_logging(name='', dir_name='logs'):
    import coloredlogs
    # root logger
    logger = logging.getLogger(name)
    coloredlogs.install(level='DEBUG', logger=logger)

    if dir_name and not os.path.exists(dir_name):
        os.makedirs(dir_name)

    filename = name if name else 'WeChat'
    fn = os.path.join(dir_name, '%s.log' % filename)

    file_handler = logging.FileHandler(fn)
    formatter = logging.Formatter(
        '%(asctime)s %(name)s[%(process)d] %(levelname)s %(message)s')
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.DEBUG)
    logger.addHandler(file_handler)

    return logger
