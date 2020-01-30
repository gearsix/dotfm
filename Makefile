DESTDIR=/usr/bin
NAME=dotfm

all: none

none:
	@echo 'nothing to do, just run "make install", or "make uninstall"'

install:
	install -vpDm755 src/${NAME}.py ${DESTDIR}/${NAME}
	

uninstall:
	rm -f ${DESTDIR}/${NAME}

.PHONY: all none install uninstall
