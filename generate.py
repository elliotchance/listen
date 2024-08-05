import yaml
import os
import re

class Broadcasts:
    def __init__(self):
        self.total_episodes = 0
        self.total_tracks = 0
        self.total_liked = 0
        self.series = []
        self.artists = {}

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
                w(f, "<tr><td>&nbsp;&nbsp;&nbsp;%s <a href=\"#%s\">%s</a></td><td>%d</td><td>%d</td><td>%d</td></tr>" % (
                    status_emoji(subseries.status),
                    anchor_name(series.name+"_"+subseries.name), subseries.name,
                    subseries.total_episodes, subseries.total_liked, subseries.total_tracks))
        w(f, "</table>")

    def write_artists(self, f):
        w(f, "<table style='border: 1px solid black'>")
        w(f, "<tr style='border: 1px solid black'>")
        w(f, "<th>Artist</th>")
        w(f, "<th>Title (On)</th>")
        w(f, "</tr>")
        for artist in sorted(self.artists):
            w(f, "<tr><td valign='top'>%s</td><td>%s</td></tr>" % (
                artist, '<br/>'.join(['%s (%s)' % (t['title'], t['on']) for t in self.artists[artist]])))
        w(f, "</table>")

    def write(self, f):
        for series in self.series:
            series.write(f)

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

    def write(self, f):
        w(f, "<h1>%s</h1>" % self.name)
        w(f, "<strong>%d episodes<span style=\"float: right\">%d/%d</span></strong>" % (
            self.total_episodes, self.total_liked, self.total_tracks))

        for subseries in self.subseries:
            subseries.write(f, self)

class Subseries:
    def __init__(self, name, **entries):
        self.name = name
        self.status = ''
        self.from_number = 0
        self.to_number = 0
        self.total_tracks = 0
        self.total_liked = 0
        self.total_episodes = 0
        self.episodes = []
        self.artists = {}

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

    def write(self, f, series):
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
            episode.write(f)

class Episode:
    def __init__(self, **entries):
        self.number = 0
        self.tracks = 0
        self.liked = []
        self.title = ''
        self.artist = ''
        self.parts = []
        self.rating = ''
        self.total_tracks = 0
        self.total_liked = 0
        self.artists = {}
        
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

    def refresh(self):
        self.total_tracks = self.tracks
        self.total_liked = len(self.liked)
        self.artists = {}

        for track in self.liked:
            append_artist(self.artists, track, self.formatted_title())

        for part in self.parts:
            part.refresh()
            self.total_tracks += part.total_tracks
            self.total_liked += part.total_liked
            append_artists(self.artists, part.artists)

    def formatted_title(self):
        title = ''
        if self.number:
            title = '#' + str(self.number)
        
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

    def write(self, f):
        tracks = '?'
        if self.tracks:
            tracks = self.tracks

        title = self.formatted_title()

        if self.rating:
            w(f, "<h3>%s %s<span style=\"float: right\">%s</span></h3>" % (
                rating_emoji(self.rating), title, tracks))
        else:
            w(f, "<h3>%s<span style=\"float: right\">%s/%s</span></h3>" % (
                title, len(self.liked), tracks))

        if len(self.liked) > 0:
            w(f, "<ul>")
            for t in self.liked:
                w(f, "<li>%s</li>" % t)
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
    parts = parse_track(s)
    if parts:
        if parts[1] not in artists:
            artists[parts[1]] = []
        artists[parts[1]].append({'title': parts[0], 'on': on})

def append_artists(dest, src):
    for k in src:
        if k not in dest:
            dest[k] = []
        dest[k].extend(src[k])

def parse_track(s):
    parts = s.split(' - ')
    if len(parts) == 2:
        return parts
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

broadcasts = Broadcasts()
for s in sorted(os.listdir("Broadcasts")):
    if not os.path.isdir("Broadcasts/%s" % s):
        continue

    series = Series(s)
    for path in os.listdir("Broadcasts/%s" % s):
        if path.endswith('.yaml'):
            with open("Broadcasts/%s/%s" % (s, path)) as f2:
                file = yaml.safe_load(f2)
                subseries = Subseries(path[:-5], **file)
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
    """)
    w(f, "</style>")
    w(f, "</head>")

    w(f, "<body>")
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
        width: 800px;
    }
    table, th, td {
        border: 1px solid black;
        border-collapse: collapse;
    }
    """)
    w(f, "</style>")
    w(f, "</head>")

    w(f, "<body>")
    broadcasts.write_artists(f)
    w(f, "</body>")
    w(f, "</html>")
