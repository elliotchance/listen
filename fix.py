import yaml
import re
import os
from typing import List, Set, Dict

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
for name in sorted(os.listdir("Broadcasts")):
  if not name.endswith('.md'):
     continue

  path = "Broadcasts/%s" % (name)

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
          artist = artist_repo.get_artist(m.group(1))
          if artist is None:
            print('missing artist: ' + m.group(1))
            return '[%s](#)' % m.group(1)
          elif artist.rym is None:
            return '[%s](#)' % m.group(1)
          else:
            return '[%s](%s)' % (m.group(1), artist.rym)
        def track_line(m):
          return '- ' + re.sub(r"\[(.*?)\]\((.*?)\)", lookup_artist,  m.group(1), re.MULTILINE)
        content = mixes[h2]['mixes'][h3]['content']
        content = re.sub(r"^- (.*)$", track_line, content, 0, re.MULTILINE)
        f.write('### ' + h3 + '\n' + content)

  toc = ''
  total_duration = 0
  total_mixes = 0
  for h2 in sorted(mixes):
    for mix in mixes[h2]['mixes']:
      total_duration += mixes[h2]['mixes'][mix]['duration']
      final_duration += mixes[h2]['mixes'][mix]['duration']
    total_mixes += len(mixes[h2]['mixes'])
    final_mixes += len(mixes[h2]['mixes'])

  toc = '**%d mixes, %s**' % (total_mixes, format_duration(total_duration)) + '\n\n'

  def tohref(s):
     return s.lower().replace(' ', '-')
  
  for h2 in sorted(mixes):
     for mix in mixes[h2]['mixes']:
        all_mixes[mix] = mixes[h2]['mixes'][mix]

  for h2 in sorted(mixes):
    duration = 0
    for mix in mixes[h2]['mixes']:
      duration += mixes[h2]['mixes'][mix]['duration']
    toc += '- [%s](#%s) (%d mixes, %s)' % (h2, tohref(h2), len(mixes[h2]['mixes']), format_duration(duration)) + '\n'

  with open(path) as fd:
    content = fd.read()
  
  content = re.sub(r"<!-- toc:start -->(.*?)<!-- toc:end -->",
                   "<!-- toc:start -->\n" + toc + "<!-- toc:end -->", content, 0, re.DOTALL)
  with open(path, "w") as f:
    f.write(content)

with open('All.md', "w") as f:
  f.write('**%d mixes, %s**\n\n' % (final_mixes, format_duration(final_duration)))
  for title in sorted(all_mixes):
    mix = all_mixes[title]
    f.write('1. %s %s\n' % (mix['emoji'], title))
