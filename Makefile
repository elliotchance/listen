all:
	python3.9 fix.py

test:
	python3.9 generate_test.py

diff:
	git diff tracks.csv

stat:
	git diff -U0 README.md

commit:
	git add .
	git commit -m "changes"
	git push
