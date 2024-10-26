import re

path = "Broadcasts/%s" % ('A State of Trance.md')

header = ''
mixes = {}
h2 = ''
h3 = ''
with open(path) as fd:
  lines = fd.readlines()
  for line in lines:
    if line.startswith('## '):
      h2 = line[3:].strip()
      h3 = ''
      mixes[h2] = {'mixes': {}, 'content': ''}
    elif line.startswith('### '):
      h3 = line[4:].strip()
      mixes[h2]['mixes'][h3] = {'quote': '', 'liked': [], 'content': ''}
    elif line.startswith('> ') and h2 != '':
      mixes[h2]['mixes'][h3]['quote'] += line
      mixes[h2]['mixes'][h3]['content'] += line
    elif line.startswith('- ') and h2 != '':
      mixes[h2]['mixes'][h3]['liked'].append(line.strip())
      mixes[h2]['mixes'][h3]['content'] += line
    else:
      if h3 != '':
        mixes[h2]['mixes'][h3]['content'] += line
      elif h2 != '':
        mixes[h2]['content'] += line
      else:
        header += line
    
    # print(lines)

    # parts = file.split('\n### ')
    # header = parts[0]
    # for m in parts[1:]:
    #     title = m.split('\n')[0]
    #     match = re.search(r'(.) (\d+)/10', m, re.IGNORECASE)
    #     if match:
    #         emoji = match.group(1)
    #         rating = match.group(2)
    #     match = re.search(r'(\d+h\d+m|\d+h|\d+m)', m, re.IGNORECASE)
    #     if match:
    #         length = match.group(0)

    #     mixes[title] = {
    #         'content': m[len(title)+1:],
    #         'emoji': emoji,
    #         'rating': rating,
    #         'length': length,
    #     }

print(mixes['2005']['mixes']['2005-07-07: A State of Trance #204']) # [])
# with open(path, "w") as f:
#   print(header)
#   # f.write(header + '\n')
#   for title in sorted(mixes):
#     print()
#     f.write('### ' + title + '\n' + mixes[title]['content'] + '\n')

print(header)
for h2 in sorted(mixes):
  print('## ' + h2 + '\n')
  if mixes[h2]['content'].strip() != '':
    print(mixes[h2]['content'].rstrip() + '\n')
  for h3 in sorted(mixes[h2]['mixes']):
    print('### ' + h3 + '\n' + mixes[h2]['mixes'][h3]['content'].rstrip() + '\n')
    # print(mixes[h2]['mixes'][h3]['quote'])
    # for t in mixes[h2]['mixes'][h3]['liked']:
    #   print(t)
