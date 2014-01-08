#!/bin/sh

#
# local directory - the one this script lives in
#
SOURCE=`dirname "$0"`

#
# name of this script - to exclude it from mirroring
#
MYSELF=`basename "$0"`

#
# mirror local directory to /var/www on the test server
#
rsync -rlptv -e 'ssh' \
    --exclude="$MYSELF" \
    "$SOURCE/var/www" \
    root@neurospin-cubicweb.intra.cea.fr:/var/www
rsync -rlptv -e 'ssh' \
    --exclude="$MYSELF" \
    "$SOURCE/home/imagen" \
    imagen@neurospin-cubicweb.intra.cea.fr:/home/imagen