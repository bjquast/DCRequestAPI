import pudb
import json


class RequestParams():
	def __init__(self):
		pass


	def get_search_params(self, request):
		
		# check if there is a json body in the request
		try:
			json_params = request.json_body
			# prepare the params as dict of lists
			request_params = {}
			for key in json_params:
				request_params[key] = []
				if isinstance(json_params[key], list) or isinstance(json_params[key], tuple):
					request_params[key].extend(json_params[key])
				else:
					request_params[key].append(json_params[key])
		except:
			request_params = request.params.dict_of_lists()
		
		search_params = {}
		
		simple_params = ['pagesize', 'page', 'sorting_col', 'sorting_dir', 'match_query', 'aggregation']
		complex_params = ['term_filters',]
		list_params = ['open_filter_selectors', 'result_table_columns']
		
		for param_name in simple_params: 
			if param_name in request_params and len(request_params[param_name]) > 0:
				search_params[param_name] = request_params[param_name][-1]
		
		for param_name in complex_params: 
			if param_name in request_params and len(request_params[param_name]) > 0:
				for searchquery in request_params[param_name]:
					query = searchquery.split(':')
					if len(query) == 2:
						if param_name not in search_params:
							search_params[param_name] = {}
						if query[0] not in search_params[param_name]:
							search_params[param_name][query[0]] = []
						search_params[param_name][query[0]].append(query[1])
			else:
				search_params[param_name] = []
		
		for param_name in list_params:
			if param_name in request_params:
				search_params[param_name] = request_params[param_name]
			else:
				search_params[param_name] = []
		
		return search_params


	def get_requeststring(self, request):
		requeststring = ''
		paramslist = []
		request_params = request.params.dict_of_lists()
		for param in request_params:
			if param not in ['username', 'password', 'token', 'logout', 'db_accronym']:
				for value in request_params[param]:
					paramslist.append('{0}={1}'.format(param, value))
		
		requeststring = '&'.join(paramslist)
		return requeststring
