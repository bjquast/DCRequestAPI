'use strict'

class Suggestions {
	
	constructor () {
		this.suggestions = {};
		this.categories = []
		this.min_length = 3
	},
	
	
	requestSuggestions(search_term) {
		let self = this;
		
		if (search_term.length >= self.min_length) {
		
			$.ajax({
				url: "./suggestions",
				type: 'POST',
				processData: false,
				contentType: false,
				dataType: 'json',
				data: {"suggestion_search": search_term}
			})
			.fail(function (xhr, textStatus, errorThrown) {
				let error_response = xhr.responseJSON;
				console.log(error_response);
			})
			.done( function(data) {
				
				self.closeOverlay()
				self.createOverlayWindow();
				self.createBucketList();
				self.addFilterEvents();
				self.addApplyCancelEvents();
			})
		}
		
		
		
	}
	
	
	
	
}
