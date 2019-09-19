

NAME:=papercheck
BIN_DIR := bin

all:
	@mkdir -p ${BIN_DIR}
	cd ./src; zip -r ../${NAME}.zip *.py lib/*.py checker/*.py pos/*.py
	echo '#!/usr/bin/env python3' | cat - ${NAME}.zip > ${BIN_DIR}/${NAME}
	chmod +x ${BIN_DIR}/${NAME}

clean:
	rm ${NAME}.zip
	rm ${BIN_DIR}/${NAME}
