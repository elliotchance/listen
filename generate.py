import yaml
import os
import re
from typing import List, Set, Dict, Tuple

class Artist:
    name: str
    rym: str

    def __init__(self, m: Dict[str, str]) -> None:
        self.name = m['name']
        self.rym = m['rym']

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
    title: str
    artists: Set[str]
    is_time_code: bool
    is_boosted: bool

    def __init__(self, s: str) -> None:
        self.title = ''
        self.artists = set()
        self.is_time_code = False
        self.is_boosted = False

        if s.startswith('@'):
            self.is_time_code = True
            return

        if s.startswith('+ '):
            self.is_boosted = True
            s = s[2:]

        parts = s.split(' - ')
        artists = re.findall('\[(.*?)\]', s)

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

    def write_artists(self, f):
        w(f, "<table style='border: 1px solid black'>")
        w(f, "<tr style='border: 1px solid black'>")
        w(f, "<th>Artists</th><td>%s</td>" % len(self.artists))
        w(f, "</tr>")
        linked = 0
        tracks = 0
        unique_tracks = 0
        for artist in self.artists:
            for title in self.artists[artist]:
                unique_tracks += 1
                tracks += len(self.artists[artist][title]['on'])
            artist_details = self.artist_repo.get_artist(artist)
            if artist_details is not None:
                linked += 1
        
        w(f, "<tr><th>Linked</th><td>%d (%.2f%%)</td></tr>" % (linked, 100 * (float(linked) / len(self.artists))))
        w(f, "<tr><th>Tracks</th><td>%d</td></tr>" % tracks)
        w(f, "<tr><th>Unique Tracks</th><td>%d</td></tr>" % unique_tracks)
        w(f, "</table>")

        w(f, "<br/><br/>")

        w(f, "<table style='border: 1px solid black'>")
        w(f, "<tr style='border: 1px solid black'>")
        w(f, "<th>Artist</th>")
        w(f, "<th>Title (On)</th>")
        w(f, "</tr>")
        for artist in sorted(self.artists):
            artist_details = self.artist_repo.get_artist(artist)
            w(f, "<tr>")
            if artist_details is not None:
                w(f, "<td valign='top'><a href=\"%s\">%s</a></td>" % (artist_details.rym, artist))
            else:
                w(f, "<td valign='top'>%s</td>" % artist)

            w(f, "<td>")
            for title in sorted(self.artists[artist]):
                w(f, '%s<br/>' % render_track(self.artist_repo, title))
                for on in sorted(self.artists[artist][title]['on']):
                    w(f, '&nbsp;&nbsp;&nbsp;<em>%s</em><br/>' % on)
            w(f, "</td></tr>")
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

                        appears = episode.formatted_title(True)
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
            self.episodes = [Episode(self.parent_series, **e) for e in entries['episodes']]

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
    def __init__(self, series, **entries):
        self.number = 0
        self.tracks = 0
        self.liked = []
        self.title = ''
        self.artist = ''
        self.parts = []
        self.rating = ''
        self.total_tracks = 0
        self.total_liked = 0
        self.urls = []
        self.artists = {}
        self.series = series
        
        if 'number' in entries:
            self.number = entries['number']
        if 'tracks' in entries:
            self.tracks = entries['tracks']
        if 'liked' in entries:
            self.liked = entries['liked']
        if 'title' in entries:
            self.title = entries['title']
        if 'artist' in entries:
            self.artist = entries['artist']
        if 'rating' in entries:
            self.rating = entries['rating']
        if 'parts' in entries:
            self.parts = [EpisodePart(**p) for p in entries['parts']]
        if 'urls' in entries:
            self.urls = entries['urls']

    def refresh(self):
        self.total_tracks = self.tracks
        self.total_liked = len(self.liked)
        self.artists = {}

        for track in self.liked:
            append_artist(self.artists, track, self.formatted_title(True))

        for part in self.parts:
            part.refresh()
            self.total_tracks += part.total_tracks
            self.total_liked += part.total_liked
            append_artists(self.artists, part.artists)

    def formatted_title(self, full_name):
        title = ''

        if full_name:
            title = self.series.name + ' '

        if self.number:
            title += '#' + str(self.number)
        
        if self.artist:
            if title == '':
                title += self.artist
            else:
                title += ': %s' % self.artist
        
        if self.title:
            if title == '':
                title += self.title
            else:
                title += ', "%s"' % self.title

        return title

    def write(self, f, artist_repo):
        tracks = '?'
        if self.tracks:
            tracks = self.tracks

        title = self.formatted_title(False)

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

        for part in self.parts:
            w(f, "<ul>")
            part.write(f)
            w(f, "</ul>")

class EpisodePart:
    def __init__(self, **entries):
        self.tracks = 0
        self.liked = []
        self.title = ''
        self.artist = ''
        self.rating = ''
        self.artists = {}
        
        if 'tracks' in entries:
            self.tracks = entries['tracks']
        if 'liked' in entries:
            self.liked = entries['liked']
        if 'title' in entries:
            self.title = entries['title']
        if 'artist' in entries:
            self.artist = entries['artist']
        if 'rating' in entries:
            self.rating = entries['rating']

    def formatted_title(self):
        title = ''
        
        if self.artist:
            if title == '':
                title += self.artist
            else:
                title += ': %s' % self.artist
        
        if self.title:
            if title == '':
                title += self.title
            else:
                title += ', "%s"' % self.title

        return title

    def refresh(self):
        self.total_tracks = self.tracks
        self.total_liked = len(self.liked)
        self.artists = {}

        for track in self.liked:
            append_artist(self.artists, track, self.formatted_title())

    def write(self, f):
        tracks = '?'
        if self.tracks:
            tracks = self.tracks

        title = self.title
        if self.artist and self.title:
            title = '%s, "%s"' % (self.artist, self.title)
        elif self.artist:
            title = self.artist

        w(f, "<li>%s %s<span style=\"float: right\">%s/%s</span></li>" % (
            rating_emoji(self.rating), title, len(self.liked), tracks))
        if len(self.liked) > 0:
            w(f, "<ul>")
            for t in self.liked:
                w(f, "<li>%s</li>" % t)
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
    
    return '⚪'

def status_emoji(status):
    if status == 'complete':
        return '🟢'
    
    if status == 'incomplete':
        return '🟡'
    
    return ''

artist_repo = ArtistRepo()

broadcasts = Broadcasts(artist_repo)
for s in sorted(os.listdir("Broadcasts")):
    if not os.path.isdir("Broadcasts/%s" % s):
        continue

    series = Series(s)
    for path in os.listdir("Broadcasts/%s" % s):
        if path.endswith('.yaml'):
            with open("Broadcasts/%s/%s" % (s, path)) as f2:
                file = yaml.safe_load(f2)
                subseries = Subseries(series, path[:-5], **file)
                series.subseries.append(subseries)

    broadcasts.series.append(series)

broadcasts.refresh()

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
    w(f, "Episodes | <a href='artists.html'>Artists</a> | <a href='top1000.html'>Top 1000</a><br/><br/>")
    broadcasts.write_toc(f)
    broadcasts.write(f)
    w(f, "</body>")
    w(f, "</html>")

with open('artists.html', "w") as f:
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
    """)
    w(f, "</style>")
    w(f, "</head>")

    w(f, "<body>")
    w(f, "<a href='index.html'>Episodes</a> | Artists | <a href='top1000.html'>Top 1000</a><br/><br/>")
    broadcasts.write_artists(f)
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
    """)
    w(f, "</style>")
    w(f, "</head>")

    w(f, "<body>")
    w(f, "<a href='index.html'>Episodes</a> | <a href='artists.html'>Artists</a> | Top 1000<br/><br/>")
    broadcasts.write_top1000(f)
    w(f, "</body>")
    w(f, "</html>")
