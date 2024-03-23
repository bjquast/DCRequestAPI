'use strict'



class Suggestions {
	
	constructor (input_id, suggestions_list_id) {
		this.input_id = input_id;
		this.suggestions_list_id = suggestions_list_id;
		
		this.suggestions = {};
		this.categories = []
		this.min_length = 3
	}
	
	request_suggestions(search_term) {
		let self = this;
		
		let form = document.getElementById("search_form");
		let form_data = new FormData(form);
		form_data.append('suggestion_search', search_term);
		
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
		
		$("#" + self.input_id).on("keyup", ( function() {
			let input_val = $(this).val();
			
			if ($(this).val().length >= self.min_length) {
				self.request_suggestions(input_val);
			}
			
			if ($(this).val().length < self.min_length) {
				self.delete_suggestions_list();
			}
			
		}));
		
		
		/*
		$("#" + self.input_id).change( function() {
			$("#search_form").submit();
		});
		*/
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
				
				$('#suggestion_category_' + i + ' > ul').append('<li>' +  suggestion + '</li>');
			}
		}
		
	}


	delete_suggestions_list() {
		let self = this;
		
		$('#' + self.suggestions_list_id + ' > ul').empty();
		$('#' + self.suggestions_list_id).addClass('hidden');
	}
}
