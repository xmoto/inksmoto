#!/bin/sh
INSTALL_DIR="/usr/share/inkscape/extensions"
VERSION=`grep "Version" control-install | cut -d ' ' -f 2`

mkdir -p inksmoto/DEBIAN
cp control-install inksmoto/DEBIAN/control

mkdir -p "inksmoto"$INSTALL_DIR
cp -rf ../extensions/* "inksmoto"$INSTALL_DIR
# this are two inkscape files.
rm -f "inksmoto""$INSTALL_DIR""/inkex.py"
rm -f "inksmoto""$INSTALL_DIR""/bezmisc.py"
rm -f "inksmoto""$INSTALL_DIR""/*~"
rm -f "inksmoto""$INSTALL_DIR""/*.pyc"
cp ~/.inkscape/extensions/listAvailableElements.xml "inksmoto""$INSTALL_DIR"
cp ~/.inkscape/extensions/listAvailableElements.py "inksmoto""$INSTALL_DIR"

dpkg-deb --build inksmoto inksmoto-$VERSION.deb
rm -rf inksmoto
