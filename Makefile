CURRDIR=$(shell pwd)
DESTBINDIR=/usr/local/bin
DESTMANDIR=/usr/local/man
NAME=dotfm

all: none

none:
	@echo 'nothing to do, just run "make install", or "make uninstall"'

install:
	install -pDm755 ${CURRDIR}/src/${NAME}.py ${DESTBINDIR}/${NAME}
	mkdir ${DESTMANDIR}/man1
	install ${CURRDIR}/src/${NAME}.1 ${DESTMANDIR}/man1/${NAME}.1
	ln -si ${DESTMANDIR}/man1/${NAME}.1 /usr/share/man/man1/${NAME}.1

link:
	ln -si ${CURRDIR}/src/${NAME}.py ${DESTBINDIR}/${NAME}
	@echo 'WARNING! moving ${CURRDIR}/src/dotfm.py will break this link'
	mkdir ${DESKMANDIR}/man1
	install ${CURRDIR}/src/${NAME}.1 ${DESTMANDIR}/man1/${NAME}.1
	ln -si ${DESTMANDIR}/man1/${NAME}.1 /usr/share/man/man1/${NAME}.1

uninstall:
	rm -i ${DESTBINDIR}/${NAME}
	rm ${DESTMANDIR}/man1/${NAME}.1 /usr/share/man/man1/${NAME}.1

.PHONY: all none install link uninstall
