'use strict'

class FilterOverlay {
	constructor () {
		this.agg_name = '';
	}


	requestBuckets() {
		let self = this;
		self.buckets = [];
		
		$.ajax({
			url: "./aggregation/" + self.agg_name,
			type: 'POST',
			dataType: 'json',
			data: 
		})
		.fail(function (xhr, textStatus, errorThrown) {
			let error_response = xhr.responseJSON;
			console.log(error_response);
		})
		.done( function(data) {
			self.buckets = data;
			closeOverlay()
			createBucketList();
		})
	}


	openOverlay(agg_name) {
		let self = this;
		self.agg_name = agg_name;
		self.requestBuckets();
	}


	createBucketList() {
		let self = this;
		$('#filter-overlay-slot').append('<div id="filter-overlay" class="overlay"></div>');
		$('#filter-overlay').append('<p>' + self.buckets['aggregation_name'] + '</p>');
		$('#filter-overlay').append('<ul></ul>');
		
		for (i = 1; i <= self.buckets['buckets'].length; i++) {
			let bucket_id = 'bucket_entry_' + i;
			let bucket_value = self.buckets['buckets'][i][0] + '_' + self.buckets['buckets'][i][1];
			$('#filter-overlay ul').append('<li id="' + bucket_id + '" class="bucket_entry>' + bucket_value + '</li>');
			$('#' + bucket_id).attr('data-filter-id', 'filter_' + self.buckets['aggregation'] + '_' + self.buckets['buckets'][i][0]);
			if (self.buckets['aggregation_names']['en']) {
				$('#' + bucket_id).attr('data-filter-name', self.buckets['aggregation_names']['en']);
			}
			$('#' + bucket_id).attr('data-filter-key', self.buckets['aggregation']);
		}
	}

	closeOverlay() {
		let self = this;
		$('#filter-overlay-slot').empty();
	}

}
