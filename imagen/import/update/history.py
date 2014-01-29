"""Helper functions to keep track of processed files."""
import logging
logger = logging.getLogger(__name__)

HISTORY_FILE = '/tmp/history.shelf'
import shelve
__shelf = shelve.open(HISTORY_FILE)


import os.path
import datetime


def init_processing(*args):
    """Start processing a set of files

    If any of the files has changed or has not been processed yet,
    the whole set of files will be processed again from scratch.

    Returns True if the set of files needs to be processed.

    """
    global __shelf
    result = False
    for path in args:
        mtime = os.path.getmtime(path)
        mtime = datetime.datetime.fromtimestamp(mtime)
        if path in __shelf:
            if __shelf[path]['mtime'] != mtime:
                tmp = __shelf[path]
                tmp['mtime'] = mtime
                __shelf[path] = tmp
                result = True
            elif not __shelf[path]['imported']:
                result = True
        else:
            __shelf[path] = { 'mtime': mtime }
            result = True
    if result:
        for path in args:
            tmp = __shelf[path]
            tmp['imported'] = False
            __shelf[path] = tmp
        __shelf.sync()
    return result


def stop_processing(*args):
    """Notify a set of files has been processed

    Returns False if processing of any of the files has not started yet
    or is already finished.

    """
    global __shelf
    result = True
    for path in args:
        if path in __shelf:
            if __shelf[path]['imported']:
                result = False
            else:
                tmp = __shelf[path]
                tmp['imported'] = True
                __shelf[path] = tmp
        else:
            result = False
    if result:
        __shelf.sync()
    return result


def __cleanup():
    """A Shelf has to be explictly closed. From the documentation::
    > Like file objects, shelve objects should be closed explicitly
    > to ensure that the persistent data is flushed to disk.

    Failure to close the Shelf results in error messages at exit upon
    module cleanup:
        Exception TypeError: "'NoneType' object is not callable" in  ignored

    """
    global __shelf
    __shelf.close()

import atexit
atexit.register(__cleanup)
