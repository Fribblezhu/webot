# coding: utf-8
import functools
import time
import logging

def retry(times, interval=0):
    def _retry(f):
        @functools.wraps(f)
        def wrapper(*args, **kwds):
            for i in range(times):
                try:
                    return f(*args, **kwds)
                except Exception:
                    sleep = interval if interval else i + 1
                    if i + 1 < times:
                        logging.warning('Retry: %s Sleep: %ss' %
                                        (i + 1, sleep))
                    time.sleep(sleep)
            else:
                import traceback
                logging.error('%s' % traceback.format_exc())

        return wrapper

    return _retry