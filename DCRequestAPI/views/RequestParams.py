import pudb
import json


class RequestParams():
	def __init__(self, request):
		self.request = request
		
		self.read_request_params()
		self.read_search_params()
		self.read_credentials()
		self.set_requeststring()
		
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


	def read_stack_queries_params(self):
		pudb.set_trace()
		
		self.search_params['stack_queries'] = []
		if 'stack_query_id' in self.params_dict:
			for query_id in self.params_dict['stack_query_id']:
				terms = []
				fields = []
				for term_id in self.params_dict['stack_query_term_id']:
					if term_id.startswith(str(query_id)):
						term = self.params_dict.get('stack_query_terms_{0}'.format(term_id), [''])[-1]
						field = self.params_dict.get('stack_query_fields_{0}'.format(term_id), [''])[-1]
						if len(term) > 0 and len(field) > 0:
							terms.append(term)
							fields.append(field)
				
				if len(terms) > 0 and len(fields) > 0:
					query_dict = {
						'terms': terms,
						'fields': fields,
						'outer_connector': self.params_dict.get('stack_search_outer_connector_{0}'.format(query_id), ['AND'])[-1],
						'inner_connector': self.params_dict.get('stack_search_inner_connector_{0}'.format(query_id), ['AND'])[-1]
					}
					self.search_params['stack_queries'].append(query_dict)
		return


	def read_search_params(self):
		self.search_params = {}
		
		self.read_stack_queries_params()
		
		exists_params = ['restrict_to_users_projects']
		simple_params = ['pagesize', 'page', 'sorting_col', 'sorting_dir', 'aggregation', 'tree', 'aggs_suggestion_search', 'match_queries_connector']
		complex_params = ['term_filters',]
		list_params = ['open_filter_selectors', 'result_table_columns', 'parent_ids', 'match_query']
		
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
						self.search_params[param_name][query[0]].append(query[1])
			else:
				self.search_params[param_name] = []
		
		for param_name in list_params:
			if param_name in self.params_dict:
				self.search_params[param_name] = self.params_dict[param_name]
			else:
				self.search_params[param_name] = []
		
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
