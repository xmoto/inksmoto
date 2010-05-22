#!/bin/sh

if [ $# -ne 1 ]
then
    echo "usage: ./create_package.sh <version>"
    exit 1
fi

VERSION="$1"
TARED_DIR="extensions"
EXCLUDES="--exclude=*~ --exclude=*.pyc --exclude=.svn"
ARCHIVE="inksmoto-""$VERSION"".tar.gz"
(cd ../../ && tar zcvf "$ARCHIVE" "$TARED_DIR" $EXCLUDES ) && mv "../../""$ARCHIVE" . && echo "build complete"
if [ ! -f "$ARCHIVE" ]
then
    echo "ERROR -- Archive not generated"
    exit 1
fi
