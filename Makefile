test:
	pytest --tb=short

watch-test:
	ls *.py | entr pytest --tb=short

black:
	black -l 86 $$(find * -name '*.py')