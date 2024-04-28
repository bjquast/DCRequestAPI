'use strict'

class BucketsOverlay {
	constructor (applied_filters_field) {
		this.applied_filters_field = applied_filters_field;
		this.agg_key = '';
		this.buckets_search_term = '';
		
		/*
		this.buckets_sort_dir = 'asc';
		this.buckets_sort_alphanum = true;
		this.remaining_or_all = 'remaining';
		this.buckets_search_term = '';
		*/
	}

	readOverlayFormParameters() {
		let self = this;
		let form = document.getElementById("buckets_overlay_form");
		self.overlay_form_data = new FormData(form);
		
		let sort_params = self.overlay_form_data.get('overlay_sort_select').split(':');
		if (sort_params[0] == 'alphanum') {
			self.overlay_form_data.append('buckets_sort_alphanum', true);
		}
		else {
			self.overlay_form_data.append('buckets_sort_alphanum', false);
		}
		self.overlay_form_data.append('buckets_sort_dir', sort_params[1]);
		
		// take over the parameters in the outer search form when remaining is selected
		if (self.overlay_form_data.get('overlay_remaining_all_select') == 'remaining') {
			self.readSearchFormParameters();
			for (let entry of self.form_data.entries()) {
				self.overlay_form_data.append(entry[0], entry[1]);
			}
			
		}
	}

	readSearchFormParameters() {
		let self = this;
		let form = document.getElementById("search_form");
		self.form_data = new FormData(form);
	}

	updateBucketList() {
		let self = this;
		
		self.buckets = [];
		self.readOverlayFormParameters();
		self.overlay_form_data.append('aggregation', self.agg_key);
		
		console.log('###########', self.buckets_search_term);
		if (self.buckets_search_term) {
			console.log('-----------', self.buckets_search_term);
			self.overlay_form_data.append('buckets_search_term', self.buckets_search_term);
		}
		
		console.log(self.overlay_form_data);
		
		$.ajax({
			url: "./aggregation",
			type: 'POST',
			processData: false,
			contentType: false,
			dataType: 'json',
			data: self.overlay_form_data
		})
		.fail(function (xhr, textStatus, errorThrown) {
			let error_response = xhr.responseJSON;
			console.log(error_response);
		})
		.done( function(data) {
			self.buckets = data;
			
			self.createBucketList();
			self.addFilterEvents();
			self.addApplyCancelEvents();
		})
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
		self.readSearchFormParameters();
		self.requestBuckets();
	}


	createOverlayWindow() {
		let self = this;
		$('#buckets-overlay-slot').append('<div id="buckets-overlay" class="overlay"></div>');
		$('#buckets-overlay').append('<div id="buckets-overlay-header" class="overlay-header"></div>');
		$('#buckets-overlay-header').append('<div id="buckets-overlay-headline" class="flex-space-between padding-1em"></div>');
		
		if (self.buckets['aggregation_names']['en']) {
			$('#buckets-overlay-headline').append('<div><label><b>' + self.buckets['aggregation_names']['en'] + '</b></label></div>');
		}
		else {
			$('#buckets-overlay-headline').append('<div><label>' + self.buckets['aggregation'] + '</label></div>');
		}
		
		$('#buckets-overlay-headline').append('<form id="buckets_overlay_form" class="hidden"></form>');
		
		$('#buckets-overlay-headline').append('<div id="overlay_search_div"></div>');
		$('#overlay_search_div').append('<label for="overlay_bucket_search">Search in filters: </label>');
		$('#overlay_search_div').append('<input id="overlay_bucket_search" form="buckets_overlay_form" type="text" name="overlay_bucket_search"/>');
		
		$('#buckets-overlay-headline').append('<div id="overlay_remaining_all_div"></div>');
		$('#overlay_remaining_all_div').append('<label for="overlay_remaining_all_select">show filters: </label>');
		$('#overlay_remaining_all_div').append('<select id="overlay_remaining_all_select" form="buckets_overlay_form" class="update_params" name="overlay_remaining_all_select"></select>');
		$('#overlay_remaining_all_select').append('<option value="remaining">remaining</option>');
		$('#overlay_remaining_all_select').append('<option value="all">all</option>');
		
		$('#buckets-overlay-headline').append('<div id="overlay_sort_div"></div>');
		$('#overlay_sort_div').append('<label for="overlay_sort_select">sort by: </label>');
		$('#overlay_sort_div').append('<select id="overlay_sort_select" form="buckets_overlay_form" class="update_params" name="overlay_sort_select"></select>');
		$('#overlay_sort_select').append('<option value="count:desc">count &darr;</option>');
		$('#overlay_sort_select').append('<option value="alphanum:asc">a-z &uarr;</option>');
		$('#overlay_sort_select').append('<option value="alphanum:desc">z-a &darr;</option>');
		
		$('#buckets-overlay-headline').append('<div class="buttons-right-position"></div>');
		$('#buckets-overlay-headline .buttons-right-position').append('<button id="buckets-overlay-cancel-button">cancel</button>');
		$('#buckets-overlay-headline .buttons-right-position').append('<button id="buckets-overlay-apply-button">apply</button>');
		
		$('#buckets-overlay-header').append('<div id="buckets-overlay-selected-div"></div>');
		$('#buckets-overlay-selected-div').append('<ul id="buckets-overlay-selected-list"></ul>');
		
		$('#buckets-overlay').append('<div id="buckets-list" class="selectable-items-list"></div>');
		
		self.setOverlayEvents();
	}


	setOverlayEvents() {
		let self = this;
		
		$('#overlay_bucket_search').off();
		$("#overlay_bucket_search").on("keyup", ( function() {
			let search_val = $(this).val();
			
			if (search_val) {
				self.buckets_search_term = search_val;
				self.updateBucketList();
			}
			
			else {
				self.buckets_search_term = '';
				self.updateBucketList();
			}
		}));
		
		$('.update_params').each( function () {
			$(this).off();
			$(this).change( function() {
				self.updateBucketList();
			});
			
		});
		
	}


	createBucketList() {
		let self = this;
		$('#buckets-list').empty();
		$('#buckets-list').append('<ul></ul>');
		
		for (let i = 0; i < self.buckets['buckets'].length; i++) {
			let bucket_id = 'bucket_entry_' + i;
			let bucket_value = self.buckets['buckets'][i][0] + ' (' + self.buckets['buckets'][i][1] + ')';
			
			$('#buckets-list ul').append('<li id="' + bucket_id + '" class="bucket_entry clickable">' + bucket_value + '</li>');
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
			$(this).off();
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
