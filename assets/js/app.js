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


CurrentSong.getParams = function() {
	var query = window.location.search.substring(1);
	var params = {};
	var pairs = query.split("&");
	if (pairs.length === 1 && pairs[0] === '') {
		return params; // bug out early
	}
	var paramRegex = /(.+)=(.*)/;
	for (var i = 0; i < pairs.length; i++) {
		var param = paramRegex.exec(pairs[i]);
		if (param !== null) {
			params[param[1]] = decodeURIComponent(param[2]);	
		}
	}
	return params;
};


// jQuery stuff
$(document).ready(function() {
	var params = CurrentSong.getParams();
	var date = params['date'];
	var time = params['time'];
	if (date === undefined || date === '') {
		date = moment().format('M/D/YYYY');
	}
	if (time === undefined || time === '') {
		time = moment().format('h:mm A');
	}

	$('input[name=time]').val(time);
	$('input[name=date]').val(date).datepicker({ 
		maxDate: new Date(),
		dateFormat: "m/d/yy"
	});
});





