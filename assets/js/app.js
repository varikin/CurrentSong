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
	content: [],
	loadSongs: function(){
		var self = this;
		$.getJSON('api/songs', function(data) {
			self.clear();
			data.forEach(function(item){
				self.pushObject(CurrentSong.Song.create(item));
			});
		});
	}
});

// jQuery stuff
$(document).ready(function() {
	$('input[name=date]').datepicker({ maxDate: new Date() });
});



