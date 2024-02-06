'use strict'

class FilterOverlay {
	constructor (applied_filters_field) {
		this.applied_filters_field = applied_filters_field;
		this.agg_key = '';
	}


	requestBuckets() {
		let self = this;
		self.buckets = [];
		
		$.ajax({
			url: "./aggregation",
			type: 'POST',
			dataType: 'json',
			data: {'aggregation': self.agg_key}
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
		})
	}


	openOverlay(agg_key) {
		let self = this;
		self.agg_key = agg_key;
		self.requestBuckets();
	}


	createOverlayWindow() {
		$('#filter-overlay-slot').append('<div id="filter-overlay" class="overlay"></div>');
		$('#filter-overlay').append('<div id="overlay-header"></div>');
	}


	createBucketList() {
		let self = this;
		if (self.buckets['aggregation_names']['en']) {
			$('#filter-overlay').append('<p>' + self.buckets['aggregation_names']['en'] + '</p>');
			
		}
		$('#filter-overlay').append('<ul></ul>');
		
		for (let i = 0; i < self.buckets['buckets'].length; i++) {
			let bucket_id = 'bucket_entry_' + i;
			let bucket_value = self.buckets['buckets'][i][0] + ' (' + self.buckets['buckets'][i][1] + ')';
			
			$('#filter-overlay ul').append('<li id="' + bucket_id + '" class="bucket_entry">' + bucket_value + '</li>');
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
		$('#filter-overlay-slot').empty();
	}

	addFilterEvents() {
		let self = this;
		$('#filter-overlay .bucket_entry').each( function () {
			$(this).click( function() {
				let filter_id = $(this).data('filter-id');
				let filter_name = $(this).data('filter-name');
				let filter_key = $(this).data('filter-key');
				let filter_value = $(this).data('filter-value');
				self.applied_filters_field.add_filter(filter_id, filter_name, filter_key, filter_value);
			});
		});
	}


}
