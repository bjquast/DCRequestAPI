'use strict' 

class HierarchyLists {

	constructor (applied_filters) {
		this.appliedfilters = appliedfilters;
	}


	add_collapsible_hierarchies_events() {
		let self = this;
		$('.hierarchy_selectors').each( function () {
			$(this).on('toggle', function() {
				if ($(this).attr('open') == 'open') {
					$(this).children('input:checkbox').prop('checked', true);
					if ($(this).find('ul').length == 0) {
						let hierarchy_list_id = $(this).prop('id');
						hierarchy_list_id = hierarchy_list_id.replace(/\./g, '\\.');
						self.updateHierarchyList(hierarchy_list_id);
					}
				}
				else {
					$(this).children('input:checkbox').prop('checked', false);
					$(this).find('ul').remove();
				}
			});
		});
	}


	add_hierarchy_filter_events() {
		let self = this;
		$('.hierarchy_entry').each( function () {
			$(this).off();
			$(this).click( function() {
				let hierarchy_filter_id = $(this).data('hierarchy-filter-id');
				let hierarchy_filter_name = $(this).data('hierarchy-filter-name');
				let hierarchy_filter_key = $(this).data('hierarchy-filter-key');
				let hierarchy_filter_value = $(this).data('hierarchy-filter-value');
				
				self.appliedfilters.add_filter(hierarchy_filter_id, hierarchy_filter_name, hierarchy_filter_key, hierarchy_filter_value);
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


	createFilterList(hierarchy_list_id, buckets) {
		let self = this;
		
		$('#' + hierarchy_list_id).append('<ul>');
		let unordered_list = $('#' + hierarchy_list_id + ' ul');
		unordered_list.addClass('ul-no-bullet');
		
		for (let i = 0; i < buckets['buckets'].length; i++) {
			let list_entry = $('<li></li>');
			unordered_list.append(list_entry);
			
			let open_button = $('<span class="hierarchy_open_button clickable"><span>').appendTo(list_entry);
			open_button.html('+ ' + buckets['buckets'][i][0] + ' ');
			open_button.attr('data-hierarchy-filter-id', 'filter_' + buckets['aggregation'] + '_' + buckets['buckets'][i][0]);
			open_button.attr('data-hierarchy-filter-key', buckets['aggregation']);
			open_button.attr('data-hierarchy-filter-value', buckets['buckets'][i][0]);
			
			let hierarchy_entry = $('<span class="hierarchy_entry clickable">' + buckets['buckets'][i][0] + ' (' + buckets['buckets'][i][1] + ')<span>').appendTo(list_entry);
			hierarchy_entry.attr('data-hierarchy-filter-id', 'filter_' + buckets['aggregation'] + '_' + buckets['buckets'][i][0]);
			hierarchy_entry.attr('data-hierarchy-filter-key', buckets['aggregation']);
			hierarchy_entry.attr('data-hierarchy-filter-value', buckets['buckets'][i][0]);
			if (buckets['aggregation_names']['en']) {
				hierarchy_entry.attr('data-hierarchy-filter-name', buckets['aggregation_names']['en']);
			}
			else {
				hierarchy_entry.attr('data-hierarchy-filter-name', buckets['aggregation']);
			}
		}
	}


	updateHierarchyList(hierarchy_list_id, hierarchy_pathes) {
		let self = this;
		
		let buckets = [];
		
		let hierarchy_filter_key = $('#' + hierarchy_list_id).attr('data-hierarchy-filter-key');
		self.readSearchFormParameters();
		
		
		self.form_data.append('hierarchies', hierarchy_filter_key + ':');
		self.form_data.append('buckets_size', 1000);
		
		$.ajax({
			url: "./hierarchy_aggregation/" + hierarchy_filter_key,
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
			self.createFilterList(hierarchy_list_id, buckets);
			//self.add_hierarchy_opener_event();
			self.add_hierarchy_filter_events();
		});
	}
}

