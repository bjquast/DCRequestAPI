'use strict'

let appliedfilters = new AppliedFiltersField();
let filteroverlay = new FilterOverlay(appliedfilters);



$(document).ready( function() {
	
	add_filter_events();
	
	set_more_button_events();
	add_collapsible_events();
	add_collapsible_status_event();
	
	appliedfilters.add_remove_filter_events();
	
	add_logout_event();
	add_submit_events();
} );


function add_submit_events() {
	$("#sort_col_selector").change( function() {
		$("#search_form").submit();
	});
	$("#sort_dir_selector").change( function() {
		$("#search_form").submit();
	});
	$("#pagesize_selector").change( function() {
		$("#search_form").submit();
	});
	$('.page_radiobutton').each( function () {
		$(this).change( function () {
			$("#search_form").submit();
		})
	});
};


function add_logout_event() {
	$("#logout_button").click( function(e) {
		$('#logout_checkbox').attr('checked', 'checked');
		$("#search_form").submit();
	});
}


function add_filter_events() {
	$('.bucket_entry').each( function () {
		$(this).click( function() {
			let filter_id = $(this).data('filter-id');
			let filter_name = $(this).data('filter-name');
			let filter_key = $(this).data('filter-key');
			let filter_value = $(this).data('filter-value');
			appliedfilters.add_filter(filter_id, filter_name, filter_key, filter_value);
		});
	});
}


function set_more_button_events() {
	$('.filter_selectors').each( function () {
		if ($(this).attr('open') == 'open') {
			let more_button = $(this).find('.more_filter_entries_button');
			more_button.click( function() {
				let agg_key = $(this).data('filter-key');
				filteroverlay.openOverlay(agg_key);
			});
		}
		else {
			$(this).find('.more_filter_entries_button').each( function () {
				$(this).off();
			});
		}
	});
}


function add_collapsible_events() {
	$('.filter_selectors').each( function () {
		$(this).on('toggle', function() {
			set_more_button_events();
		});
	});
}


function add_collapsible_status_event() {
	$('#search_form').on('submit', function () {
		$('.filter_selectors').each( function () {
			if ($(this).attr('open') == 'open') {
				$(this).children('input:checkbox').prop('checked', true);
			}
			else {
				$(this).children('input:checkbox').prop('checked', false);
			}
		});
	});
}

