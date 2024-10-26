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

artist_repo = ArtistRepo()

for name in os.listdir("Broadcasts"):
  if not name.endswith('.md'):
     continue

  path = "Broadcasts/%s" % (name)
  print(path)

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
