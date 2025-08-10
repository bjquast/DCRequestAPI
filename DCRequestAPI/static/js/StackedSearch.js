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
	};
	
	
	add_field_selector_events() {
		let self = this;
		$('.stack_query_field_selector').each( function () {
			$(this).off();
			$(this).on('change', function () {
				
				let query_id = $(this).parent().attr('id');
				let field = $(this).prop('selected', true).val();
				self.set_query_type(query_id, field);
			});
		});
	};
	
	set_query_type(query_id, field) {
		let self = this;
		console.log(query_id);
		console.log(field);
		$.ajax({
			dataType: "json",
			url: "./get_field_type/" + field
		})
		.fail(function (xhr, textStatus, errorThrown) {
			let error_response = xhr.responseJSON;
			console.log(error_response);
		})
		.done( function(data) {
			console.log(data);
			self.query_type = data['field_type'];
			
		})
	}
	
	set_input_field(query_id) {
		let self = this;
		let query_count_string = query_id.substring(16);
		let current_query_type = $('#' + query_id).data('query-type');
		if (current_query_type != self.query_type) {
			if (self.query_type == 'date') {
				$('#' + query_id + ' > input[type=text]').each( function () {
					$(this).remove();
					$(this).append('<label>Date from: </label>');
					$(this).append('<input type="date" class="width-8em with_clearbutton" name="stack_query_dates_from_' + query_count_string +'" />');
					$(this).append('<label>Date to: </label>');
					$(this).append('<input type="date" class="width-8em with_clearbutton" name="stack_query_dates_to_' + query_count_string +'" />');
				});
			}
			else if (self.query_type == 'term') {
				$('#' + query_id + ' > input[type=date]').each( function () {
					$(this).remove();
					$(this).append('<input type="text" class="width-8em with_clearbutton" value="" name="stack_query_terms_' + query_count_string +'" />');
				});
			}
		}
		
	}
}
