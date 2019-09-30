

NAME:=papercheck


all:
	cd ./src; zip -r ../${NAME}.zip *.py lib/*.py checker/*.py pos/*.py dictionary/*.dic
	echo '#!/usr/bin/env python3' | cat - ${NAME}.zip > ${NAME}
	rm ${NAME}.zip
	chmod +x ${NAME}

clean:
	rm ${NAME}
