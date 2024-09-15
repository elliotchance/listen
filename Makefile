all:
	python3.9 generate.py

test:
	python3.9 generate_test.py

diff:
	git diff tracks.csv
