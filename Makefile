file_finder = find . -type f $(1) -not -path './venv/*'

NAME:=papercheck
ZIP_FILES = $(call file_finder,-name "*.py" -o -name "*.dic")
PY_FILES = $(call file_finder,-name "*.py")

default:
	cd ./src && $(ZIP_FILES) | zip -r ../${NAME}.zip -@
	echo '#!/usr/bin/env python3' | cat - ${NAME}.zip > ${NAME}
	rm ${NAME}.zip
	chmod +x ${NAME}

clean:
	rm ${NAME}

format:
	$(PY_FILES) | xargs black

check_format:
	$(PY_FILES) | xargs black --diff --check
