'use strict'

/* Create overlay for table cells that contain more than one row 
 * e. g. Vernaculars or Taxonomy
*/

var td_overlay = null;

$(document).ready( function() {
	td_overlay = new TDListOverlay();
});

class TDListOverlay {
	constructor () {
		this.addCellOpenButtons();
	}

	addCellOpenButtons() {
		let self = this;
		$('.td_list_button').each( function () {
			let row_number = $(this).data('rownum');
			let column_number = $(this).data('colnum');
			let button_id = "#td_list_button_" + column_number + '_' + row_number;
			
			//$(button_id).removeClass('display_none');
			$(button_id).off();
			$(button_id).on('click', function() {
				self.toggleOpener(row_number);
			});
		});
	}

	toggleOpener(row_number) {
		let self = this;
		$('.td_long_list_' + row_number).each( function () {
			let iupart_row = $(this);
			if (iupart_row.hasClass('y-scroll')) {
				iupart_row.removeClass('y-scroll');
				$('.td_list_button_' + row_number).attr('src', './static/buttons/close_row_fields.png');
			}
			else {
				iupart_row.addClass('y-scroll');
				$('.td_list_button_' + row_number).attr('src', './static/buttons/open_row_fields.png');
			}
		});
	}
}


