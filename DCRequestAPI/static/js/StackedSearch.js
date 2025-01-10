'use strict'

class StackedSearch {
	
	add_subsearch_events() {
		let self = this;
		$('.add_subsearch_label').each( function () {
			$(this).off();
			$(this).click( function () {
				let i = $(this).attr('data-stacked-query-num');
				$('#stack_search_add_subquery_' + i).attr('checked', 'checked');
				$("#search_form").submit();
			});
		});
		
		// hide the .delete_subsearch_label labels when using javascript
		// because the input field can be cleared with input_clearbutton
		// deactivated in stacked_queries macro now
		/*
		$('.delete_subsearch_label').each( function () {
			$(this).addClass('hidden');
		});
		*/
		
		/*
		$('.delete_subsearch_label').each( function () {
			$(this).off();
			$(this).click( function () {
				let i = $(this).attr('data-stacked-query-num');
				$('#stack_search_delete_subquery_' + i).attr('checked', 'checked');
				$("#search_form").submit();
			});
		});
		*/
	}
	
	/*
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
	* */
}
