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
						
						let hierarchy_filter_key = $('#' + hierarchy_list_id).attr('data-hierarchy-filter-key');
						
						self.readSearchFormParameters();
						self.updateHierarchyList(hierarchy_filter_key, self.form_data);
					}
				}
				else {
					let hierarchy_list_id = $(this).prop('id');
					hierarchy_list_id = hierarchy_list_id.replace(/\./g, '\\.');
					let hierarchy_filter_key = $('#' + hierarchy_list_id).attr('data-hierarchy-filter-key');
					
					$(this).find('ul').remove();
					
					$('.open_hierarchy_selectors_input').each( function () {
						if ($(this).val() == hierarchy_filter_key) {
							$(this).prop('checked', false);
						}
					});
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
				let hierarchy_filter_key = $(this).data('hierarchy-filter-key');
				let hierarchy_filter_value = $(this).data('hierarchy-filter-value');
				let is_parent = $(this).data('is-parent');
				
				self.toggleHierarchyPart(hierarchy_filter_key, hierarchy_filter_value, is_parent);
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


	updateHierarchyList(hierarchy_filter_key, form_data) {
		let self = this;
		
		let buckets = [];
		
		// add a hierarchies parameter without path to open the hierarchy tree when no other path is available
		// self.form_data.append('hierarchies', hierarchy_filter_key + ':');
		
		let open_hierarchies = form_data.getAll('open_hierarchy_selectors');
		
		if (open_hierarchies.indexOf(hierarchy_filter_key) == -1) {
			form_data.append('open_hierarchy_selectors', hierarchy_filter_key);
		}
		
		form_data.delete('buckets_size');
		form_data.append('buckets_size', 1000);
		
		$.ajax({
			url: "./hierarchies",
			type: 'POST',
			processData: false,
			contentType: false,
			data: form_data
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


	removePathFromHierarchyList(hierarchy_filter_key, form_data) {
		let self = this;
		
		let buckets = [];
		
		form_data.append('buckets_size', 1000);
		
		//console.log(self.form_data);
		
		$.ajax({
			url: "./hierarchy/remove_path/" + hierarchy_filter_key,
			type: 'POST',
			processData: false,
			contentType: false,
			data: form_data
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


	toggleHierarchyPart(hierarchy_filter_key, hierarchy_filter_value, is_parent) {
		let self = this;
		self.readSearchFormParameters();
		if (is_parent == 'is parent') {
			self.form_data.append('path_to_remove', hierarchy_filter_value);
			self.form_data.append('buckets_size', 1000);
			self.removePathFromHierarchyList(hierarchy_filter_key, self.form_data);
		}
		
		else {
			self.form_data.append('hierarchies', hierarchy_filter_key + ':' + hierarchy_filter_value);
			self.form_data.append('buckets_size', 1000);
			self.updateHierarchyList(hierarchy_filter_key, self.form_data);
		}
	}

}
