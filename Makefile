file_finder = find $(1) -type f $(2) -not -path './venv/*'

NAME:=paperchecker
ZIP_FILES = $(call file_finder,papercheck,-name "*.py" -o -name "*.dic")
PY_FILES = $(call file_finder,.,-name "*.py")

default:
	$(ZIP_FILES) | zip -r $(NAME).zip -@
	cd papercheck && zip -u ../$(NAME).zip __main__.py
	echo '#!/usr/bin/env python3' | cat - $(NAME).zip > $(NAME)
	rm $(NAME).zip
	chmod +x $(NAME)

clean:
	rm $(NAME)

format:
	$(PY_FILES) | xargs black

check: check_format

check_format:
	$(PY_FILES) | xargs black --diff --check

unit_test:
	python3 testrunner.py

test: default unit_test
	./$(NAME) -sgy example/testfile.pdf
	./$(NAME) -sgy example/testfile.pdf
	python3 $(NAME).py -sgy example/testfile.tex
	python3 $(NAME).py -sgy example/testfile.tex

setup:
	sudo apt install -y poppler-utils
	pip3 install -r requirements.txt

install: default
	sudo cp -u $(NAME) /usr/local/bin