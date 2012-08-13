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
		$.ajax({
			url: 'api/songs',
			type: 'GET',
			data: $('form[name=current_song]').serialize(),
			success: function(data) {
				console.log(data);
				self.clear();
				$.each(data, function(i, song){
					self.pushObject(CurrentSong.Song.create(song));
				});
			},
			error: function(jqXHR, textStatus, errorThrown) {
				console.log("Gentlemen, we have an error");
			}
		});
	}
});

// jQuery stuff
$(document).ready(function() {
	var dateField = $('input[name=date]');
	var now = moment();
	$('input[name=time]').val(now.format('h:mm A'));
	dateField.val(now.format('M/D/YYYY'));
	dateField.datepicker({ 
		maxDate: new Date(),
		dateFormat: "m/d/yy"
	});
});



