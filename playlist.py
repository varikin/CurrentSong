from google.appengine.api import taskqueue, urlfetch
from google.appengine.ext import db

from datetime import datetime

from BeautifulSoup import BeautifulSoup
from models import Song, PlaylistTask
import logging

class PlaylistQueue(object):
    """Simple queue for getting the playlist for a day."""

    def add(self, playlist_date):
        """Adds the playlist date to the queue."""
        db.put(PlaylistTask(date=playlist_date))
        taskqueue.add(url="/tasks/playlist")

    def next(self):
        """Returns the next playlist date from the queue"""
        date = None
        task = PlaylistTask.all().order("added").get()
        logging.info("Next task is %s" % task)
        if task is not None:
            date = task.date
            task.delete()
            db.put(get_playlist(date))    

def get_playlist(playlist_date):
    """Returns a list of songs for the playlist date."""
    
    day = playlist_date.day
    month = playlist_date.month
    year = playlist_date.year

    song_blocks = _get_songblocks(day, month, year)

    songs = []
    for song_block in song_blocks:
        try:
            hour = _get_hour(song_block)
            minute = _get_minute(song_block)
            song_time = datetime(year, month, day, hour, minute)
            artist, title = _get_artist_title(song_block)
            song = Song(title=title, artist=artist, time=song_time)
            songs.append(song)
        except ValueError, e:
            pass
    return songs

URL = 'http://minnesota.publicradio.org/radio/services/the_current/playlist/playlist.php'

def _get_songblocks(day, month, year):
    url = '%s?month=%d&day=%d&year=%d' % (URL, month, day, year)
    result = urlfetch.fetch(url)
    if result.status_code == 200:
        soup = BeautifulSoup(result.content)
        return soup.findAll('div', 'songBlock')
    else:
        return None

def _get_artist_title(song_block):
    h4 = song_block.find('h4')
    children = h4.findAll(text=True)
    text = [c.strip() for c in children if c.strip() != u'']
    if len(text) >= 2:
        return text[0], text[1]
    else:
        raise ValueError("Couldn't find the artist and title")

def _get_hour(song_block):
    for attr in song_block.attrs:
        if attr[0] == 'class':
            for cls in attr[1].split():
                if cls.startswith('hour_'):
                        return int(cls[5:])
    return None

def _get_minute(song_block):
    return int(song_block.find('div', 'playTime').text[-2:])

