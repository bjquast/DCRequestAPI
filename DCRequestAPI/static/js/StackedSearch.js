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

	update_form() {
		let self = this
		let form = document.getElementById("search_form");
		let formdata= new FormData(form);
		
		$.ajax({
			url: "./stacked_queries_form",
			type: 'POST',
			processData: false,
			contentType: false,
			data: formdata
		})
		.fail(function (xhr, textStatus, errorThrown) {
			console.log(textStatus, errorThrown);
		})
		.done( function(data) {
			self.update_stacked_queries(data);
		})
	}

	update_stacked_queries(data) {
		let self = this;
		$('#stacked_queries_macro').empty();
		$('#stacked_queries_macro').append(data);
		self.add_subsearch_events();
		self.add_field_selector_events();
		self.set_input_clearbuttons();
	}
}
