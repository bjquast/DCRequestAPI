'use strict'


$(document).ready( function() {
	add_filter_events();
	add_remove_filter_events()
	add_submit_events();
} );


function add_submit_events() {
	$("#sort_col_selector").change( function() { 
		$("#search_form").submit();
	});
	$("#sort_dir_selector").change( function() {
		$("#search_form").submit();
	});
};


function add_filter_events() {
	$('.bucket_entry').each( function () {
		$(this).click( function() {
			let filter_id = $(this).data('filter-id');
			let filter_name = $(this).data('filter-name');
			let filter_key = $(this).data('filter-key');
			let filter_value = $(this).data('filter-value');
			add_filter(filter_id, filter_name, filter_key, filter_value);
		});
	});
}


function add_filter(filter_id, filter_name, filter_key, filter_value) {
	//console.log(filter_id);
	
	let filter_exists = false;
	
	$('.filter_checkbox').each( function () {
		console.log(filter_id, $(this).data('filter-id'));
		if (filter_id == $(this).data('filter-id')) {
			filter_exists = true;
		}
	});
	
	if (filter_exists == false) {
		$('#applied_filters').append('<span class="filter_checkbox new_filter"></span>');
		$('#applied_filters>span.new_filter').attr('data-filter-id', filter_id);
		$('#applied_filters>span.new_filter').append('<label><b>' + filter_name + ': </b>' + filter_value + '</label>');
		$('#applied_filters>span.new_filter').append('<input type="checkbox" checked="checked" value="' + filter_key + ':' + filter_value + '" name="term_filters">');
		$('#applied_filters>span.new_filter>input').attr('data-filter-id', filter_id);
		$('#applied_filters>span.new_filter').removeClass('new_filter');
		
		// only submit when the filter was not set before
		$("#search_form").submit();
	}
}


function add_remove_filter_events() {
	$('#applied_filters .filter_checkbox>input').each( function () {
		$(this).change( function() {
			let filter_id = $(this).data('filter-id');
			remove_filter(filter_id);
		});
	});
}


function remove_filter(filter_id) {
	$('#applied_filters .filter_checkbox').each( function () {
		if ($(this).data('filter-id') == filter_id) {
			$(this).remove();
		}
	});
	
	
	$("#search_form").submit();
}

