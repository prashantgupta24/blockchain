MY_ENV := myenv

all: install-dev

install-dev: check-python install-python activate-venv

check-python:
	which python3

install-python:
	brew install python

install-venv:
	python3 -m pip install virtualenv

activate-venv:
	virtualenv -p `which python3` $(MY_ENV)
	$(shell source $(MY_ENV)/bin/activate)
	pip install requests

activate:
	ls
	python --version

act1:
	. $(MY_ENV)/bin/activate
	python --version
clean:
	$(deactivate)
	rm -rf $(MY_ENV)
