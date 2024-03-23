'use strict'



class Suggestions {
	
	constructor (input_id, suggestions_list_id) {
		this.input_id = input_id;
		this.suggestions_list_id = suggestions_list_id;
		
		this.suggestions = {};
		this.categories = [];
		this.min_length = 3;
		this.suggestion_ids = [];
	}
	
	request_suggestions(search_term) {
		let self = this;
		
		let form = document.getElementById("search_form");
		let form_data = new FormData(form);
		form_data.append('suggestion_search', search_term);
		// delete the value currently in simple_search_input as they should not filter the suggestions before one is chosen and submitted
		form_data.delete('match_query');
		
		$.ajax({
			url: "./suggestions",
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
			self.suggestions = data['buckets'];
			self.categories = Object.keys(self.suggestions);
			
			self.delete_suggestions_list()
			self.fill_suggestions_list()
			
		})
	}


	add_suggestion_events() {
		let self = this;
		
		$("#" + self.input_id).off();
		
		$("#" + self.input_id).on("keyup", ( function() {
			let input_val = $(this).val();
			
			if ($(this).val().length >= self.min_length) {
				self.request_suggestions(input_val);
			}
			
			if ($(this).val().length < self.min_length) {
				self.delete_suggestions_list();
			}
			
		}));
	}


	add_suggestion_entry_handler(suggestion_id) {
		let self = this;
		
		$('#' + suggestion_id).off();
		
		$('#' + suggestion_id).click( function() {
			let suggestion = $('#' + suggestion_id).attr('data-suggestion');
			$('#' + self.input_id).val(suggestion);
			
			
			$("#search_form").submit();
		});
		
		
	}


	fill_suggestions_list() {
		let self = this;
		
		$('#' + self.suggestions_list_id).removeClass('hidden');
		
		let list = $('#' + self.suggestions_list_id + ' > ul');
		
		for (let i=0; i < self.categories.length; i++) {
			if (self.suggestions[self.categories[i]].length > 0) {
				list.append('<li id="suggestion_category_' + i + '" class="suggestion_category">' + self.categories[i] + '<ul class="ul-no-bullet"></ul></li>');
			}
			
			for (let j=0; j < self.suggestions[self.categories[i]].length; j++) {
				let suggestion = self.suggestions[self.categories[i]][j]['key'];
				let suggestion_id = "suggestion_" + i + "_" + j;
				$('#suggestion_category_' + i + ' > ul').append('<li id="' + suggestion_id + '" class="clickable">' +  suggestion + '</li>');
				$('#' + suggestion_id).attr('data-suggestion', suggestion);
				
				self.suggestion_ids.push(suggestion_id);
				self.add_suggestion_entry_handler(suggestion_id);
			}
		}
		
	}


	delete_suggestions_list() {
		let self = this;
		
		for (let i = 0; i < self.suggestion_ids.length; i++) {
			$('#' + self.suggestion_ids[i]).off();
		}
		
		$('#' + self.suggestions_list_id + ' > ul').empty();
		$('#' + self.suggestions_list_id).addClass('hidden');
	}
}
