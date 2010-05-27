from BeautifulSoup import BeautifulSoup
from datetime import datetime, timedelta
import logging

from google.appengine.api import urlfetch
from google.appengine.api.labs import taskqueue
from google.appengine.ext import db
from google.appengine.ext.webapp import template, WSGIApplication, RequestHandler
from google.appengine.ext.webapp.util import run_wsgi_app

#Cheapest timezone hack ever!
#Will need to change to 6 in a couple months:(
CST = timedelta(hours=-5)

class Song(db.Model):
    title = db.StringProperty(required=True)
    artist = db.StringProperty(required=True)
    time = db.DateTimeProperty(required=True)

    def __str__(self):
        return unicode(self)

    def __unicode__(self):
        return '%s by %s at %s' % (self.title, self.artist, \
                self.time.strftime("%I:%M %p %m/%d/%Y"))

    def __repr__(self):
        return unicode(self)

class PlaylistQueueItem(db.Model):
    date = db.DateProperty(required=True)
    added = db.DateTimeProperty(required=True, auto_now_add=True)

    def __unicode__(self):
        return self.date.strftime("%Y-%m-%d")

    def __str__(self):
        return unicode(self)

    def __repr__(self):
        return unicode(self)

class PlaylistQueue(object):
    def add(self, date):
        db.put(PlaylistQueueItem(key_name=date.strftime("%Y-%m-%d"), date=date.date()))
        taskqueue.add(url="/playlist")

    def next(self):
        date = None
        task = PlaylistQueueItem.all().order("added").get()
        if task is not None:
            date = task.date
            task.delete()
        return date

class SongHandler(RequestHandler):
    def get(self):
        date = self.request.get('date')
        time = self.request.get('time')
        context = {}
        if date != '' and time != '':
            try:
                song_time = datetime.strptime("%s %s" % (date, time), \
                    "%m/%d/%Y %I:%M %p")
                d, t = self.get_datetime(song_time)
                delta = timedelta(minutes=10)
                songs = Song.all().order('time')
                songs.filter("time <", song_time + delta)
                songs.filter("time >", song_time - delta)
                context['songs'] = songs
                if songs.count() == 0:
                    PlaylistQueue().add(song_time)
            except ValueError, e:
                pass
                d, t = self.get_datetime()
        else:
            d, t = self.get_datetime()
        context['date'] = d
        context['time'] = t
        self.response.out.write(template.render('index.html', context))
    
    def get_datetime(self, dt=None):
        if dt is None:
            dt = datetime.now() + CST
        return dt.strftime("%m/%d/%Y"), dt.strftime("%I:%M %p")

class PlaylistHandler(RequestHandler):
    URL = 'http://minnesota.publicradio.org/radio/services/the_current/playlist/playlist.php'    

    def post(self):
        logging.debug("Entering POST")
        date = PlaylistQueue().next()
        db.put(self.get_playlist(date))
        logging.debug("Exiting POST")
        
    def get_playlist(self, date):
        songs = []
        song_blocks = self.get_songblocks(date)
        for song_block in song_blocks:
            try:
                hour = self.get_hour(song_block)
                minute = self.get_minute(song_block)
                song_time = datetime(date.year, date.month, date.day, hour, minute)
                artist, title = self.get_artist_title(song_block)
                song = Song(key_name=str(song_time), title=title, artist=artist, time=song_time)
                songs.append(song)
            except ValueError, e:
                pass
        return songs

    def get_songblocks(self, date):
        url = '%s?month=%d&day=%d&year=%d' % (PlaylistHandler.URL, date.month, date.day, date.year)
        result = urlfetch.fetch(url)
        if result.status_code == 200:
            soup = BeautifulSoup(result.content)
            return soup.findAll('div', 'songBlock')
        else:
            return None

    def get_artist_title(self, song_block):
        h4 = song_block.find('h4')
        children = h4.findAll(text=True)
        text = [c.strip() for c in children if c.strip() != u'']
        if len(text) >= 2:
            return text[0], text[1]
        else:
            raise ValueError("Couldn't find the artist and title")

    def get_hour(self, song_block):
        for attr in song_block.attrs:
            if attr[0] == 'class':
                for cls in attr[1].split():
                    if cls.startswith('hour_'):
                            return int(cls[5:])
        return None

    def get_minute(self, song_block):
        return int(song_block.find('div', 'playTime').text[-2:])

if __name__ == '__main__':
    run_wsgi_app(WSGIApplication([
        ('/', SongHandler),
        ('/playlist', PlaylistHandler),
    ]))