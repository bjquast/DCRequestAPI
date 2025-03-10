'use strict'

const appliedfilters = new AppliedFiltersField();
const filterlists = new FilterLists(appliedfilters);
const hierarchylists = new HierarchyLists(appliedfilters);
const bucketsoverlay = new BucketsOverlay(appliedfilters);
const aggs_suggestions = new AggsSuggestions(appliedfilters, "aggs_search_input", "aggs_search_suggestions_list");
const stacked_search = new StackedSearch();
// load the overlay when the page is loading
const loading_overlay = new LoadingOverlay();


$(document).ready( function() {
	stacked_search.add_subsearch_events();
	
	filterlists.add_filter_events();
	filterlists.set_more_button_events();
	filterlists.add_collapsible_filters_events();
	
	
	hierarchylists.add_collapsible_hierarchies_events();
	
	add_column_selector_event();
	add_columnheader_sorting_events();
	add_filter_sections_selector_event();
	
	aggs_suggestions.add_suggestion_events();
	appliedfilters.add_remove_filter_events();
	
	set_input_clearbuttons();
	
	add_users_projects_restriction_event();
	
	add_logout_event();
	add_submit_events();
	
	loading_overlay.remove_loading_overlay();
	loading_overlay.add_loading_overlay_event();
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

function set_input_clearbuttons() {
	$('.input_delete_wrapper').remove();
	$('.delete_icon').remove();
	$('input.with_clearbutton').each( function() {
		
		$(this).wrap('<span class="input_delete_wrapper"></span>').after($('<span class="delete_icon">x</span>').click(function() {
			$(this).prev('input').val('').trigger('change').focus();
		}));
	});
}


function add_column_selector_event() {
	$('#column_preferences').on('toggle', function() {
		if (!$(this).attr('open')) {
			$("#search_form").submit();
		}
	})
}

function add_filter_sections_selector_event() {
	$('#filter_preferences').on('toggle', function() {
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


