'use strict' 

class HierarchyLists {

	constructor (applied_filters) {
		this.appliedfilters = appliedfilters;
	}


	add_collapsible_hierarchies_events() {
		let self = this;
		$('.hierarchy_selectors').each( function () {
			//$(this).off();
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
		
		$('.hierarchy_open_button').each( function () {
			$(this).off();
			$(this).click( function() {
				let hierarchy_filter_id = $(this).data('hierarchy-filter-id');
				let hierarchy_filter_name = $(this).data('hierarchy-filter-name');
				let hierarchy_filter_key = $(this).data('hierarchy-filter-key');
				let hierarchy_filter_value = $(this).data('hierarchy-filter-value');
				
				//self.toggleHierarchyPart(hierarchy_filter_id, hierarchy_filter_name, hierarchy_filter_key, hierarchy_filter_value);
			});
		});
	}


	readSearchFormParameters() {
		let self = this;
		let form = document.getElementById("search_form");
		self.form_data = new FormData(form);
	}


	createFilterList(data) {
		let self = this;
		$('#hierarchy_filters').empty();
		$('#hierarchy_filters').append(data);
	}


	updateHierarchyList(hierarchy_list_id) {
		let self = this;
		
		let buckets = [];
		
		let hierarchy_filter_key = $('#' + hierarchy_list_id).attr('data-hierarchy-filter-key');
		self.readSearchFormParameters();
		
		
		// add a hierarchies parameter without path to open the hierarchy tree when no other path is available
		self.form_data.append('hierarchies', hierarchy_filter_key + ':');
		self.form_data.append('buckets_size', 1000);
		
		console.log(self.form_data);
		
		
		$.ajax({
			url: "./hierarchies",
			type: 'POST',
			processData: false,
			contentType: false,
			data: self.form_data
		})
		.fail(function (xhr, textStatus, errorThrown) {
			let error_response = xhr.responseJSON;
			console.log(error_response);
		})
		.done( function(data) {
			//console.log(data);
			self.createFilterList(data);
			self.add_collapsible_hierarchies_events();
			self.add_hierarchy_filter_events();
		});
	}

	/*
	toggleHierarchyPart(hierarchy_filter_id, hierarchy_filter_name, hierarchy_filter_key, hierarchy_filter_value) {
		let self = this;
		
		let buckets = [];
		self.readSearchFormParameters();
		
	}
	*/
}
