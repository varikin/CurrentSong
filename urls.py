from google.appengine.ext.webapp import WSGIApplication
from google.appengine.ext.webapp.util import run_wsgi_app

from handlers import SongsApi, Index, Playlist
    
if __name__ == '__main__':
    run_wsgi_app(WSGIApplication([
        ('/', Index),
        ('/tasks/playlist', Playlist),
        ('/api/songs', SongsApi),
    ]))
