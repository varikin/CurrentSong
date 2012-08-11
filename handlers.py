from datetime import datetime, timedelta
import simplejson
import logging

from google.appengine.ext.webapp import template, RequestHandler
from google.appengine.api import memcache

from playlist import PlaylistQueue
from models import Song

#Cheapest timezone hack ever!
#Will need to change to 6 in a couple months:(
CST = timedelta(hours=-5)
TIME_FORMAT = "%m/%d/%Y %I:%M %p"

class SongsApi(RequestHandler):
    def get(self):
        date = self.request.get('date')
        time = self.request.get('time')
            
        try:
            # Parse the date & time into a datetime object
            time_str = "%s %s" % (date, time)
            song_time = datetime.strptime(time_str, TIME_FORMAT)
        except ValueError, e:
            # Or just use right now
            song_time = datetime.now() + CST

        logging.info("Song time: %s" % song_time)

        # We want songs plus or minus 10 minutes from the time
        delta = timedelta(minutes=10)
        
        # Get the songs!
        songs = Song.all().order('time')
        songs.filter("time <", song_time + delta)
        songs.filter("time >", song_time - delta)
        
        # We didn't find any song
        if songs.count() == 0:
            PlaylistQueue().add(song_time.date())

        # Get simple list of objects to JSONify
        results = []
        for song in songs:
            results.append({ 
                "artist": song.artist,
                "title": song.title,
                "time": datetime.strftime(song.time, TIME_FORMAT),
            })

        self.response.out.write(simplejson.dumps(results))
    
class Playlist(RequestHandler):
    def post(self):
        logging.info("getting next queue item")
        PlaylistQueue().next()

class Index(RequestHandler):
    def get(self):
        index = memcache.get('index-template')
        index = None
        if index is None:        
            f = open('templates/index.html')
            index = f.read()
            f.close()
            #memcache.set("index-template", index)
        self.response.out.write(index)
