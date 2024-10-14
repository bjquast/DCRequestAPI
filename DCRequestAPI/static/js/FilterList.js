'use strict' 

class FilterList {
	constructor (filter_list_id) {
		this.filter_list_id = filter_list_id;
		this.filter_list_details = $('#' + this.filter_list_id);
		this.filter_key = $('#' + this.filter_list_id).data('filter-key');
		console.log('---------', this.filter_list_details);
		console.log('---------', this.filter_list_id);
		console.log('---------', this.filter_key);
		console.log('FilterList called');
	}


	createFilterList() {
		let self = this;
		
		$('#' + self.filter_list_id).append('<ul>');
		let unordered_list = $('#' + self.filter_list_id + ' ul');
		console.log('##############', unordered_list);
		unordered_list.addClass('ul-no-bullet');
		
		for (let i = 0; i < self.buckets['buckets'].length; i++) {
			let list_entry = $('<li></li>');
			unordered_list.append(list_entry);
			
			list_entry.addClass('bucket_entry clickable');
			list_entry.html(self.buckets['buckets'][i][0] + ' (' + self.buckets['buckets'][i][1] + ')');
			list_entry.attr('data-filter-id', 'filter_' + self.buckets['aggregation'] + '_' + self.buckets['buckets'][i][0]);
			list_entry.attr('data-filter-key', self.buckets['aggregation']);
			list_entry.attr('data-filter-value', self.buckets['buckets'][i][0]);
			if (self.buckets['aggregation_names']['en']) {
				list_entry.attr('data-filter-name', self.buckets['aggregation_names']['en']);
			}
			else {
				list_entry.attr('data-filter-name', self.buckets['aggregation']);
			}
		}
		let button_list_entry = $('<li></li>');
		unordered_list.append(button_list_entry);
		let more_button = $('<button>more options</button>');
		button_list_entry.append(more_button);
		more_button.addClass('more_filter_entries_button');
		more_button.attr('id', 'more_button_' + self.buckets['aggregation']);
		more_button.attr('data-filter-key', self.buckets['aggregation']);
	}


	readSearchFormParameters() {
		let self = this;
		let form = document.getElementById("search_form");
		self.form_data = new FormData(form);
	}


	requestBuckets() {
		let self = this;
		
		self.buckets = [];
		
		self.readSearchFormParameters();
		self.form_data.append('aggregation', self.filter_key);
		self.form_data.append('buckets_size', 10);
		
		$.ajax({
			url: "./aggregation",
			type: 'POST',
			processData: false,
			contentType: false,
			dataType: 'json',
			data: self.form_data
		})
		.fail(function (xhr, textStatus, errorThrown) {
			let error_response = xhr.responseJSON;
			console.log(error_response);
		})
		.done( function(data) {
			self.buckets = data;
			console.log('got them');
			console.log(self.buckets);
			self.createFilterList();
		});
	}
}

