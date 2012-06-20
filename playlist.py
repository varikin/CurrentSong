from google.appengine.api import taskqueue, urlfetch
from google.appengine.ext import db

from datetime import date, datetime

from BeautifulSoup import BeautifulSoup
from models import Song

class PlaylistQueue(object):
    """Simple queue for getting the playlist for a day."""

    def add(self, playlist_date):
        """Adds the playlist date to the queue."""
        db.put(PlaylistTask(date=playlist_date))
        taskqueue.add(url="/playlist")

    def next(self):
        """Returns the next playlist date from the queue"""
        date = None
        task = PlaylistTask.all().order("added").get()
        if task is not None:
            date = task.date
            task.delete()
            db.put(Playlist(date).get_playlist())

class PlaylistTask(db.Model):
    """A playlist task."""
    date = db.DateProperty(required=True)
    added = db.DateTimeProperty(required=True, auto_now_add=True)

    def __init__(self, *args, **kwargs):
        playlist_date = kwargs.get('date', date.today())
        kwargs['key_name'] = playlist_date.strftime("%Y-%m-%d")
        super(PlaylistTask, self).__init__(*args, **kwargs)

    def __unicode__(self):
        return self.date.strftime("%Y-%m-%d")

    def __str__(self):
        return unicode(self)

    def __repr__(self):
        return unicode(self)


class Playlist(object):
    URL = 'http://minnesota.publicradio.org/radio/services/the_current/playlist/playlist.php'    

    def __init__(self, playlist_date):
        self.date = playlist_date
    
    def get_playlist(self):
        """Returns a list of songs for the playlist date."""
        songs = []
        song_blocks = self._get_songblocks()
        day = self.date.day
        month = self.date.month
        year = self.date.year
        for song_block in song_blocks:
            try:
                hour = self._get_hour(song_block)
                minute = self._get_minute(song_block)
                song_time = datetime(year, month, day, hour, minute)
                artist, title = self._get_artist_title(song_block)
                song = Song(title=title, artist=artist, time=song_time)
                songs.append(song)
            except ValueError, e:
                pass
        return songs

    def _get_songblocks(self):
        url = '%s?month=%d&day=%d&year=%d' % (Playlist.URL, self.date.month, 
                self.date.day, self.date.year)
        result = urlfetch.fetch(url)
        if result.status_code == 200:
            soup = BeautifulSoup(result.content)
            return soup.findAll('div', 'songBlock')
        else:
            return None

    def _get_artist_title(self, song_block):
        h4 = song_block.find('h4')
        children = h4.findAll(text=True)
        text = [c.strip() for c in children if c.strip() != u'']
        if len(text) >= 2:
            return text[0], text[1]
        else:
            raise ValueError("Couldn't find the artist and title")

    def _get_hour(self, song_block):
        for attr in song_block.attrs:
            if attr[0] == 'class':
                for cls in attr[1].split():
                    if cls.startswith('hour_'):
                            return int(cls[5:])
        return None

    def _get_minute(self, song_block):
        return int(song_block.find('div', 'playTime').text[-2:])

