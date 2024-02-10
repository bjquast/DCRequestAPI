'use strict'

class BucketsOverlay {
	constructor (applied_filters_field) {
		this.applied_filters_field = applied_filters_field;
		this.agg_key = '';
	}


	readFormParameter() {
		let self = this;
		let form = document.getElementById("search_form");
		self.form_data = new FormData(form);
	}

	requestBuckets() {
		let self = this;
		self.buckets = [];
		
		self.form_data.append('aggregation', self.agg_key);
		
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
			self.closeOverlay()
			self.createOverlayWindow();
			self.createBucketList();
			self.addFilterEvents();
			self.addApplyCancelEvents();
		})
	}


	openOverlay(agg_key) {
		let self = this;
		self.agg_key = agg_key;
		self.selected_filters = [];
		self.readFormParameter();
		self.requestBuckets();
	}


	createOverlayWindow() {
		let self = this;
		$('#buckets-overlay-slot').append('<div id="buckets-overlay" class="buckets-overlay"></div>');
		$('#buckets-overlay').append('<div id="buckets-overlay-header"></div>');
		$('#buckets-overlay-header').append('<div id="buckets-overlay-headline"></div>');
		
		if (self.buckets['aggregation_names']['en']) {
			$('#buckets-overlay-headline').append('<div><label>' + self.buckets['aggregation_names']['en'] + '</label></div>');
		}
		else {
			$('#buckets-overlay-headline').append('<div><label>' + self.buckets['aggregation'] + '</label></div>');
		}
		
		$('#buckets-overlay-headline').append('<div class="buttons-right-position"></div>');
		$('#buckets-overlay-headline .buttons-right-position').append('<button id="buckets-overlay-cancel-button">cancel</button>');
		$('#buckets-overlay-headline .buttons-right-position').append('<button id="buckets-overlay-apply-button">apply</button>');
		
		$('#buckets-overlay-header').append('<div id="buckets-overlay-selected-div"></div>');
		$('#buckets-overlay-selected-div').append('<ul id="buckets-overlay-selected-list"></ul>');
		
		$('#buckets-overlay').append('<div id="buckets-list"></div>');
	}


	createBucketList() {
		let self = this;
		$('#buckets-list').append('<ul></ul>');
		
		for (let i = 0; i < self.buckets['buckets'].length; i++) {
			let bucket_id = 'bucket_entry_' + i;
			let bucket_value = self.buckets['buckets'][i][0] + ' (' + self.buckets['buckets'][i][1] + ')';
			
			$('#buckets-list ul').append('<li id="' + bucket_id + '" class="bucket_entry">' + bucket_value + '</li>');
			$('#' + bucket_id).attr('data-filter-id', 'filter_' + self.buckets['aggregation'] + '_' + self.buckets['buckets'][i][0]);
			$('#' + bucket_id).attr('data-filter-key', self.buckets['aggregation']);
			$('#' + bucket_id).attr('data-filter-value', self.buckets['buckets'][i][0]);
			if (self.buckets['aggregation_names']['en']) {
				$('#' + bucket_id).attr('data-filter-name', self.buckets['aggregation_names']['en']);
			}
			else {
				$('#' + bucket_id).attr('data-filter-name', self.buckets['aggregation']);
			}
		}
	}

	closeOverlay() {
		let self = this;
		$('#buckets-overlay-slot').empty();
	}

	addFilterEvents() {
		let self = this;
		$('#buckets-overlay .bucket_entry').each( function () {
			$(this).click( function() {
				let filter_exists = false;
				for (let i = 0; i < self.selected_filters.length; i++) {
					if (self.selected_filters[i]['filter_id'] == $(this).data('filter-id')) {
						filter_exists = true;
					}
				}
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

	submitSelectedFilters() {
		let self = this;
		for (let i=0; i<self.selected_filters.length; i++) {
			
			self.applied_filters_field.add_filter (
				self.selected_filters[i]['filter_id'], 
				self.selected_filters[i]['filter_name'],
				self.selected_filters[i]['filter_key'], 
				self.selected_filters[i]['filter_value'],
				false
			);
		}
		
		$("#search_form").submit();
	}

	add2SelectedList(filter_value) {
		$('#buckets-overlay-selected-list').append('<li id="overlay_selected_' + filter_value + '">' + filter_value + '</li>');
	}


	addApplyCancelEvents() {
		let self = this;
		$('#buckets-overlay-cancel-button').click( function () {
			self.closeOverlay();
		});
		$('#buckets-overlay-apply-button').click( function () {
			self.submitSelectedFilters();
		});
	}

}
