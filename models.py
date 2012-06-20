from google.appengine.ext import db

class Song(db.Model):
    title = db.StringProperty(required=True)
    artist = db.StringProperty(required=True)
    time = db.DateTimeProperty(required=True)
    
    def __init__(self, *args, **kwargs):
        song_time = kwargs['time']
        kwargs['key_name'] = str(song_time)
        super(Song, self).__init__(*args, **kwargs)  

    def __str__(self):
        return unicode(self)

    def __unicode__(self):
        return '%s by %s at %s' % (self.title, self.artist, \
                self.time.strftime("%I:%M %p %m/%d/%Y"))

    def __repr__(self):
        return unicode(self)

