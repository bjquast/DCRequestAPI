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
		query_pattern = re.compile(r'stack_query_((string)|(date_from)|(date_to))_(\d+)_(\d+)$')
		cache_dicts = {}
		#pudb.set_trace()
		
		"""
		generate a dict from all stack_query parameters
		TODO: currently, this dict is converted into a dict of lists with subqueries later on, due to the stacked_queries_macro template
		and the methods in ES_Searcher. They should be changed to use a dict of dicts, perhaps with arbitrary depth
		"""
		for param in self.params_dict:
			if param.startswith('stack_query_'):
				m = query_pattern.match(param)
				if m is not None:
					query_type = m.group(1)
					query_count = m.group(5)
					sub_query_count = m.group(6)
					# if there are more than one parameter with the same query_count and sub_query_count take only the last one, if there is no parameter value
					# for the parameter add an empty string
					query_string = self.params_dict.get('stack_query_string_{0}_{1}'.format(query_count, sub_query_count), [''])[-1]
					date_from = self.params_dict.get('stack_query_date_from_{0}_{1}'.format(query_count, sub_query_count), [''])[-1]
					date_to = self.params_dict.get('stack_query_date_to_{0}_{1}'.format(query_count, sub_query_count), [''])[-1]
					field = self.params_dict.get('stack_query_field_{0}_{1}'.format(query_count, sub_query_count), [''])[-1]
					if query_string or date_from or date_to:
						if query_count not in cache_dicts:
							cache_dicts[query_count] = {
								'outer_connector': self.params_dict.get('stack_search_outer_connector_{0}'.format(query_count), ['AND'])[-1],
								'inner_connector': self.params_dict.get('stack_search_inner_connector_{0}'.format(query_count), ['AND'])[-1]
							}
							if 'stack_search_add_subquery_{0}'.format(query_count) in self.params_dict:
								cache_dicts[query_count]['add_subquery'] = True
							
							cache_dicts[query_count]['subqueries'] = {}
						
						if sub_query_count not in cache_dicts[query_count]['subqueries']:
							cache_dicts[query_count]['subqueries'][sub_query_count] = {}
						
						cache_dicts[query_count]['subqueries'][sub_query_count]['string'] = query_string
						cache_dicts[query_count]['subqueries'][sub_query_count]['date_from'] = date_to
						cache_dicts[query_count]['subqueries'][sub_query_count]['date_to'] = date_from
						cache_dicts[query_count]['subqueries'][sub_query_count]['field'] = field
						if query_type in ['date_from', 'date_to']:
							cache_dicts[query_count]['subqueries'][sub_query_count]['query_type'] = 'date'
						elif query_type in ['string']:
							cache_dicts[query_count]['subqueries'][sub_query_count]['query_type'] = 'term'
		
		"""
		convert to a dict of queries with lists of subqueries
		reset the count of the queries to sequential numbers starting with 0
		"""
		pudb.set_trace()
		self.search_params['stack_queries'] = []
		query_dicts = {}
		i = 0
		for query_count in cache_dicts:
			if i not in query_dicts:
				query_dicts[i] = {
					'string': [],
					'date_from': [],
					'date_to': [],
					'field': [],
					'query_type': [],
				}
			query_dicts[i]['outer_connector'] = cache_dicts[query_count]['outer_connector']
			query_dicts[i]['inner_connector'] = cache_dicts[query_count]['inner_connector']
			if 'add_subquery' in cache_dicts[query_count]:
				query_dicts[i]['add_subquery'] = cache_dicts[query_count]['add_subquery']
			
			for sub_query_count in cache_dicts[query_count]['subqueries']:
				query_dicts[i]['string'].append(cache_dicts[query_count]['subqueries'][sub_query_count]['string'])
				query_dicts[i]['date_from'].append(cache_dicts[query_count]['subqueries'][sub_query_count]['date_from'])
				query_dicts[i]['date_to'].append(cache_dicts[query_count]['subqueries'][sub_query_count]['date_to'])
				query_dicts[i]['field'].append(cache_dicts[query_count]['subqueries'][sub_query_count]['field'])
				query_dicts[i]['query_type'].append(cache_dicts[query_count]['subqueries'][sub_query_count]['query_type'])
			
			self.search_params['stack_queries'].append(query_dicts[i])
			i = i + 1
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
	
