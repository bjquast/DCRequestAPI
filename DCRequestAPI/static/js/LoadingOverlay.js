'use strict'

// load the overlay when the page is loading


class LoadingOverlay {
	constructor () {
		this.add_loading_overlay();
	}
	
	add_loading_overlay_event() {
		let self = this;
		$("#search_form").on ( 'submit',
			function(e) {
				//self.add_loading_overlay();
			}
		);
	}
	
	add_loading_overlay() {
		$('html').append('<div id="loading_overlay"><div id="loading_overlay_image"></div></div>');
	}

	remove_loading_overlay() {
		$('#loading_overlay').remove();
	}
}
