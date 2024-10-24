import yaml
import os
import re
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

class Track:
    original: str
    canonical: str
    title: str
    artists: Set[str]
    is_time_code: bool
    rating: int
    version: str

    def __init__(self, s: str, rating: int) -> None:
        self.rating = rating
        if s.startswith('<'):
            self.rating = int(''.join(re.findall(r'<(\d+)>', s)))
            s = s.split('> ')[1]

        self.original = s
        self.canonical = re.sub(r'\s*\{(.*?)\}', '', s)
        self.title = ''
        self.artists = set()
        self.is_time_code = False
        self.version = '; '.join(re.findall(r'\{(.*?)\}', s))
        if self.version == '':
            self.version = 'Original Mix'

        if s.startswith('@'):
            self.is_time_code = True
            self.canonical = ''
            return

        if s.startswith('+ '):
            self.rating += 2
            s = s[2:]
            self.canonical = self.canonical[2:]
            self.original = self.original[2:]

        parts = s.split(' - ')
        artists = re.findall(r'\[(.*?)\]', s)

        if len(parts) == 2:        
            self.title = parts[0]
            self.title = re.sub(r'[\[\]]', '', self.title).strip()

            if '[' in parts[1]:
                self.artists = set(artists)
            else:
                self.artists = set([parts[1]])
            return

        print("cannot parse track: "+s)
        return None
    
    def __repr__(self):
        return self.original
    
    def render_title(self, artist_repo: ArtistRepo) -> str:
        parts = self.original.split(' - ')
        return apply_artists(re.sub(r'\s*\{(.*?)\}', '', parts[0]), artist_repo)
    
    def render_artist(self, artist_repo: ArtistRepo) -> str:
        parts = self.original.split(' - ')
        if '[' not in parts[1]:
            parts[1] = '[' + parts[1] + ']'

        return apply_artists(parts[1], artist_repo)
    
    def render_version(self, artist_repo: ArtistRepo) -> str:
        return apply_artists(self.version, artist_repo)
    
    def render_rating(self):
        if self.rating > 8:
            return '❤️'
        
        if self.rating > 6:
            return '👍'
        
        return ''

def apply_artists(s, artist_repo: ArtistRepo) -> str:
    artists = re.findall('\[(.*?)\]', s)
    for artist in artists:
        a = artist_repo.get_artist(artist)
        if a is None:
            print("missing link for artist: " + artist)
        if a is None or a.rym is None:
            s = s.replace("[%s]" % artist, "<u>%s</u>" % artist)
        else:
            s = s.replace("[%s]" % artist, "<a href=\"%s\">%s</a>" % (a.rym, artist))

    return s
class TrackAppearance:
    track: Track
    appears_on: List[str]
    points: int

    def __init__(self, track: Track, appears_on: str = None) -> None:
        self.track = track
        self.appears_on = appears_on
        self.points = 0

class TrackRepo:
    tracks: Dict[str, Dict[str, TrackAppearance]]

    def __init__(self) -> None:
        self.tracks = {}

    def load_broadcast_file(self, path: str, broadcast: str) -> None:
        with open(path) as f:
            file = yaml.safe_load(f)
            if 'episodes' in file:
                for episode in file['episodes']:
                    appears_on = broadcast
                    if 'release' in episode:
                        appears_on = episode['release']
                    else:
                        if 'date' in episode:
                            appears_on = episode['date'].strftime('%Y-%m-%d') + ': ' + appears_on
                        if 'number' in episode:
                            appears_on += ' #' + str(episode['number'])
                        if 'artist' in episode:
                            appears_on += ', "' + episode['artist'] + '"'
                    if 'liked' in episode:
                        for title in episode['liked']:
                            t = Track(title, 7)
                            if t.canonical not in self.tracks:
                                self.tracks[t.canonical] = {}

                            if t.version not in self.tracks[t.canonical]:
                                self.tracks[t.canonical][t.version] = TrackAppearance(t, [appears_on])
                            else:
                                self.tracks[t.canonical][t.version].appears_on.append(appears_on)

                            if t.rating > self.tracks[t.canonical][t.version].track.rating:
                                self.tracks[t.canonical][t.version].track.rating = t.rating
                    if 'date' not in episode:
                        if 'release' not in episode or not Release(episode['release']).date:
                            print('missing date: ' + appears_on)

    def calculate_points(self):
        for track in self.tracks.values():
            for version in track.values():
                version.points = version.track.rating * 10 + len(version.appears_on)

    def top1000(self):
        versions = []
        for track in self.tracks.values():
            possible_tracks = [t for t in track.values() if not t.track.is_time_code and 'ID' not in t.track.original]
            if len(possible_tracks) == 0:
                continue
            versions.append(sorted(possible_tracks, key=lambda x: (x.points, x.track.version == 'Original Mix'), reverse=True)[0])

        versions = sorted(versions, key=lambda x: (x.points, sorted(x.appears_on)[0]), reverse=True)
        
        return versions[:1000]

class URL:
    url: str

    def __init__(self, url) -> None:
        self.url = url

    def html(self) -> str:
        host = self.url.split('/')[2]
        if host == '1001.tl':
            return '<a href="%s" class="tracklists">&nbsp;</a>' % self.url
        else:
            raise Exception("unknown host: %s" % host)

class Release:
    original: str
    date: str
    series: str
    number: str
    title: str
    location: str
    artists: list[str]

    def __init__(self, original) -> None:
        self.original = original
        self.date = match_first('^([\d-]+):', original, '')
        self.series = match_first('[\d-]+:([^,#]+)', original, '').replace('[', '').replace(']', '').strip()
        if self.series == '':
            self.series = match_first('^([^,#]+)', original, '').strip()
        self.number = match_first('#(\d+)', original, '')
        self.title = match_first('"(.*?)"', original, '').replace('[', '').replace(']', '')
        self.location = match_first("\": (.*)", original, '')
        self.artists = re.findall(r"\[(.*?)\]", original)

class Location:
    name: str
    contains: List # List[Location]

    def __init__(self, location) -> None:
        self.name = location['name']
        self.contains = []
        if 'contains' in location:
            self.contains = [Location(l) for l in location['contains']]

    def __repr__(self) -> str:
        return self.name

class LocationRepo:
    root: Location

    def __init__(self) -> None:
        with open("locations.yaml") as locations_file:
            locations_details = yaml.safe_load(locations_file)
            self.root = Location({'name': 'Root', 'contains': locations_details['locations']})

    def check_location(self, name):
        parts = name.split(', ')
        root = self.root
        for part in reversed(parts):
            found = False
            for location in root.contains:
                if location.name == part:
                    root = location
                    found = True

            if not found:
                print("missing location: %s (%s)" % (name, part))
                return False

        return True

def match_first(regex, s, default):
    m = re.findall(regex, s)
    if len(m) > 0:
        return m[0]

    return default

class Broadcasts:
    def __init__(self, artist_repo):
        self.total_episodes = 0
        self.total_tracks = 0
        self.total_liked = 0
        self.series = []
        self.artists = {}
        self.artist_repo = artist_repo

    def refresh(self):
        self.series.sort(key=lambda x: x.name)
        self.total_episodes = 0
        self.total_tracks = 0
        self.total_liked = 0
        self.artists = {}
        for series in self.series:
            series.refresh()
            self.total_episodes += series.total_episodes
            self.total_tracks += series.total_tracks
            self.total_liked += series.total_liked
            append_artists(self.artists, series.artists)

    def write_toc(self, f):
        w(f, "<table style='border: 1px solid black'>")
        w(f, "<tr style='border: 1px solid black'>")
        w(f, "<th>&nbsp;</th>")
        w(f, "<th>Episodes</th>")
        w(f, "<th>Liked</th>")
        w(f, "<th>Tracks</th>")
        w(f, "</tr>")
        w(f, "<tr style='background: LightGray'><td><strong>Total</strong></td><td>%d</td><td>%d</td><td>%d</td></tr>" % (
            self.total_episodes, self.total_liked, self.total_tracks))
        for series in self.series:
            w(f, "<tr style='background: LightGray'><td><strong>%s</strong></td><td>%d</td><td>%d</td><td>%d</td></tr>" % (
                series.name, series.total_episodes, series.total_liked, series.total_tracks))
            for subseries in series.subseries:
                if subseries.total_episodes == 0:
                    continue
                w(f, "<tr><td>&nbsp;&nbsp;&nbsp;%s <a href=\"#%s\">%s</a></td><td>%d</td><td>%d</td><td>%d</td></tr>" % (
                    status_emoji(subseries.status),
                    anchor_name(series.name+"_"+subseries.name), subseries.name,
                    subseries.total_episodes, subseries.total_liked, subseries.total_tracks))
        w(f, "</table>")

    def write_top1000(self, f):
        tracks = {}
        for series in self.series:
            if series.name != 'A State of Trance' and \
                series.name != 'Future Sound of Egypt' and \
                series.name != 'Group Therapy' and \
                series.name != 'Sophie Sugar\'s Symphony' and \
                series.name != 'The Anjunadeep Edition' and \
                series.name != 'Tritonia' and \
                series.name != 'VONYC Sessions':
                continue

            for subseries in series.subseries:
                for episode in subseries.episodes:
                    for title in episode.liked:
                        if is_time_code(title) or 'ID' in title:
                            continue

                        loved = False
                        if title.startswith('+ '):
                            title = title[2:]
                            loved = True

                        if title not in tracks:
                            tracks[title] = {'count': 0, 'loved': False, 'earliest': ''}

                        tracks[title]['count'] += 1
                        if loved:
                            tracks[title]['loved'] = True

                        appears = episode.formatted_title()
                        if tracks[title]['earliest'] == '' or appears < tracks[title]['earliest']:
                            tracks[title]['earliest'] = appears

        sorted_tracks = []
        for track in tracks:
            sorted_tracks.append({
                'count': tracks[track]['count'],
                'loved': tracks[track]['loved'],
                'earliest': tracks[track]['earliest'],
                'title': track,
            })

        sorted_tracks = sorted(sorted_tracks, key=lambda x: (not x['loved'], 1000 - x['count'], x['earliest'], x['title']))

        w(f, "<table style='border: 1px solid black'>")
        w(f, "<tr style='border: 1px solid black'>")
        w(f, "<th>Title</th>")
        w(f, "<th>First Appeared</th>")
        w(f, "</tr>")

        for track in sorted(sorted_tracks[:1000], key=lambda x: x['title']):
            count = track['count']
            if track['loved']:
                count += 10

            w(f, "<tr>")
            if count >= 5:
                w(f, "<td valign='top'><strong>%s</strong></td>" % render_track(self.artist_repo, track['title']))
            else:
                w(f, "<td valign='top'>%s</td>" % render_track(self.artist_repo, track['title']))
            w(f, "<td valign='top'>%s</td>" % track['earliest'])
            w(f, "</tr>")
        w(f, "</table>")

    def write(self, f):
        for series in self.series:
            series.write(f, self.artist_repo)

def is_time_code(title):
    return title.startswith('@')

def render_track(artist_repo, s):
    if ' - ' in s and '[' not in s:
        parts = s.split(' - ')
        a = artist_repo.get_artist(parts[1])
        if a is not None:
            return parts[0] + ' - <a href="%s">%s</a>' % (a.rym, parts[1])

    artists = re.findall('\[(.*?)\]', s)
    for artist in artists:
        a = artist_repo.get_artist(artist)
        if a is None:
            s = s.replace("[%s]" % artist, "<u>%s</u>" % artist)
        else:
            s = s.replace("[%s]" % artist, "<a href=\"%s\">%s</a>" % (a.rym, artist))

    return s

class Series:
    def __init__(self, name):
        self.name = name
        self.total_episodes = 0
        self.total_tracks = 0
        self.total_liked = 0
        self.subseries = []
        self.artists = {}

    def refresh(self):
        self.subseries.sort(key=lambda x: x.name)
        self.total_episodes = 0
        self.total_tracks = 0
        self.total_liked = 0
        self.artists = {}
        for subseries in self.subseries:
            subseries.refresh()
            self.total_episodes += subseries.total_episodes
            self.total_tracks += subseries.total_tracks
            self.total_liked += subseries.total_liked
            append_artists(self.artists, subseries.artists)

    def write(self, f, artist_repo):
        w(f, "<h1>%s</h1>" % self.name)
        w(f, "<strong>%d episodes<span style=\"float: right\">%d/%d</span></strong>" % (
            self.total_episodes, self.total_liked, self.total_tracks))

        for subseries in self.subseries:
            subseries.write(f, self, artist_repo)

class Subseries:
    def __init__(self, parent_series, name, **entries):
        self.name = name
        self.status = ''
        self.from_number = 0
        self.to_number = 0
        self.total_tracks = 0
        self.total_liked = 0
        self.total_episodes = 0
        self.episodes = []
        self.artists = {}
        self.parent_series = parent_series

        if 'series' in entries:
            if 'status' in entries['series']:
                self.status = entries['series']['status']
            if 'from' in entries['series']:
                self.from_number = entries['series']['from']
            if 'to' in entries['series']:
                self.to_number = entries['series']['to']
        if 'episodes' in entries:
            self.episodes = [Episode(**e) for e in entries['episodes']]

    def refresh(self):
        self.total_tracks = 0
        self.total_liked = 0
        self.total_episodes = len(self.episodes)
        self.artists = {}
        for episode in self.episodes:
            episode.refresh()
            self.total_tracks += episode.total_tracks
            self.total_liked += episode.total_liked
            append_artists(self.artists, episode.artists)

    def write(self, f, series, artist_repo):
        range = ''
        if self.from_number:
            if self.to_number:
                range = '<span style=\"float: right\">#%s - #%s</span>' % (
                    self.from_number, self.to_number)
            else:
                range = '<span style=\"float: right\">#%s - </span>' % self.from_number

        w(f, "<a name=\"%s\"><h2>%s %s%s</h2>" % (
            anchor_name(series.name+"_"+self.name), status_emoji(self.status), self.name, range))
        w(f, "<strong>%d episodes<span style=\"float: right\">%d/%d</span></strong>" % (
            self.total_episodes, self.total_liked, self.total_tracks))
        for episode in self.episodes:
            episode.write(f, artist_repo)

class Episode:
    def __init__(self, **entries):
        self.number = 0
        self.tracks = 0
        self.liked = []
        self.rating = ''
        self.total_tracks = 0
        self.total_liked = 0
        self.urls = []
        self.artists = {}
        self.series = ''
        self.date = ''
        self.release = ''
        self.duration = 0
        self.location = ''
        self.listened = True
        
        if 'release' in entries:
            r = Release(entries['release'])
            self.release = entries['release']
            self.number = r.number
            self.title = r.title
            self.date = r.date
            self.series = r.series
            self.location = r.location
        if 'number' in entries:
            self.number = entries['number']
        if 'tracks' in entries:
            self.tracks = entries['tracks']
        if 'liked' in entries:
            self.liked = entries['liked']
        if 'rating' in entries:
            self.rating = entries['rating']
        if 'urls' in entries:
            self.urls = entries['urls']
        if 'duration' in entries:
            if match := re.search(r'(\d+)\s*h', entries['duration'], re.IGNORECASE):
                self.duration += int(match.group(1)) * 60
            if match := re.search(r'(\d+)\s*m', entries['duration'], re.IGNORECASE):
                self.duration += int(match.group(1))
            if match := re.search(r'(\d+)\s*s', entries['duration'], re.IGNORECASE):
                self.duration += round((float(match.group(1)) / 60))
            if match := re.search(r'(\d+):(\d+):(\d+)', entries['duration'], re.IGNORECASE):
                self.duration = int(match.group(1)) * 60 + int(match.group(2)) + round((float(match.group(3)) / 60))

        if self.duration == 0:
            print("missing duration: %s" % self.release)

        if 'listened' in entries:
            self.listened = entries['listened']

    def refresh(self):
        self.total_tracks = self.tracks
        self.total_liked = len(self.liked)
        self.artists = {}

        for track in self.liked:
            append_artist(self.artists, track, self.formatted_title())

    def score(self):
        if self.rating != '':
            if isinstance(self.rating, int):
                return self.rating - 1
            
            return int(self.rating.split('/')[0]) - 1

        if len(self.liked) == 0:
            return 0
        
        hours = self.hours()
        final = round(float(len(self.liked)) / hours * 2)
        if final > 9:
            final = 9
        
        return final
    
    def hours(self):
        return self.duration / 60

    def score_html(self):
        return '<span class="r%d">&nbsp;</span>' % self.score()

    def duration_str(self):
        if self.duration == 0:
            return '?'
        h = int(self.duration / 60)
        m = self.duration - (h * 60)
        if h == 0:
            return '%dm' % m
        if m == 0:
            return '%dh' % h
        return '%dh%02dm' % (h, m)

    def formatted_title(self):
        return self.release

    def write(self, f, artist_repo):
        tracks = '?'
        if self.tracks:
            tracks = self.tracks

        title = self.formatted_title()

        urls = []
        for url in self.urls:
            host = url.split('/')[2]
            if host == '1001.tl':
                urls.append('<a href="%s" class="tracklists">&nbsp;</a>' % url)
            else:
                raise Exception("unknown host: %s" % host)

        if self.rating:
            w(f, "<h3>%s %s<span style=\"float: right\">%s</span></h3>" % (
                rating_emoji(self.rating), title, tracks))
        else:
            w(f, "<h3>%s %s<span style=\"float: right\">%s/%s</span></h3>" % (
                title, ''.join(urls), len(self.liked), tracks))

        if len(self.liked) > 0:
            w(f, "<ul>")
            for t in self.liked:
                w(f, "<li>%s</li>" % render_track(artist_repo, t))
            w(f, "</ul>")

def append_artist(artists, s, on):
    track = parse_track(s)
    if track is not None:
        for artist in track['artists']:
            if artist not in artists:
                artists[artist] = {}
            if track['title'] not in artists[artist]:
                artists[artist][track['title']] = {'on': []}
            artists[artist][track['title']]['on'].append(on)

def append_artists(dest, src):
    for artist in src:
        if artist not in dest:
            dest[artist] = {}
        for title in src[artist]:
            if title not in dest[artist]:
                dest[artist][title] = {'on': []}
            dest[artist][title]['on'].extend(src[artist][title]['on'])

def parse_track(s):
    if s.startswith('@'):
        return None

    if s.startswith('+ '):
        s = s[2:]

    parts = s.split(' - ')
    artists = re.findall('\[(.*?)\]', s)

    if len(parts) == 2:        
        title = parts[0]
        title = re.sub(r'\{.*?\}', '', title).strip()

        if '[' in parts[1]:
            return {'title': title, 'artists': artists}

        return {'title': title, 'artists': [parts[1]]}
    
    print("cannot parse track: "+s)
    return None

def w(f, s):
    f.write("%s\n" % s)

def anchor_name(s):
    return re.sub(r'[^a-z0-9_]', '_', s.lower())

def rating_emoji(rating):
    if rating == '7/10' or rating == '8/10':
        return '👍'
    
    if rating == '9/10' or rating == '10/10':
        return '❤️'
    
    return '▫️'

def status_emoji(status):
    if status == 'complete':
        return '🟢'
    
    if status == 'incomplete':
        return '🟡'
    
    return ''

artist_repo = ArtistRepo()
track_repo = TrackRepo()
location_repo = LocationRepo()

broadcasts = Broadcasts(artist_repo)
for s in sorted(os.listdir("Broadcasts")):
    if not os.path.isdir("Broadcasts/%s" % s):
        continue

    series = Series(s)
    for path in os.listdir("Broadcasts/%s" % s):
        if path.endswith('.yaml'):
            track_repo.load_broadcast_file("Broadcasts/%s/%s" % (s, path), s)
            with open("Broadcasts/%s/%s" % (s, path)) as f2:
                file = yaml.safe_load(f2)
                subseries = Subseries(series, path[:-5], **file)
                series.subseries.append(subseries)

    broadcasts.series.append(series)

broadcasts.refresh()
track_repo.calculate_points()

with open('index.html', "w") as f:
    w(f, "<html>")

    w(f, "<head>")
    w(f, "<meta charset=\"UTF-8\">")
    w(f, "<style>")
    w(f, """
    html, body {
        font-family: Roboto, sans-serif;
        width: 800px;
    }
    h1 {
        color: orange;
        border-bottom: orange 1px solid;
    }
    h2 {
        color: blue;
        border-bottom: blue 1px solid;
    }
    table, th, td {
        border: 1px solid black;
        border-collapse: collapse;
    }
    a.tracklists {
      background-image: url("https://cdn.1001tracklists.com/images/static/1001icon_s.png");
      background-size: 16px 16px;
      text-decoration: none;
      background-repeat: no-repeat;
      width: 16px;
      display: inline-block;
    }
    """)
    w(f, "</style>")
    w(f, "</head>")

    w(f, "<body>")
    w(f, "Episodes | <a href='artists.html'>Artists</a> | <a href='tracks.html'>Tracks</a> | <a href='top1000.html'>Top 1000</a><br/><br/>")
    broadcasts.write_toc(f)
    broadcasts.write(f)
    w(f, "</body>")
    w(f, "</html>")

with open('top1000.html', "w") as f:
    w(f, "<html>")

    w(f, "<head>")
    w(f, "<meta charset=\"UTF-8\">")
    w(f, "<style>")
    w(f, """
    html, body {
        font-family: Roboto, sans-serif;
    }
    table, th, td {
        border: 1px solid black;
        border-collapse: collapse;
    }
    a:link, a:visited {
        color: SlateBlue;
    }
    """)
    w(f, "</style>")
    w(f, "</head>")

    w(f, "<body>")
    w(f, "<a href='index.html'>Episodes</a> | <a href='tracks.html'>Tracks</a> | Top 1000 | <a href='releases.html'>Releases</a><br/><br/>")
    broadcasts.write_top1000(f)
    w(f, "</body>")
    w(f, "</html>")

with open('tracks.html', "w") as f:
    w(f, "<html>")

    w(f, "<head>")
    w(f, "<meta charset=\"UTF-8\">")
    w(f, "<style>")
    w(f, """
    html, body {
        font-family: Roboto, sans-serif;
    }
    table, th, td {
        border: 1px solid black;
        border-collapse: collapse;
    }
    a:link, a:visited {
        color: SlateBlue;
    }
    """)
    w(f, "</style>")
    w(f, "</head>")

    w(f, "<body>")
    w(f, "<a href='index.html'>Episodes</a> | Tracks | <a href='top1000.html'>Top 1000</a> | <a href='releases.html'>Releases</a><br/><br/>")
    w(f, "<table style='border: 1px solid black'>")
    w(f, "<tr style='border: 1px solid black'>")
    w(f, "<th>&nbsp;</th>")
    w(f, "<th>Title</th>")
    w(f, "<th>Artists</th>")
    w(f, "<th>Version</th>")
    w(f, "<th>Appears On</th>")
    w(f, "</tr>")
    for canonical in sorted(track_repo.tracks):
        for version in sorted(track_repo.tracks[canonical]):
            appearance = track_repo.tracks[canonical][version]
            if appearance.track.is_time_code:
                continue

            w(f, "<tr style='border: 1px solid black'>")
            w(f, "<td valign='top'>"+appearance.track.render_rating()+"</td>")
            w(f, "<td valign='top'>"+appearance.track.render_title(artist_repo)+"</td>")
            w(f, "<td valign='top'>"+appearance.track.render_artist(artist_repo)+"</td>")
            w(f, "<td valign='top'>"+appearance.track.render_version(artist_repo)+"</td>")
            w(f, "<td nowrap>"+'<br/>'.join(sorted(appearance.appears_on))+"</td>")
            w(f, "</tr>")
    w(f, "</table>")
    w(f, "</body>")
    w(f, "</html>")

def strip_annotations(s: str) -> str:
    return re.sub(r'[\[\]{}]', '', s)

with open('tracks.csv', "w") as f:
    w(f, 'title,artist,version,rating')
    for canonical in sorted(track_repo.tracks):
        for version in sorted(track_repo.tracks[canonical]):
            appearance = track_repo.tracks[canonical][version]
            if appearance.track.is_time_code:
                continue

            w(f, strip_annotations('"'+canonical.replace(' - ', '","')+'","'+appearance.track.version+'",'+str(appearance.track.rating)))

with open('top1000.html', "w") as f:
    w(f, "<html>")

    w(f, "<head>")
    w(f, "<meta charset=\"UTF-8\">")
    w(f, "<style>")
    w(f, """
    html, body {
        font-family: Roboto, sans-serif;
    }
    table, th, td {
        border: 1px solid black;
        border-collapse: collapse;
    }
    a:link, a:visited {
        color: SlateBlue;
    }
    """)
    w(f, "</style>")
    w(f, "</head>")

    w(f, "<body>")
    w(f, "<a href='index.html'>Episodes</a> | <a href='tracks.html'>Tracks</a> | Top 1000 | <a href='releases.html'>Releases</a><br/><br/>")

    w(f, "<ol>")
    for version in track_repo.top1000():
        if version.track.rating >= 8:
            w(f, "<strong>")
        if version.track.version == 'Original Mix':
            w(f, "<li>"+version.track.render_title(artist_repo)+" - "+version.track.render_artist(artist_repo)+"</li>")
        else:
            w(f, "<li>"+version.track.render_title(artist_repo)+" ("+version.track.render_version(artist_repo)+") - "+version.track.render_artist(artist_repo)+"</li>")
        if version.track.rating >= 8:
            w(f, "</strong>")
    w(f, "</ol>")
    w(f, "</body>")
    w(f, "</html>")

def write_location_options(f, location, indent, path):
    if len(indent) > 18:
        return
    if path == "":
        w(f, '<option value="%s">%s%s</option>' % (location.name, indent, location.name))
    else:
        w(f, '<option value="%s">%s%s</option>' % (location.name + ', ' + path, indent, location.name))
    for l in location.contains:
        if path == "":
            write_location_options(f, l, indent+'&nbsp;&nbsp;&nbsp;', location.name)
        else:
            write_location_options(f, l, indent+'&nbsp;&nbsp;&nbsp;', location.name + ', ' + path)

with open('releases.html', "w") as f:
    w(f, "<html>")

    w(f, "<head>")
    w(f, "<meta charset=\"UTF-8\">")
    w(f, "<style>")
    w(f, """
    html, body {
        font-family: Roboto, sans-serif;
    }
    .release {
      font-family: Monaco;
      font-size: 14px;
    }
    .duration {
      font-size: 12px;
      color: gray;
    }
    table, th, td {
        border: 1px solid black;
        border-collapse: collapse;
    }
    a:link, a:visited {
        color: SlateBlue;
    }
    a.tracklists {
      background-image: url("https://cdn.1001tracklists.com/images/static/1001icon_s.png");
      background-size: 16px 16px;
      text-decoration: none;
      background-repeat: no-repeat;
      width: 16px;
      display: inline-block;
    }
      
    /* https://loading.io/color/feature/Spectral-10/ */
    .r0 { background-color: #9e0142; padding-left: 5px; padding-right: 5px; color: #61febd; }
    .r1 { background-color: #d53e4f; padding-left: 5px; padding-right: 5px; color: #2ac1b0; }
    .r2 { background-color: #f46d43; padding-left: 5px; padding-right: 5px; color: #0b92bc; }
    .r3 { background-color: #fdae61; padding-left: 5px; padding-right: 5px; color: #02519e; }
    .r4 { background-color: #fee08b; padding-left: 5px; padding-right: 5px; color: #011f74; }
    .r5 { background-color: #e6f598; padding-left: 5px; padding-right: 5px; color: #190a67; }
    .r6 { background-color: #abdda4; padding-left: 5px; padding-right: 5px; color: #54225b; }
    .r7 { background-color: #66c2a5; padding-left: 5px; padding-right: 5px; color: #993d5a; }
    .r8 { background-color: #3288bd; padding-left: 5px; padding-right: 5px; color: #cd7742; }
    .r9 { background-color: #5e4fa2; padding-left: 5px; padding-right: 5px; color: #a1b05d; }
    """)
    w(f, "</style>")

    all = []
    for series in broadcasts.series:
        for subseries in series.subseries:
            all.extend([e for e in subseries.episodes if e.date])

    all = sorted(all, key=lambda x: x.formatted_title())

    all_series = {}
    all_artists = {}
    for release in all:
        if not release.listened:
            continue
        
        if artist_repo.get_artist(release.series) is None:
            if release.series not in all_series:
                all_series[release.series] = [0, 0]
            all_series[release.series][0] += 1
            all_series[release.series][1] += release.duration

        for artist in Release(release.release).artists:
            if artist not in all_artists:
                all_artists[artist] = 0
            all_artists[artist] += 1

    w(f, '<script src="https://code.jquery.com/jquery-3.7.1.min.js"></script>')
    w(f, "<script>const releases = [")
    for release in all:
        if release.location:
            location_repo.check_location(release.location)

        duration = ''
        if release.duration:
            duration = ' <span class="duration">(' + release.duration_str() + ')</a>'

        listened = 'false'
        if release.listened:
            listened = 'true'

        w(f, "{rating: %d, year: %s, release: \"%s\", html: \"%s\", series: \"%s\", tracks: %d, duration: %f, listened: %s}," % (
            release.score(), release.date[:4], release.formatted_title().replace('"', '\\"'),
            (apply_artists(release.formatted_title(), artist_repo) + ' ' + ''.join([URL(url).html() for url in release.urls]) + duration).replace('"', '\\"'),
            release.series, release.tracks, release.duration, listened))
    w(f, """
    ];
      
    function refresh() {
        const minRating = $('#minrating option:selected').text();
        const maxRating = $('#maxrating option:selected').text();
        const minYear = $('#minyear option:selected').text();
        const maxYear = $('#maxyear option:selected').text();
        const series = $('#series option:selected').val();
        const artist = $('#artist option:selected').val();
        const location = $('#location option:selected').val();
        let html = '<ol>';
    
        const sort = $('#sort option:selected').text();
        if (sort == 'Title') {
            releases.sort((a, b) => a.release.localeCompare(b.release));
        }
        if (sort == 'Rating') {
            releases.sort((a, b) => b.rating - a.rating);
        }

        let releaseCount = 0;
        let totalReleaseCount = 0;
        let trackCount = 0;
        let duration = 0;
        let totalDuration = 0;
        for (const release of releases) {
            if (series != 'All Series' && release.series != series) {
                continue;
            }
            if (artist != 'All Artists' && !release.release.includes('[' + artist + ']')) {
                continue;
            }
            if (!release.release.includes(location)) {
                continue;
            }
      
            ++totalReleaseCount;
            totalDuration += release.duration;
            if (!release.listened) {
                continue;
            }
            if (release.rating >= minRating && release.rating <= maxRating &&
                release.year >= minYear && release.year <= maxYear) {
                html += `<li><span class="r${release.rating}">&nbsp;</span> ${Math.floor(release.rating/2)+1} <span class='release'>` + release.html + '</span></li>';
                releaseCount++;
                trackCount += release.tracks;
                duration += release.duration;
            }
        }
        $('#results').html(`<p>${releaseCount} of ${totalReleaseCount} releases, ${trackCount} tracks, ${Math.round(duration / 60)} of ${Math.round(totalDuration / 60)} hours:</p>` + html + '</ol>');
    }
    </script>
    """)
    w(f, "</head>")

    w(f, "<body>")
    w(f, "<a href='index.html'>Episodes</a> | <a href='tracks.html'>Tracks</a> | <a href='top1000.html'>Top 1000</a> | Releases<br/><br/>")

    w(f, "<form>")
    w(f, '<span class="r0">0</span><span class="r1">1</span><span class="r2">2</span><span class="r3">3</span><span class="r4">4</span><span class="r5">5</span><span class="r6">6</span><span class="r7">7</span><span class="r8">8</span><span class="r9">9</span>')
    w(f, "Rating: <select id='minrating' onchange='refresh()'><option>0</option><option>1</option><option>2</option><option>3</option><option>4</option><option>5</option><option>6</option><option>7</option><option>8</option><option>9</option></select>")
    w(f, "- <select id='maxrating' onchange='refresh()'><option>0</option><option>1</option><option>2</option><option>3</option><option>4</option><option>5</option><option>6</option><option>7</option><option>8</option><option selected>9</option></select>")
    w(f, "Year: <select id='minyear' onchange='refresh()'><option>2001</option><option>2002</option><option>2003</option><option>2004</option><option>2005</option><option>2006</option><option>2007</option><option>2008</option><option>2009</option><option>2010</option><option>2011</option><option>2012</option><option>2013</option><option>2014</option><option>2015</option><option>2016</option><option>2017</option><option>2018</option><option>2019</option><option>2020</option>><option>2021</option><option>2022</option><option>2023</option><option>2024</option></select>")
    w(f, "- <select id='maxyear' onchange='refresh()'><option>2001</option><option>2002</option><option>2003</option><option>2004</option><option>2005</option><option>2006</option><option>2007</option><option>2008</option><option>2009</option><option>2010</option><option>2011</option><option>2012</option><option>2013</option><option>2014</option><option>2015</option><option>2016</option><option>2017</option><option>2018</option><option>2019</option><option>2020</option><<option>2021</option><option>2022</option><option>2023</option><option selected>2024</option></select>")
    w(f, "<select id='series' onchange='refresh()'>")
    w(f, '<option>%s</option>' % 'All Series')
    for series in sorted(all_series.keys()):
        w(f, '<option value="%s">%s (%d / %dh)</option>' % (series, series, all_series[series][0], round(all_series[series][1] / 60)))
    w(f, "</select>")
    w(f, "<select id='artist' onchange='refresh()'>")
    w(f, '<option>%s</option>' % 'All Artists')
    for artist in sorted(all_artists.keys()):
        w(f, '<option value="%s">%s (%d)</option>' % (artist, artist, all_artists[artist]))
    w(f, "</select>")
    w(f, "<select id='location' onchange='refresh()'>")
    w(f, '<option value="">%s</option>' % 'All Locations')
    for l in location_repo.root.contains:
        write_location_options(f, l, '', '')
    w(f, "</select>")
    w(f, "Sort: <select id='sort' onchange='refresh()'>")
    w(f, '<option>Title</option>')
    w(f, '<option>Rating</option>')
    w(f, "</select>")
    w(f, "</form>")

    w(f, "<div id='results'></div>")
    w(f, "<script>refresh();</script>")

    w(f, "</body>")
    w(f, "</html>")

def square(score):
    if score <= 1:
        return '🟥'
    if score <= 3:
        return '🟧'
    if score <= 5:
        return '🟨'
    if score <= 7:
        return '🟩'
    if score <= 8:
        return '🟦'

    return '🟪'

with open('releases.md', "w") as f:
    all = []
    for series in broadcasts.series:
        for subseries in series.subseries:
            all.extend([e for e in subseries.episodes if e.date])

    all = sorted(all, key=lambda x: x.formatted_title())

    for release in all:
        # if release.location:
        #     location_repo.check_location(release.location)

        # duration = ''
        # if release.duration:
        #     duration = ' <span class="duration">(' +  + ')</a>'

        # listened = 'false'
        if not release.listened:
            continue

        w(f, "### %s\n" % release.formatted_title())
        if release.tracks > 0:
            w(f, "> %s %d/10 | %s | %d tracks" % (square(release.score()), release.score()+1, release.duration_str(), release.tracks))
        else:
            w(f, "> %s %d/10 | %s" % (square(release.score()), release.score()+1, release.duration_str()))

        if release.urls:
            w(f, "> | [1001tracklists](%s)" % release.urls[0])

        w(f, "")
        for t in release.liked:
            t = t.replace('{', '_(')
            t = t.replace('}', ')_')
            t = t.replace(']', '](#)')
            w(f, "- %s" % t)

        if len(release.liked) > 0:
            w(f, "")

            # (apply_artists(release.formatted_title(), artist_repo) + ' ' + ''.join([URL(url).html() for url in release.urls]) + duration).replace('"', '\\"'),
            # release.series, , , listened))
