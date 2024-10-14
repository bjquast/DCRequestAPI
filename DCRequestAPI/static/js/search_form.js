'use strict'

const appliedfilters = new AppliedFiltersField();
const bucketsoverlay = new BucketsOverlay(appliedfilters);
const aggs_suggestions = new AggsSuggestions(appliedfilters, "aggs_search_input", "aggs_search_suggestions_list");
const stacked_search = new StackedSearch();



$(document).ready( function() {
	
	add_filter_events();
	
	set_more_button_events();
	add_collapsible_filters_events();
	add_column_selector_event();
	add_columnheader_sorting_events();
	
	add_match_query_events();
	
	aggs_suggestions.add_suggestion_events();
	appliedfilters.add_remove_filter_events();
	stacked_search.add_subsearch_events();
	
	add_users_projects_restriction_event();
	
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


function add_columnheader_sorting_events() {
	$('.column_sort_selector').each( function () {
		$(this).click( function() {
			let sorting_col = $(this).attr('data-columnkey');
			let sorting_dir = $(this).attr('data-sorting_dir');
			
			if (sorting_dir == 'asc') {
				sorting_dir = 'desc';
				$(this).attr('data-sorting_dir', 'desc');
			}
			else {
				sorting_dir = 'asc';
				$(this).attr('data-sorting_dir', 'asc');
			}
			
			$("#sort_col_selector").val(sorting_col);
			$("#sort_dir_selector").val(sorting_dir);
			
			$("#search_form").submit();
		});
	});
}


function add_logout_event() {
	$("#logout_button").click( function(e) {
		$('#logout_checkbox').attr('checked', 'checked');
		$("#search_form").submit();
	});
}


function add_filter_events() {
	$('.bucket_entry').each( function () {
		$(this).off();
		$(this).click( function() {
			let filter_id = $(this).data('filter-id');
			let filter_name = $(this).data('filter-name');
			let filter_key = $(this).data('filter-key');
			let filter_value = $(this).data('filter-value');
			appliedfilters.add_filter(filter_id, filter_name, filter_key, filter_value);
		});
	});
	
	$('#term_filters_connector').off();
	$('#term_filters_connector').change( function () {
		$("#search_form").submit();
	});
	
}


function set_more_button_events() {
	$('.filter_selectors').each( function () {
		if ($(this).attr('open') == 'open') {
			let more_button = $(this).find('.more_filter_entries_button');
			more_button.click( function() {
				let agg_key = $(this).data('filter-key');
				bucketsoverlay.openOverlay(agg_key);
			});
		}
		else {
			$(this).find('.more_filter_entries_button').each( function () {
				$(this).off();
			});
		}
	});
}


function add_match_query_events() {
	$('.match_query_checkbox').each( function () {
		$(this).off();
		
		$(this).change( function () {
			if (!$(this).prop('checked')) {
				$("#search_form").submit();
			}
		});
	});
}


function add_collapsible_filters_events() {
	$('.filter_selectors').each( function () {
		$(this).on('toggle', function() {
			set_more_button_events();
			if ($(this).attr('open') == 'open') {
				$(this).children('input:checkbox').prop('checked', true);
				let filter_list_id = $(this).prop('id');
				
				updateFilterList(filter_list_id);
				
				//let filterlist = new FilterList(filter_list_id);
				//filterlist.requestBuckets();
				//set_more_button_events();
			}
			else {
				$(this).children('input:checkbox').prop('checked', false);
				$(this).find('ul').remove();
				console.log('removed');
			}
		});
	});
}


//////////////////////////////////////////////////

function readSearchFormParameters() {
	let form = document.getElementById("search_form");
	let form_data = new FormData(form);
	return form_data
}


function createFilterList(filter_list_id, buckets) {
	
	$('#' + filter_list_id).append('<ul>');
	let unordered_list = $('#' + filter_list_id + ' ul');
	console.log('##############', unordered_list);
	unordered_list.addClass('ul-no-bullet');
	
	for (let i = 0; i < buckets['buckets'].length; i++) {
		let list_entry = $('<li></li>');
		unordered_list.append(list_entry);
		
		list_entry.addClass('bucket_entry clickable');
		list_entry.html(buckets['buckets'][i][0] + ' (' + buckets['buckets'][i][1] + ')');
		list_entry.attr('data-filter-id', 'filter_' + buckets['aggregation'] + '_' + buckets['buckets'][i][0]);
		list_entry.attr('data-filter-key', buckets['aggregation']);
		list_entry.attr('data-filter-value', buckets['buckets'][i][0]);
		if (buckets['aggregation_names']['en']) {
			list_entry.attr('data-filter-name', buckets['aggregation_names']['en']);
		}
		else {
			list_entry.attr('data-filter-name', buckets['aggregation']);
		}
	}
	let button_list_entry = $('<li></li>');
	unordered_list.append(button_list_entry);
	let more_button = $('<button>more options</button>');
	button_list_entry.append(more_button);
	more_button.addClass('more_filter_entries_button');
	more_button.attr('id', 'more_button_' + buckets['aggregation']);
	more_button.attr('data-filter-key', buckets['aggregation']);
}


function updateFilterList(filter_list_id) {
	let buckets = [];
	let filter_key = filter_list_id.substring(12,);
	
	console.log('---------', filter_list_id);
	console.log('---------', filter_key);
	
	let form_data = readSearchFormParameters();
	
	console.log(form_data);
	
	form_data.append('aggregation', filter_key);
	form_data.append('buckets_size', 10);
	
	console.log(form_data);
	
	$.ajax({
		url: "./aggregation",
		type: 'POST',
		processData: false,
		contentType: false,
		dataType: 'json',
		data: form_data
	})
	.fail(function (xhr, textStatus, errorThrown) {
		let error_response = xhr.responseJSON;
		console.log(error_response);
	})
	.done( function(data) {
		buckets = data;
		console.log('got them');
		console.log(buckets);
		createFilterList(filter_list_id, buckets);
		add_filter_events();
		set_more_button_events();
	});
}

//////////////////////////////////////////////////////////


function add_column_selector_event() {
	$('#column_preferences').on('toggle', function() {
		if (!$(this).attr('open')) {
			$("#search_form").submit();
		}
	})
}

function add_users_projects_restriction_event() {
	$('#restrict_users_projects_checkbox').change( function () {
		console.log($(this));
		$("#search_form").submit();
	});
}
