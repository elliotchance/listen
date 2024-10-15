#!/usr/bin/env python3

from urllib.request import urlopen
import re
import sys

for url in sys.argv[1:]:
  output = urlopen(url).read().decode('utf-8')

  title = re.search(r"<title>(.*)</title>", output).group(1)
  release_parts = re.search(r"(.*) - (.*?) (\d+) ([\d-]+)", title).groups()

  release = '%s: %s #%s' % (release_parts[3], release_parts[1], release_parts[2])

  print('  - release: "%s"' % release.replace(' Of ', ' of '))
  print('    duration: 2h # approx')
  print('    urls:')
  print('      - %s' % url)
  print('')
