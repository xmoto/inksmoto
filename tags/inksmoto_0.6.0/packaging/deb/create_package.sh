#!/bin/sh
INSTALL_DIR="/usr/share/inkscape/extensions"
VERSION=`grep "Version" control-install | cut -d ' ' -f 2`

mkdir -p inksmoto/DEBIAN
cp control-install inksmoto/DEBIAN/control

mkdir -p "inksmoto"$INSTALL_DIR
cp -rf ../../extensions/* "inksmoto"$INSTALL_DIR

# remove emacs backup, svn and pyc files
find "inksmoto" -name '*~' -exec rm -f {} \;
find "inksmoto" -name '*.pyc' -exec rm -f {} \;

dpkg-deb --build inksmoto inksmoto-$VERSION.deb
rm -rf inksmoto
