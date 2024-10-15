'use strict' 

class FilterLists {

	constructor (applied_filters) {
		this.appliedfilters = appliedfilters;
	}


	add_collapsible_filters_events() {
		let self = this;
		$('.filter_selectors').each( function () {
			$(this).on('toggle', function() {
				if ($(this).attr('open') == 'open') {
					$(this).children('input:checkbox').prop('checked', true);
					if ($(this).find('ul').length == 0) {
						let filter_list_id = $(this).prop('id');
						filter_list_id = filter_list_id.replace(/\./g, '\\.');
						self.updateFilterList(filter_list_id);
					}
				}
				else {
					$(this).children('input:checkbox').prop('checked', false);
					$(this).find('ul').remove();
				}
			});
		});
	}


	set_more_button_events() {
		let self = this;
		
		$('.filter_selectors').each( function () {
			if ($(this).attr('open') == 'open') {
				let more_button = $(this).find('.more_filter_entries_button');
				more_button.click( function() {
					let agg_key = $(this).data('filter-key');
					bucketsoverlay.openOverlay(agg_key);
				});
			}
			else {
				$(this).find('.more_filter_entries_button').each( function () {
					$(this).off();
				});
			}
		});
	}


	add_filter_events() {
		let self = this;
		$('.bucket_entry').each( function () {
			$(this).off();
			$(this).click( function() {
				let filter_id = $(this).data('filter-id');
				let filter_name = $(this).data('filter-name');
				let filter_key = $(this).data('filter-key');
				let filter_value = $(this).data('filter-value');
				self.appliedfilters.add_filter(filter_id, filter_name, filter_key, filter_value);
			});
		});
		
		$('#term_filters_connector').off();
		$('#term_filters_connector').change( function () {
			$("#search_form").submit();
		});
		
	}


	readSearchFormParameters() {
		let self = this;
		let form = document.getElementById("search_form");
		self.form_data = new FormData(form);
	}


	createFilterList(filter_list_id, buckets) {
		let self = this;
		
		$('#' + filter_list_id).append('<ul>');
		let unordered_list = $('#' + filter_list_id + ' ul');
		unordered_list.addClass('ul-no-bullet');
		
		for (let i = 0; i < buckets['buckets'].length; i++) {
			let list_entry = $('<li></li>');
			unordered_list.append(list_entry);
			
			list_entry.addClass('bucket_entry clickable');
			list_entry.html(buckets['buckets'][i][0] + ' (' + buckets['buckets'][i][1] + ')');
			list_entry.attr('data-filter-id', 'filter_' + buckets['aggregation'] + '_' + buckets['buckets'][i][0]);
			list_entry.attr('data-filter-key', buckets['aggregation']);
			list_entry.attr('data-filter-value', buckets['buckets'][i][0]);
			if (buckets['aggregation_names']['en']) {
				list_entry.attr('data-filter-name', buckets['aggregation_names']['en']);
			}
			else {
				list_entry.attr('data-filter-name', buckets['aggregation']);
			}
		}
		let button_list_entry = $('<li></li>');
		unordered_list.append(button_list_entry);
		let more_button = $('<button>more options</button>');
		button_list_entry.append(more_button);
		more_button.addClass('more_filter_entries_button');
		more_button.attr('id', 'more_button_' + buckets['aggregation']);
		more_button.attr('data-filter-key', buckets['aggregation']);
	}


	updateFilterList(filter_list_id) {
		let self = this;
		
		let buckets = [];
		let filter_key = $('#' + filter_list_id).attr('data-filter-key');
		self.readSearchFormParameters();
		
		self.form_data.append('aggregation', filter_key);
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
			buckets = data;
			self.createFilterList(filter_list_id, buckets);
			self.add_filter_events();
			self.set_more_button_events();
		});
	}
}

