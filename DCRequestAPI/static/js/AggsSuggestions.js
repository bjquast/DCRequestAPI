'use strict'



class AggsSuggestions {
	
	constructor (appliedfilters, input_id, suggestions_list_id) {
		this.appliedfilters = appliedfilters;
		this.input_id = input_id;
		this.suggestions_list_id = suggestions_list_id;
		
		this.suggestions = {};
		this.filter_keys = [];
		this.min_length = 3;
		this.suggestion_ids = [];
		this.timeout = null;
		this.progress_animation = null;
		
		this.current_search_term = '';
	}
	
	request_suggestions() {
		let self = this;
		
		$("#" + self.input_id).off();
		
		let form = document.getElementById("search_form");
		let form_data = new FormData(form);
		form_data.append('buckets_search_term', self.search_term);
		
		$.ajax({
			url: "./aggs_suggestions",
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
			self.filter_keys = Object.keys(self.suggestions);
			
			self.delete_suggestions_list();
			self.fill_suggestions_list();
		})
		.always( function () {
			self.remove_progress_animation();
			// check if search_term has been changed during request
			// if so send the next request with the new search term
			
			self.search_term = $("#" + self.input_id).val();
			if (self.search_term != self.current_search_term) {
				self.handle_input_change();
			}
			else {
				self.add_suggestion_events();
			}
		})
	}


	handle_input_change() {
		let self = this;
		
		if (self.search_term.length >= self.min_length) {
			self.set_progress_animation();
			clearTimeout(self.timeout);
			
			self.timeout = setTimeout( function() {
				self.current_search_term = self.search_term;
				self.request_suggestions();
			}
			, 200);
		}
		
		if (self.search_term.length < self.min_length) {
			
			//self.unblock_suggest_input();
			clearTimeout(self.timeout);
			self.timeout = setTimeout( function() {
				self.remove_progress_animation();
				self.delete_suggestions_list();
			}
			, 200);
		}
		self.add_suggestion_events();
	}


	add_suggestion_events() {
		let self = this;
		
		$("#" + self.input_id).off();
		
		$("#" + self.input_id).on("keyup", ( function() {
			self.search_term = $("#" + self.input_id).val();
			self.search_term = $(this).val();
			self.handle_input_change();
		}));
	}


	set_progress_animation() {
		let self = this;
		
		if (self.progress_animation === null) {
			$('#' + self.suggestions_list_id).removeClass('hidden');
			$('#' + self.suggestions_list_id).prepend('<progress id="progress_animation" aria-label="Content loading…"></progress>');
			self.progress_animation = $('#progress_animation');
		}
	}


	remove_progress_animation() {
		let self = this;
		
		$('#progress_animation').remove();
		self.progress_animation = null;
	}


	add_filter_entry_handler(suggestion_id) {
		let self = this;
		
		$('#' + suggestion_id).off();
		
		$('#' + suggestion_id).click( function() {
			let filter_id = $('#' + suggestion_id).attr('data-filter-id');
			let filter_name = $('#' + suggestion_id).attr('data-filter-name');
			let filter_key = $('#' + suggestion_id).attr('data-filter-key');
			let filter_value = $('#' + suggestion_id).attr('data-filter-value');
			
			$('#' + self.input_id).val(filter_value);
			
			$('input:checkbox[name="open_filter_selectors"][value="' + filter_key + '"]').prop('checked', true);
			
			self.appliedfilters.add_filter(filter_id, filter_name, filter_key, filter_value);
		});
	}


	fill_suggestions_list() {
		let self = this;
		
		$('#' + self.suggestions_list_id).removeClass('hidden');
		
		let list = $('#' + self.suggestions_list_id + ' > ul');
		
		for (let i=0; i < self.filter_keys.length; i++) {
			if (self.suggestions[self.filter_keys[i]]['buckets'].length > 0) {
				let category_name = self.suggestions[self.filter_keys[i]]['names']['en'];
				list.append('<li id="suggestion_category_' + i + '" class="suggestion_category">' + category_name + '<ul class="ul-no-bullet"></ul></li>');
				
				for (let j=0; j < self.suggestions[self.filter_keys[i]]['buckets'].length; j++) {
					let suggestion = self.suggestions[self.filter_keys[i]]['buckets'][j]['key'];
					let suggestion_id = "suggestion_" + i + "_" + j;
					$('#suggestion_category_' + i + ' > ul').append('<li id="' + suggestion_id + '" class="clickable">' +  suggestion + '</li>');
					$('#' + suggestion_id).attr('data-filter-value', suggestion);
					$('#' + suggestion_id).attr('data-filter-key', self.filter_keys[i]);
					$('#' + suggestion_id).attr('data-filter-name', category_name);
					$('#' + suggestion_id).attr('data-filter-id', 'filter_' + self.filter_keys[i] + '_' + suggestion);
					
					self.suggestion_ids.push(suggestion_id);
					self.add_filter_entry_handler(suggestion_id);
				}
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
