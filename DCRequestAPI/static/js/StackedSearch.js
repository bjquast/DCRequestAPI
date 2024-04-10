'use strict'

class StackedSearch {
	
	add_toggle_subsearch_events() {
		let self = this;
		$('.toggle_subsearch').each( function () {
			$(this).off();
			$(this).click( function () {
				let stacked_query_num = $(this).attr('data-stacked-query-num');
				self.toggle_visibility(stacked_query_num);
			})
		});
		
	}


	toggle_visibility(stacked_query_num) {
		let sub_search_field = $('#stacked_query_subsearch_' + stacked_query_num);
		if (sub_search_field) {
			if (sub_search_field.hasClass('hidden')) {
				sub_search_field.removeClass('hidden');
			}
			else {
				sub_search_field.addClass('hidden');
			}
		}
		
	}
}
