#!/usr/bin/python

from update.history import init_processing
from update.history import stop_processing

import logging


if __name__ == "__main__":
    logging.basicConfig()

    # run a quick test
    example = '/etc/passwd'

    # 1st pass
    ret = init_processing(example)
    if ret:
        print 'Start importing "' + example + '"'
        ret = stop_processing(example)
        if ret:
            print 'Done importing "' + example + '"'
        else:
            print 'Error while importing "' + example + '"'
    else:
        print 'Already imported "' + example + '"'

    # 2nd pass
    ret = init_processing(example)
    if ret:
        print 'Start importing "' + example + '"'
        ret = stop_processing(example)
        if ret:
            print 'Done importing "' + example + '"'
        else:
            print 'Error while importing "' + example + '"'
    else:
        print 'Already imported "' + example + '"'
