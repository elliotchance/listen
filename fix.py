import yaml
import re
import os
from typing import List, Set, Dict

dir = "Broadcasts"


def plural(word, n):
  if word == 'mix':
    if n == 1:
        return '1 mix'
    return '%d mixes' % n
  if n == 1:
      return '1 %s' % word
  return '%d %ss' % (n, word)

class Artist:
    name: str
    rym: str

    def __init__(self, m: Dict[str, str]) -> None:
        self.name = m['name']
        if 'rym' in m:
            self.rym = m['rym']
        else:
            self.rym = None

class ArtistRepo:
    artists: List[Artist]

    def __init__(self) -> None:
        with open("artists.yaml") as artists_file:
            artist_details = yaml.safe_load(artists_file)
            self.artists = [Artist(a) for a in artist_details['artists']]

    def get_artist(self, name):
        for artist in self.artists:
            if artist.name == name:
                return artist

        return None

def format_duration(d):
  h = int(d / 60)
  m = d - (h * 60)
  if h == 0:
      return '%dm' % m
  if m == 0:
      return '%dh' % h
  return '%dh%02dm' % (h, m)

artist_repo = ArtistRepo()

all_mixes = {}
final_duration = 0
final_mixes = 0
primary_toc = {}
for name in sorted(os.listdir(dir)):
  if not name.endswith('.md'):
     continue

  path = "%s/%s" % (dir, name)
  primary_toc[name] = {'mix_count': 0, 'duration': 0}

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
        s = re.search(r"(.) (\d+)/10", line)
        if s is not None:
          mixes[h2]['mixes'][h3]['emoji'] = s.group(1)
          mixes[h2]['mixes'][h3]['rating'] = int(s.group(2))
        if 'duration' not in mixes[h2]['mixes'][h3]:
          mixes[h2]['mixes'][h3]['duration'] = 0
          duration = re.search(r"(\d+)h(\d+)m", line)
          if duration is not None:
            mixes[h2]['mixes'][h3]['duration'] = int(duration.group(1)) * 60 + int(duration.group(2))
          else:
            duration = re.search(r"(\d+)h", line)
            if duration is not None:
              mixes[h2]['mixes'][h3]['duration'] = int(duration.group(1)) * 60
            else:
              duration = re.search(r"(\d+)m", line)
              if duration is not None:
                mixes[h2]['mixes'][h3]['duration'] = int(duration.group(1))
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

  with open(path, "w") as f:
    f.write(header)
    for h2 in sorted(mixes):
      f.write('## ' + h2 + '\n' + mixes[h2]['content'])
      for h3 in sorted(mixes[h2]['mixes']):
        def lookup_artist(m):
          if m.group(1) == '1001tracklists' or m.group(1) == 'MusicBrainz':
            return '[%s](%s)' % (m.group(1), m.group(2))
          artist = artist_repo.get_artist(m.group(1))
          if artist is None:
            print('missing artist: ' + m.group(1))
            return '[%s](#)' % m.group(1)
          elif artist.rym is None:
            return '[%s](#)' % m.group(1)
          else:
            return '[%s](%s)' % (m.group(1), artist.rym)
        content = mixes[h2]['mixes'][h3]['content']
        content = re.sub(r"\[(.*?)\]\((.*?)\)", lookup_artist, content, 0, re.MULTILINE)
        f.write('### ' + h3 + '\n' + content)

  toc = ''
  total_duration = 0
  total_mixes = 0
  for h2 in sorted(mixes):
    for mix in mixes[h2]['mixes']:
      total_duration += mixes[h2]['mixes'][mix]['duration']
      final_duration += mixes[h2]['mixes'][mix]['duration']
      primary_toc[name]['duration'] += mixes[h2]['mixes'][mix]['duration']
    total_mixes += len(mixes[h2]['mixes'])
    final_mixes += len(mixes[h2]['mixes'])
    primary_toc[name]['mix_count'] += len(mixes[h2]['mixes'])

  toc = '**%s, %s**' % (plural('mix', total_mixes), format_duration(total_duration)) + '\n\n'

  def tohref(s):
     return s.lower().replace(' ', '-')
  
  def to_url(s):
     return s.replace(' ', '%20')
  
  for h2 in sorted(mixes):
     for mix in mixes[h2]['mixes']:
        all_mixes[mix] = mixes[h2]['mixes'][mix]

  for h2 in sorted(mixes):
    duration = 0
    for mix in mixes[h2]['mixes']:
      duration += mixes[h2]['mixes'][mix]['duration']
    toc += '- [%s](#%s) (%s, %s)' % (h2, tohref(h2), plural('mix', len(mixes[h2]['mixes'])), format_duration(duration)) + '\n'

  with open(path) as fd:
    content = fd.read()
  
  content = re.sub(r"<!-- toc:start -->(.*?)<!-- toc:end -->",
                   "<!-- toc:start -->\n\n" + toc + "<!-- toc:end -->", content, 0, re.DOTALL)
  with open(path, "w") as f:
    f.write(content)

with open('All.md', "w") as f:
  f.write('**%d mixes, %s**\n\n' % (final_mixes, format_duration(final_duration)))
  for path in sorted(primary_toc):
    f.write('- [%s](%s/%s) (%s, %s)\n' % (path[:-3], dir, to_url(path), plural('mix', primary_toc[path]['mix_count']), format_duration(primary_toc[path]['duration'])))
  f.write('\n---\n\n')
  for title in sorted(all_mixes):
    mix = all_mixes[title]
    emoji = '⬜'
    if 'emoji' in mix:
       emoji = mix['emoji']
    f.write('1. %s `%s` (%s)\n' % (emoji, title, format_duration(mix['duration'])))

with open('README.md', "w") as f:
  f.write('**%d mixes, %s**\n\n' % (final_mixes, format_duration(final_duration)))
  f.write('[All Mixes](All.md)\n\n')
  for path in sorted(primary_toc):
    f.write('- [%s](%s/%s) (%s, %s)\n' % (path[:-3], dir, to_url(path), plural('mix', primary_toc[path]['mix_count']), format_duration(primary_toc[path]['duration'])))
