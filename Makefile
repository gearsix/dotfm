CURRDIR=$(shell pwd)
DESTDIR=/usr/local/bin
NAME=dotfm

all: none

none:
	@echo 'nothing to do, just run "make install", or "make uninstall"'

install:
	install -pDm755 ${CURRDIR}/src/${NAME}.py ${DESTDIR}/${NAME}

link:
	ln -s ${CURRDIR}/src/${NAME}.py ${DESTDIR}/${NAME}
	@echo 'WARNING! moving ${CURRDIR}/src/dotfm.py will break this link'

uninstall:
	rm -f ${DESTDIR}/${NAME}

.PHONY: all none install link uninstall
