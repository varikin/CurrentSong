#!/usr/bin/env python

import os
from BeautifulSoup import BeautifulSoup
from datetime import datetime, timedelta
from google.appengine.api import urlfetch
from google.appengine.ext import db, webapp
from google.appengine.ext.webapp import template, util

PLAYLIST_URL = 'http://minnesota.publicradio.org/radio/services/the_current/playlist/playlist.php'

class Song(db.Model):
    title = db.StringProperty(required=True)
    artist = db.StringProperty(required=True)
    time = db.DateTimeProperty(required=True)

    def __str__(self):
        return unicode(self)
        
    def __unicode__(self):
        return '%s by %s at %d:%d %d/%d/%d' % (self.title, self.artist, \
                self.time.hour, self.time.minute, self.time.month, \
                self.time.day, self.time.year)

    def __repr__(self):
        return str(self)
        

class MainHandler(webapp.RequestHandler):

    def get(self):
        #db.put(self.get_playlist(datetime(2010, 3, 20)))
        date = self.request.get('date')
        time = self.request.get('time')
        context = {}
        if date != '' and time != '':
            try:
                song_time = datetime.strptime("%s %s" % (date, time), \
                    "%m/%d/%Y %I:%M %p")
                delta = timedelta(minutes=10)
                songs = Song.all().order('time')
                songs.filter("time <", song_time + delta)
                songs.filter("time >", song_time - delta)
                context['songs'] = songs
                if songs.count() == 0:
                    db.put(self.get_playlist(song_time))
            except ValueError, e:
                pass
        self.response.out.write(template.render('index.html', context))
        

    def get_playlist(self, time):
        songs = []
        song_blocks = self.get_songblocks(time)
        for song_block in song_blocks:
            try:
                hour = self.get_hour(song_block)
                minute = self.get_minute(song_block)
                song_time = datetime(time.year, time.month, time.day, hour, minute)
                artist, title = self.get_artist_title(song_block)
                song = Song(key_name=str(song_time), title=title, artist=artist, time=song_time)
                songs.append(song)
            except ValueError, e:
                pass
        return songs     

    def get_songblocks(self, time):
        url = '%s?month=%d&day=%d&year=%d' % (PLAYLIST_URL, time.month, time.day, time.year)
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

def main():
    application = webapp.WSGIApplication([('/', MainHandler)], debug=True)
    util.run_wsgi_app(application)


if __name__ == '__main__':
    main()
