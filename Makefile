all: sdist bdist_wheel

sdist:
	python setup.py sdist

bdist_wheel:
	python setup.py bdist_wheel

upload_build:
	@read -p "Enter user token\n" token; \
	echo $$token; \
	python -m twine upload --repository pypi dist/* -u __token__ -p $$token --verbose

.PHONY : sdist bdist_wheel