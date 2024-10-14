'use strict'

const appliedfilters = new AppliedFiltersField();
const bucketsoverlay = new BucketsOverlay(appliedfilters);
//const filterlists = new FilterList();
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
				filterlist = new FilterList(filter_list_id);
			}
			else {
				$(this).children('input:checkbox').prop('checked', false);
				$(this).children('ul').remove();
			}
		});
	});
}


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
