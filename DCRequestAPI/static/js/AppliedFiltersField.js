'use strict'

class AppliedFiltersField {

	add_filter(filter_id, filter_name, filter_key, filter_value, auto_submit) {
		let self = this;
		if (auto_submit == undefined) {
			auto_submit = true;
		}
		let filter_exists = false;
		
		$('.filter_checkbox').each( function () {
			if (filter_id == $(this).data('filter-id')) {
				filter_exists = true;
			}
		});
		
		// add filter only when it was not added before
		if (filter_exists == false) {
			$('#applied_filters').append('<div class="filter_checkbox new_filter"></div>');
			$('#applied_filters .new_filter').attr('data-filter-id', filter_id);
			$('#applied_filters .new_filter').append('<input type="checkbox" form="search_form" checked="checked" value="' + filter_key + ':' + filter_value + '" name="term_filters">');
			$('#applied_filters .new_filter>input').attr('data-filter-id', filter_id);
			$('#applied_filters .new_filter').append('<label><b>' + filter_name + ': </b>' + filter_value + '</label>');
			$('#applied_filters .new_filter').removeClass('new_filter');
			
			if (auto_submit == true) {
				$("#search_form").submit();
			}
		}
	}


	add_remove_filter_events() {
		let self = this;
		
		$('#applied_filters .filter_checkbox>input').each( function () {
			$(this).change( function() {
				let filter_id = $(this).data('filter-id');
				self.remove_filter(filter_id);
			});
		});
	}


	remove_filter(filter_id) {
		let self = this;
		
		$('#applied_filters .filter_checkbox').each( function () {
			if ($(this).data('filter-id') == filter_id) {
				$(this).remove();
			}
		});
		
		$("#search_form").submit();
	}

}
