#!/bin/sh

path=`dirname "$0"`
file=`basename "$0" .sh`

cubicweb-ctl shell imagen "$path/$file.py"
