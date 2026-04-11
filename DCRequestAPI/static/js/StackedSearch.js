'use strict'

class StackedSearch {
	constructor () {
	}

	set_input_clearbuttons() {
		let self = this;
		$('.input_delete_wrapper').remove();
		$('.delete_icon').remove();
		$('input.with_clearbutton').each( function() {
			$(this).wrap('<span class="input_delete_wrapper"></span>').after($('<span class="delete_icon">x</span>').click(function() {
				$(this).prev('input').val('').trigger('change').focus();
			}));
		});
	}

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
				self.stacked_query_parms = {};
				self.update_form();
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
				self.change_input_type(query_id, field);
			});
		});
	};


	change_input_type(query_id, field) {
		/* 
		 * read the type of the field as defined in FielddConfig.py
		 * to access the data from FieldConfig.py do a jsonp request
		 * change the input fields and labels accordingly with self.set_input_field();
		*/
		let self = this;
		console.log(query_id);
		console.log(field);
		$.ajax({
			dataType: "json",
			url: "./get_field_type/" + field
		})
		.fail(function (xhr) {
			let error_response = xhr.responseJSON;
			console.log(xhr.responseJSON, );
		})
		.done( function(data) {
			console.log(data);
			let query_type = data['field_type'];
			self.set_input_field(query_id, query_type, field);
		})
	}

	set_input_field(query_id, query_type, field) {
		let self = this;
		let query_index = query_id.substring(15);
		let current_query_type = $('#' + query_id).attr('data-query-type');
		
		if (current_query_type != query_type) {
			if (query_type == 'date') {
				
				$('#' + query_id + ' label').each( function () {
					$(this).remove();
				});
				$('#' + query_id + ' input').each( function () {
					$(this).remove();
				});
				$('#' + query_id + ' .input_delete_wrapper, .delete_icon').each( function () {
					$(this).remove();
				});
				
				$('#' + query_id).prepend('<input type="date" class="width-11em with_clearbutton" name="stack_query_date_to_' + query_index +'" />');
				$('#' + query_id).prepend('<label>Date to: </label>');
				
				$('#' + query_id).prepend('<input type="date" class="width-11em with_clearbutton" name="stack_query_date_from_' + query_index +'" />');
				$('#' + query_id).prepend('<label>Date from: </label>');
				
				$('#' + query_id + ' input.with_clearbutton').each( function() {
					$(this).wrap('<span class="input_delete_wrapper"></span>').after($('<span class="delete_icon">x</span>').click(function() {
						$(this).prev('input').val('').trigger('change').focus();
					}));
				});
				
				
				$('#' + query_id).attr('data-query-type', 'date');
			}
			else if (query_type == 'term') {
				$('#' + query_id + ' label').remove();
				$('#' + query_id + ' input').remove();
				$('#' + query_id + ' .input_delete_wrapper, .delete_icon').each( function () {
					$(this).remove();
				});
				
				$('#' + query_id).prepend('<input type="text" class="width-11em with_clearbutton" value="" name="stack_query_string_' + query_index +'" />');
				$('#' + query_id + ' input').wrap('<span class="input_delete_wrapper"></span>').after($('<span class="delete_icon">x</span>').click(function() {
					$('#' + query_id + ' input').prev('input').val('').trigger('change').focus();
				}));
				
				$('#' + query_id).attr('data-query-type', 'term');
			}
		}
		
		$('#' + query_id + ' > .stack_query_field_selector').val(field);
		
		self.add_subsearch_events();
		self.add_field_selector_events();
	}
}
