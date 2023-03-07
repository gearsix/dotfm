#!/usr/bin/env sh

set -e

NAME="dotfm"
CURRDIR=$(pwd)
DESTBIN=/usr/local/bin
DESTMAN=/usr/local/share/man/man1

mkdir -p $DESTBIN $DESTMAN

if [ "$1" = "-h" ]; then
	echo "usage: ./install.sh [-h|-l|-u]"
	echo ""
	echo "options:"
	echo "  -h    print this message"
	echo "  -l    link the install files from source (not copy)"
	echo "  -u    uninstall all install files"
	echo ""
elif [ "$1" = "-l" ]; then
	ln -iv "$CURRDIR/src/$NAME.py" "$DESTBIN/$NAME"
	ln -iv "$CURRDIR/src/$NAME.1" "$DESTMAN"
elif [ "$1" = "-u" ]; then
	rm -i "$DESTBIN/$NAME"
	rm -i "$DESTMAN/$NAME.1"
else
	cp -v "$CURRDIR/src/$NAME.py" "$DESTBIN/$NAME"
	chmod +x "$DESTBIN/$NAME"
	chown root:wheel "$DESTBIN/$NAME"
	cp -v "$CURRDIR/src/$NAME.1" "$DESTMAN"
fi

