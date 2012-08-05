from datetime import datetime, timedelta
import logging

from google.appengine.ext.webapp import template, WSGIApplication, RequestHandler
from google.appengine.ext.webapp.util import run_wsgi_app

from playlist import PlaylistQueue
from models import Song

#Cheapest timezone hack ever!
#Will need to change to 6 in a couple months:(
CST = timedelta(hours=-5)

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
                    PlaylistQueue().add(song_time.date())
            except ValueError, e:
                pass
                d, t = self.get_datetime()
        else:
            d, t = self.get_datetime()
        context['date'] = d
        context['time'] = t
        self.response.out.write(template.render('templates/index.html', context))
    
    def get_datetime(self, dt=None):
        if dt is None:
            dt = datetime.now() + CST
        return dt.strftime("%m/%d/%Y"), dt.strftime("%I:%M %p")

class PlaylistHandler(RequestHandler):
    def post(self):
        date = PlaylistQueue().next()
        
    
if __name__ == '__main__':
    run_wsgi_app(WSGIApplication([
        ('/', SongHandler),
        ('/playlist', PlaylistHandler),
    ]))
