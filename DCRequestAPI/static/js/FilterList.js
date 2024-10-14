'use strict' 

class FilterList {
	constructor (filter_list_id) {
		this.filter_list_id = filter_list_id;
		this.list_header = $('#' + self.filter_list_id);
		this.filter_key = details_element.data('filter-key');
	}


	fillFilterList() {
		let self = this;
		
	}


	requestBuckets() {
		let self = this;
		self.buckets = [];
		
		self.form_data.append('aggregation', self.filter_key);
		
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
		})
	}

	addFilterListEvents() {
		let self = this;
		$('#available_filters .filter_selectors').each( function () {
			$(this).off();
			$(this).click( function() {
				let filter_list_id = $(this).prop('id');
				
				
				
				if (filter_exists == false) {
					self.selected_filters.push({
						'filter_id': $(this).data('filter-id'),
						'filter_name': $(this).data('filter-name'),
						'filter_key': $(this).data('filter-key'),
						'filter_value': $(this).data('filter-value')
					});
					self.add2SelectedList($(this).data('filter-value'));
				}
			});
		});
	}
