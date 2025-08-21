import logging
import logging.config
logging.config.fileConfig('logging.conf')
logger = logging.getLogger('elastic_queries')

import pudb

from ElasticSearch.QueryConstructor.QueryConstructor import QueryConstructor


class StackedQueries():
	def __init__(self, search_params, users_project_ids):
		self.search_params = search_params
		self.users_project_ids = users_project_ids
		
		self.query_stack = {
			'bool': {
				'must': []
			}
		}
		self.create_query_stack()


	def create_query_stack(self):
		"""
		iterate over the stack_queries list wich contains dicts with:
		{
			['string']: list,
			['date_from']: list,
			['date_to']: list,
			['field']: list,
			['query_type']: list,
			['outer_connector']: string 'AND'/'OR',
			['inner_connector']: string 'AND'/'OR'
		}
		
		the elements lists define a sub query each, so if there are 2 strings and 2 fields etc. these are 2 sub queries with:
		query[0] = {'string' = search_params['stack_queries'][0]['string'][0], 'field': search_params['stack_queries'][0]['field'][0], ...}
		query[1] = {'string' = search_params['stack_queries'][0]['string'][1], 'field': search_params['stack_queries'][0]['field'][1], ...}
		
		the queries are separated by StackedInnerQuery.readQueryDict()
		
		inner queries are appended to a list of queries connected to each other according to the inner_connector
		these inner queries are then appended to a list of outer queries according to the outer_connector
		
		TODO: this has to be adopted for separate requests on strings and date ranges and other query types
		"""
		pudb.set_trace()
		outer_query = StackedOuterQuery()
		
		if 'stack_queries' in self.search_params:
			# set outer connector to AND for the first query, otherwise it might result in all documents matched when it starts with an OR query and it is the only query
			if len(self.search_params['stack_queries']) > 0:
				self.search_params['stack_queries'][0]['outer_connector'] = 'AND'
			
			# iterate over the outer queries,
			# the StackedInnerQuery class then iterates over the inner queries
			for stack_query in self.search_params['stack_queries']:
				inner_query = StackedInnerQuery(stack_query, users_project_ids = self.users_project_ids)
				inner_string_query = inner_query.getInnerStackQuery()
				
				if inner_string_query is not None:
					if stack_query['outer_connector'] == 'AND':
						outer_query.addMustQuery(inner_string_query)
					else:
						outer_query.addShouldQuery(inner_string_query)
				
			
			if len(outer_query.query_stack) > 0:
				# add them all to must to ensure that the stacked query results must be fullfilled when connected with other query types
				self.query_stack = outer_query.query_stack
		return


class StackedInnerQuery(QueryConstructor):
	def __init__(self, query_dict, users_project_ids = []):
		QueryConstructor.__init__(self)
		
		self.request_dict = query_dict
		self.users_project_ids = users_project_ids
		
		self.source_fields = self.request_dict['field']
		
		self.readQueryDict()
		
		self.string_type = 'simple_query_string'


	def readQueryDict(self):
		"""
		# iterate over the inner queries and set fields for string queries when 'all fields' is chosen by the user
		"""
		
		self.single_query_dicts = []
		
		
		if len(self.request_dict['query_type']) > 0 and len(self.request_dict['string']) == len(self.request_dict['field']):
			
			
			# check if 'all fields' are selected
			for i in range(len(self.request_dict['query_type'])):
				if self.request_dict['query_type'][i] == 'term' and self.request_dict['string'][i]:
					if self.request_dict['field'][i] == 'all fields':
						
						query_dict = {
							'term': self.request_dict['string'][i],
							'fields': self.fieldconf.stacked_term_fields
						}
						self.single_query_dicts.append(query_dict)
					else:
						query_dict = {
							'term': self.request_dict['string'][i],
							'fields': [self.request_dict['field'][i]]
						}
						self.single_query_dicts.append(query_dict)
				elif self.request_dict['query_type'][i] == 'date' and (self.request_dict['date_from'][i] or self.request_dict['date_from'][i]):
					if self.request_dict['field'][i] in self.fieldconf.date_fields:
						query_dict = {
							'date_from': self.request_dict['date_from'][i],
							'date_to': self.request_dict['date_to'][i],
							'fields': [self.request_dict['field'][i]]
						}
						self.single_query_dicts.append(query_dict)
			
		else:
			raise ValueError('count of terms and fields must be the same')
		
		return


	def setQueryType(self, querystring):
		if querystring.startswith('*') or querystring.startswith('?') or querystring.startswith('%'):
			self.string_type = 'query_string'
			#self.escapeReservedCharacters
		else:
			self.string_type = 'simple_query_string'
		return


	def escapeReservedCharacters(self, query_string):
		reserved_characters = ['+', '-', '=', '&', '|', '!', '(', ')', '{', '}', '[', ']', '^', '~', ':', '/']
		count = query_string.count('"')
		if count % 2 != 0:
			reserved_characters.append('"')
		
		for character in reserved_characters:
			#pass
			query_string = query_string.replace(character, r'\{0}'.format(character))
		for character in ['>', '<']:
			query_string = query_string.replace(character, '?')
			pass
			#query_string = query_string.replace(character, '*')
		
		return query_string


	def replaceWildcards(self, query_string):
		wildcards = ['%']
		
		for character in wildcards:
			query_string = query_string.replace(character, r'*')
		
		return query_string


	def appendSimpleStringQueries(self, query_string):
		self.setQueryType(query_string)
		if self.string_type == 'query_string':
			query_string = self.escapeReservedCharacters(query_string)
		query_string = self.replaceWildcards(query_string)
		
		search_fields = []
		for field in self.simple_fields:
			search_fields.append(self.getStringQuerySearchField(field, self.simple_fields[field]))
		
		if len(search_fields) > 0:
			query = {
				self.string_type: {
					'query': query_string,
					'fields': search_fields,
					'default_operator': 'AND'
				}
			}
			self.query_list.append(query)
		return


	def appendNestedStringQueries(self, query_string):
		self.setQueryType(query_string)
		if self.string_type == 'query_string':
			query_string = self.escapeReservedCharacters(query_string)
		
		query_string = self.replaceWildcards(query_string)
		
		search_fields = []
		for field in self.nested_fields:
			search_field = self.getStringQuerySearchField(field, self.nested_fields[field])
			
			query = {
				'nested': {
					'path': self.nested_fields[field]['path'],
					'query': { 
						'bool': {
							'must': [
								{
									self.string_type: {
										'query': query_string,
										'fields': [search_field],
										'default_operator': 'AND'
									}
								}
							]
						}
					}
				}
			}
			
			self.query_list.append(query)
		return


	def appendSimpleRestrictedStringQueries(self, query_string):
		self.setQueryType(query_string)
		if self.string_type == 'query_string':
			query_string = self.escapeReservedCharacters(query_string)
		
		query_string = self.replaceWildcards(query_string)
		
		# restricted fields must be queried one by one because they all have their own withholdterms
		# that can not be queried together in one question
		for field in self.simple_restricted_fields:
			search_field = self.getStringQuerySearchField(field, self.simple_restricted_fields[field])
			withholdterms = [{"term": {withholdfield: "false"}} for withholdfield in self.simple_restricted_fields[field]['withholdflags']]
			
			query = {
				'bool': {
					'must': [
						{
							self.string_type: {
								'query': query_string,
								'fields': [search_field],
								'default_operator': 'AND'
							}
						}
					],
					'filter': [
						{
							'bool': {
								'should': [
									{"terms": {"Projects.DB_ProjectID": self.users_project_ids}},
									{
										"bool": {
											"must": withholdterms
										}
									}
								],
								"minimum_should_match": 1
							}
						}
					]
				}
			}
			self.query_list.append(query)
		return


	def appendNestedRestrictedStringQueries(self, query_string):
		self.setQueryType(query_string)
		if self.string_type == 'query_string':
			query_string = self.escapeReservedCharacters(query_string)
		
		query_string = self.replaceWildcards(query_string)
		
		# restricted fields must be queried one by one because they all have their own withholdterms
		# that can not be queried together in one question
		for field in self.nested_restricted_fields:
			search_field = self.getStringQuerySearchField(field, self.nested_restricted_fields[field])
			withholdterms = [{"term": {withholdfield: "false"}} for withholdfield in self.nested_restricted_fields[field]['withholdflags']]
			
			query = {
				'nested': {
					'path': self.nested_restricted_fields[field]['path'],
					'query': {
						'bool': {
							'must': [
								{
									self.string_type: {
										'query': query_string,
										'fields': [search_field],
										'default_operator': 'AND'
									}
								}
							],
							'filter': [
								{
									'bool': {
										'should': [
											# need to use the DB_ProjectID within the path for nested objects otherwise the filter fails
											{"terms": {"{0}.DB_ProjectID".format(self.nested_restricted_fields[field]['path']): self.users_project_ids}},
											{
												"bool": {
													"must": withholdterms
												}
											}
										],
										"minimum_should_match": 1
									}
								}
							]
						}
					}
				}
			}
			self.query_list.append(query)
		return



	def getInnerStackQuery(self):
		
		self.string_query = {
			'bool': {
				'should': [],
				'must': []
			}
		}
		
		# TODO: can this integrate the code from 
		
		for query_dict in self.single_query_dicts:
			
			self.set_source_fields(query_dict['fields'])
			self.sort_queries_by_definitions()
			
			# set the query_list for each query separately because i have to differentiate between queries in multiple fields and queries in one field when 
			# combining them with the AND inner connector
			self.query_list = []
			
			if query_dict['term'] is not None and len(query_dict['term']) > 0:
				
				if len(self.simple_fields) > 0:
					self.appendSimpleStringQueries(query_dict['term'])
				
				if len(self.nested_fields) > 0:
					self.appendNestedStringQueries(query_dict['term'])
				
				if len(self.simple_restricted_fields) > 0:
					self.appendSimpleRestrictedStringQueries(query_dict['term'])
				
				if len(self.nested_restricted_fields) > 0:
					self.appendNestedRestrictedStringQueries(query_dict['term'])
			
			if len(self.query_list) > 0:
				if self.request_dict['inner_connector'] == 'OR':
					self.string_query['bool']['should'].extend(self.query_list)
					self.string_query['bool']['minimum_should_match'] = 1
					
				
				else:
					
					# query within one field
					if len(self.query_list) == 1:
						self.string_query['bool']['must'].extend(self.query_list)
					# query in multiple fields
					elif len(self.query_list) > 1:
						query_dict = {
							'bool': {
								'should': [],
								'minimum_should_match': 1
							}
						}
						
						query_dict['bool']['should'].extend(self.query_list)
						self.string_query['bool']['must'].append(query_dict)
		
		if len(self.string_query['bool']['must']) < 1 and len(self.string_query['bool']['should']) < 1:
			self.string_query = None
		
		return self.string_query



class StackedOuterQuery():
	def __init__(self):
		
		self.should = []
		self.must = [] 
		
		self.query_stack = {
			'bool': {
				'must': [],
				'should': [],
				'minimum_should_match': 1
			}
		}


	def deleteEmptyElements(self):
		if 'should' in self.query_stack['bool'] and len(self.query_stack['bool']['should']) < 1:
			del self.query_stack['bool']['should']
			if 'minimum_should_match' in self.query_stack['bool']:
				del self.query_stack['bool']['minimum_should_match']
		if 'must' in self.query_stack['bool'] and len(self.query_stack['bool']['must']) < 1:
			del self.query_stack['bool']['must']


	def addShouldQuery(self, inner_query):
		self.deleteEmptyElements()
		
		if len(inner_query) > 0:
			new_outer_query = {
				'bool': {
					'should': [
						inner_query
					],
					'minimum_should_match': 1
				}
			}
			
			if len(self.query_stack) > 0:
				new_outer_query['bool']['should'].append(self.query_stack)
			
			self.query_stack = new_outer_query
		
		return


	def addMustQuery(self, inner_query):
		self.deleteEmptyElements()
		
		if len(inner_query) > 0:
			new_outer_query = {
				'bool': {
					'must': [
						inner_query
					]
				}
			}
			
			if len(self.query_stack) > 0:
				new_outer_query['bool']['must'].append(self.query_stack)
			
			self.query_stack = new_outer_query
		
		return
