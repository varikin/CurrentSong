Ember.LOG_BINDINGS = true;

// Current Song EmberJS application
var CurrentSong = Ember.Application.create();

// Song data model for Current Song
CurrentSong.Song = Ember.Object.extend({
	title: null,
	time: null,
	artist: null
});

// Song Controller for the Current Song
CurrentSong.songsController  = Ember.ArrayController.create({
	content: [
		CurrentSong.Song.create({'title': 'a title', 'time': 'a time', 'artist': "an artist"}),
		CurrentSong.Song.create({'title': 'a title', 'time': 'a time', 'artist': "an artist"}),
		CurrentSong.Song.create({'title': 'a title', 'time': 'a time', 'artist': "an artist"})
	],
	loadSongs: function(){
		var self = this;
		// $.getJSON('api/songs', function(data) {
		// 	self.clear();
		// 	data.forEach(function(item){
		// 		self.pushObject(CurrentSong.Song.create(item));
		// 	});
		// });
	}
});


