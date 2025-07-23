'use strict'

// load the overlay when the page is loading


class LoadingOverlay {
	constructor () {
		this.add_loading_overlay();
	}
	
	add_loading_overlay_event() {
		let self = this;

		// i haven't find a way to get the submitter when using a jquery submit event
		document.addEventListener('submit',function(e){
			let submitter_name = e.submitter['name'];
			if (submitter_name != 'file download') {
				self.add_loading_overlay();
			}
		});
	}
	
	add_loading_overlay() {
		$('html').append('<div id="loading_overlay"><div id="loading_overlay_image"></div></div>');
	}

	remove_loading_overlay() {
		$('#loading_overlay').remove();
	}
}
