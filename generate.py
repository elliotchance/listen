import yaml
import os
import re

class Broadcasts:
    def __init__(self):
        self.total_episodes = 0
        self.total_tracks = 0
        self.total_liked = 0
        self.series = []

    def refresh(self):
        self.series.sort(key=lambda x: x.name)
        self.total_episodes = 0
        self.total_tracks = 0
        self.total_liked = 0
        for series in self.series:
            series.refresh()
            self.total_episodes += series.total_episodes
            self.total_tracks += series.total_tracks
            self.total_liked += series.total_liked

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

    def refresh(self):
        self.subseries.sort(key=lambda x: x.name)
        self.total_episodes = 0
        self.total_tracks = 0
        self.total_liked = 0
        for subseries in self.subseries:
            subseries.refresh()
            self.total_episodes += subseries.total_episodes
            self.total_tracks += subseries.total_tracks
            self.total_liked += subseries.total_liked

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
        for episode in self.episodes:
            episode.refresh()
            self.total_tracks += episode.total_tracks
            self.total_liked += episode.total_liked

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
        self.urls = []
        
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

        for part in self.parts:
            self.total_tracks += part.tracks
            self.total_liked += len(part.liked)

    def write(self, f):
        tracks = '?'
        if self.tracks:
            tracks = self.tracks

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
    broadcasts.write_toc(f)
    broadcasts.write(f)
    w(f, "</body>")
    w(f, "</html>")
