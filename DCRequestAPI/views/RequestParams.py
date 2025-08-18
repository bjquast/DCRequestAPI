import pudb
import json
import re

from ElasticSearch.FieldConfig import FieldConfig


class RequestParams():
	def __init__(self, request):
		self.request = request
		self.fieldconf = FieldConfig()
		
		self.read_request_params()
		self.read_search_params()
		self.read_credentials()
		self.set_requeststring()
		
		default_params_setter = DefaultParamsSetter(self.search_params)
		self.search_params = default_params_setter.search_params
		pass


	def read_request_params(self):
		self.params_dict = {}
		try:
			json_params = self.request.json_body
			# prepare the params as dict of lists
			for key in json_params:
				self.params_dict[key] = []
				if isinstance(json_params[key], list) or isinstance(json_params[key], tuple):
					self.params_dict[key].extend(json_params[key])
				else:
					self.params_dict[key].append(json_params[key])
		except:
			self.params_dict = self.request.params.dict_of_lists()
		return


	def read_stack_queries_params(self):
		query_pattern = re.compile(r'stack_query_((terms)|(date_from)|(date_to))_(\d+)_(\d+)$')
		query_dicts = {}
		self.search_params['stack_queries'] = []
		for param in self.params_dict:
			if param.startswith('stack_query_'):
				m = query_pattern.match(param)
				if m is not None:
					query_type = m.group(1)
					query_count = m.group(5)
					subquery_count = m.group(6)
					# if there are more than one parameter with the same query_count and subquery_count take only the last one, if there is no parameter value
					# for the parameter add an empty string
					query_string = self.params_dict.get('stack_query_{0}_{1}_{2}'.format(query_type, query_count, subquery_count), [''])[-1]
					field = self.params_dict.get('stack_query_fields_{0}_{1}'.format(query_count, subquery_count), [''])[-1]
					if query_string:
						if query_count not in query_dicts:
							query_dicts[query_count] = {
								'terms': [],
								'fields': [],
								'query_types': [],
								'outer_connector': self.params_dict.get('stack_search_outer_connector_{0}'.format(query_count), ['AND'])[-1],
								'inner_connector': self.params_dict.get('stack_search_inner_connector_{0}'.format(query_count), ['AND'])[-1]
							}
							if 'stack_search_add_subquery_{0}'.format(query_count) in self.params_dict:
								query_dicts[query_count]['add_subquery'] = True
							# if 'stack_search_delete_subquery_{0}'.format(query_count) in self.params_dict:
							# 	query_dicts[query_count]['delete_subquery'] = True
						
						query_dicts[query_count]['terms'].append(query_string)
						query_dicts[query_count]['fields'].append(field)
						if query_type in ['date_from', 'date_to']:
							query_dicts[query_count]['query_types'].append('date')
						elif query_type in ['terms']:
							query_dicts[query_count]['query_types'].append('term')
						
		
		for query_count in query_dicts:
			'''
			# is 'delete_subquery' needed? The buttons for deleting subqueries were not shown any more
			# and subqueries are deleted when their query_string is empty
			if 'delete_subquery' in query_dicts[query_count] and len(query_dicts[query_count]['terms']) > 1:
				query_dicts[query_count]['terms'].pop()
				query_dicts[query_count]['fields'].pop()
				query_dicts[query_count]['query_types'].pop()
			'''
			
			terms_copy = []
			fields_copy = []
			query_types_copy = []
			for i in range(len(query_dicts[query_count]['terms'])):
				terms_copy.append(query_dicts[query_count]['terms'][i])
				fields_copy.append(query_dicts[query_count]['fields'][i])
				query_types_copy.append(query_dicts[query_count]['query_types'][i])
			query_dicts[query_count]['terms'] = terms_copy
			query_dicts[query_count]['fields'] = fields_copy
			query_dicts[query_count]['query_types'] = query_types_copy
			
			self.search_params['stack_queries'].append(query_dicts[query_count])
		return


	def read_search_params(self):
		self.search_params = {}
		
		self.read_stack_queries_params()
		
		exists_params = ['restrict_to_users_projects']
		boolean_params = ['buckets_sort_alphanum']
		simple_params = ['pagesize', 'page', 'sorting_col', 'sorting_dir', 'aggregation', 'tree', 'match_queries_connector', 
							'term_filters_connector', 'buckets_search_term', 'overlay_remaining_all_select', 'buckets_sort_dir', 'buckets_size',
							'path_to_remove'
						]
		complex_params = ['term_filters', 'hierarchies', 'date']
		
		#range_params = ['date']
		
		list_params = ['open_filter_selectors', 'result_table_columns', 'selected_filter_sections', 'open_hierarchy_selectors']
		
		for param_name in boolean_params:
			if param_name in self.params_dict:
				if self.params_dict[param_name][-1] in ['false', 'False', '', '0']:
					self.search_params[param_name] = False
				elif not self.params_dict[param_name][-1]:
					self.search_params[param_name] = False
				else:
					self.search_params[param_name] = True
		
		for param_name in exists_params:
			if param_name in self.params_dict:
				self.search_params[param_name] = True
		
		for param_name in simple_params:
			if param_name in self.params_dict and len(self.params_dict[param_name]) > 0:
				self.search_params[param_name] = self.params_dict[param_name][-1]
		
		for param_name in complex_params: 
			if param_name in self.params_dict and len(self.params_dict[param_name]) > 0:
				for searchquery in self.params_dict[param_name]:
					query = searchquery.split(':', 1)
					if len(query) == 2:
						if param_name not in self.search_params:
							self.search_params[param_name] = {}
						if query[0] not in self.search_params[param_name]:
							self.search_params[param_name][query[0]] = []
						if query[1] not in self.search_params[param_name][query[0]]:
							self.search_params[param_name][query[0]].append(query[1])
					else:
						pass
			else:
				self.search_params[param_name] = {}
		
		for param_name in list_params:
			if param_name in self.params_dict:
				self.search_params[param_name] = self.params_dict[param_name]
			else:
				self.search_params[param_name] = []
		
		'''
		for param_name in range_params:
			if param_name in self.params_dict and len(self.params_dict[param_name]) > 0:
				for searchquery in self.params_dict[param_name]:
					query = searchquery.split(':', 2)
					if len(query) == 3 and (len(query[1]) > 0 or len(query[2]) > 0):
						if param_name not in self.search_params:
							self.search_params[param_name] = {}
						if query[0] not in self.search_params[param_name]:
							self.search_params[param_name][query[0]] = []
						range_dict = {}
						if len(query[1]) > 0:
							range_dict['gte'] = query[1]
						if len(query[2]) > 0:
							range_dict['gte'] = query[2]
						self.search_params[param_name][query[0]].append(range_dict)
					else:
						pass
			else:
				self.search_params[param_name] = {}
		'''
		
		return


	def read_credentials(self):
		self.credentials = {}
		credentials = ['username', 'password', 'token', 'logout']
		for param_name in credentials: 
			if param_name in self.params_dict and len(self.params_dict[param_name]) > 0:
				if self.params_dict[param_name][-1] != '' and self.params_dict[param_name][-1] is not None:
					self.credentials[param_name] = self.params_dict[param_name][-1]
		return


	def set_requeststring(self):
		self.requeststring = ''
		paramslist = []
		for param in self.params_dict:
			if param not in ['username', 'password', 'token', 'logout', 'db_accronym']:
				for value in self.params_dict[param]:
					paramslist.append('{0}={1}'.format(param, value))
		
		self.requeststring = '&'.join(paramslist)
		return






class DefaultParamsSetter():
	"""
	set default values for missing search_params, concatenate parent parameters and fix some params
	"""
	def __init__(self, search_params):
		self.fieldconf = FieldConfig()
		
		self.search_params = search_params
		self.set_default_params()
		
		self.reduce_hierarchical_term_filters()


	def set_default_params(self):
		self.set_term_filters()
		self.set_date_filters()
		self.set_hierarchy_filters()
		
		self.set_selected_filter_sections()
		self.set_open_filter_selectors()
		#self.set_open_hierarchy_selectors()
		self.set_result_table_columns()


	def set_term_filters(self):
		term_filters = {}
		for key in self.search_params['term_filters']:
			if key in self.fieldconf.term_fields:
				term_filters[key] = self.search_params['term_filters'][key]
		self.search_params['term_filters'] = term_filters


	def set_date_filters(self):
		date_filters = {}
		for key in self.search_params['date']:
			if key in self.fieldconf.date_fields:
				date_filters[key] = self.search_params['date'][key]
		self.search_params['date'] = date_filters


	def set_hierarchy_filters(self):
		hierarchy_filters = {}
		for key in self.search_params['hierarchies']:
			if key in self.fieldconf.hierarchy_filter_fields:
				hierarchy_filters[key] = self.search_params['hierarchies'][key]
		self.search_params['hierarchies'] = hierarchy_filters


	def set_selected_filter_sections(self):
		# these are the filters shown as available filters
		selected_filters = []
		for field in self.fieldconf.available_filter_fields:
			if field in self.search_params['selected_filter_sections']:
				selected_filters.append(field)
			elif field in self.search_params['term_filters']:
				selected_filters.append(field)
			elif field in self.search_params['date']:
				selected_filters.append(field)
			elif field in self.search_params['hierarchies']:
				selected_filters.append(field)
		if len(selected_filters) <= 0:
			selected_filters = self.fieldconf.default_filter_sections
		self.search_params['selected_filter_sections'] = selected_filters
		return


	def set_open_filter_selectors(self):
		# these are the filters that are opend and show a list of buckets
		open_filters = []
		for field in self.fieldconf.available_filter_fields:
			if field in self.search_params['open_filter_selectors']:
				open_filters.append(field)
			elif field in self.search_params['term_filters']:
				open_filters.append(field)
			elif field in self.search_params['date']:
				open_filters.append(field)
			elif field in self.search_params['hierarchies']:
				open_filters.append(field)
		self.search_params['open_filter_selectors'] = open_filters
		return


	'''
	def set_open_hierarchy_selectors(self):
		open_hierarchy_selectors = []
		for field in self.search_params['open_hierarchy_selectors']:
			if field in self.fieldconf.hierarchy_filter_fields:
				open_hierarchy_selectors.append(field)
		self.search_params['open_hierarchy_selectors'] = open_hierarchy_selectors
	'''


	def set_result_table_columns(self):
		table_cols = []
		for field in self.search_params['result_table_columns']:
			if field in self.fieldconf.result_fields:
				table_cols.append(field)
		if len(table_cols) <= 0:
			table_cols = self.fieldconf.result_fields
		if 'PartAccessionNumber' not in table_cols:
			table_cols.insert(0, 'PartAccessionNumber')
		
		self.search_params['result_table_columns'] = table_cols
		return


	# for hierarchy filters all term_filters must be removed that are a parent of any other term filter in the hierarchy
	def reduce_hierarchical_term_filters(self):
		# when term_filters are used with hierarchies
		# filter out the term_filters that are parents of other term_filters
		
		hierarchy_filter_fields = self.fieldconf.hierarchy_filter_fields
		term_filters = self.search_params['term_filters']
		
		new_term_filters = {}
		for key in term_filters:
			if key in hierarchy_filter_fields:
				
				filter_dict = {}
				
				for filter_entry in term_filters[key]:
					element_list = [element.strip() for element in filter_entry.split('>')]
					self.set_reduced_hierarchy_dict(filter_dict, element_list)
				
				self.reduced_hierarchy_pathes = []
				self.set_reduced_hierarchy_pathes(filter_dict)
				
				if len(self.reduced_hierarchy_pathes) > 0:
					new_term_filters[key] = []
					for hierarchy_path in self.reduced_hierarchy_pathes:
						new_term_filters[key].append('>'.join(hierarchy_path))
				
			else:
				new_term_filters[key] = term_filters[key]
		
		self.search_params['term_filters'] = new_term_filters
		return


	def set_reduced_hierarchy_dict(self, subdict, element_list):
		if len(element_list) <= 0:
			return
		element = element_list.pop(0)
		if element in subdict.keys():
			self.set_reduced_hierarchy_dict(subdict[element], element_list)
		else:
			subdict[element] = {}
			self.set_reduced_hierarchy_dict(subdict[element], element_list)
		return


	def set_reduced_hierarchy_pathes(self, sub_dict, path = None):
		if path is None:
			path = []
		for key in sub_dict:
			if isinstance(sub_dict[key], dict) and len(sub_dict[key]) > 0:
				path.append(key)
				self.set_reduced_hierarchy_pathes(sub_dict[key], path)
			elif isinstance(sub_dict[key], dict) and len(sub_dict[key]) <= 0:
				path.append(key)
				self.reduced_hierarchy_pathes.append(path)
				return
		return
	
