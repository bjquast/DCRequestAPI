import logging
import logging.config
logging.config.fileConfig('logging.conf')
logger = logging.getLogger('elastic_queries')

import pudb

from ElasticSearch.QueryConstructor.QueryConstructor import QueryConstructor


class StackedInnerQuery(QueryConstructor):
	def __init__(self, query_dict, users_project_ids = []):
		QueryConstructor.__init__(self)
		
		self.query_dict = query_dict
		self.users_project_ids = users_project_ids
		
		self.source_fields = self.query_dict['fields']
		
		self.readQueryDict()
		
		self.query_type = 'simple_query_string'



	def readQueryDict(self):
		self.single_query_dicts = []
		
		if len(self.query_dict['terms']) > 0 and len(self.query_dict['terms']) == len(self.query_dict['fields']):
			
			# check if 'all fields' are selected
			for i in range(len(self.query_dict['terms'])):
				if self.query_dict['fields'][i] == 'all fields':
					
					query_dict = {
						'term': self.query_dict['terms'][i],
						'fields': self.fieldconf.stacked_query_fields
					}
					self.single_query_dicts.append(query_dict)
			
				else:
					query_dict = {
						'term': self.query_dict['terms'][i],
						'fields': [self.query_dict['fields'][i]]
					}
					self.single_query_dicts.append(query_dict)
			
		else:
			raise ValueError('count of terms and fields must be the same')
		
		return


	def setQueryType(self, querystring):
		if querystring.startswith('*') or querystring.startswith('?') or querystring.startswith('%'):
			self.querytype = 'query_string'
			#self.escapeReservedCharacters
		else:
			self.querytype = 'simple_query_string'
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
		if self.querytype == 'query_string':
			query_string = self.escapeReservedCharacters(query_string)
		query_string = self.replaceWildcards(query_string)
		
		search_fields = []
		for field in self.simple_fields:
			search_fields.append(self.getStringQuerySearchField(field, self.simple_fields[field]))
		
		if len(search_fields) > 0:
			query = {
				self.querytype: {
					'query': query_string,
					'fields': search_fields,
					'default_operator': 'AND'
				}
			}
			self.query_list.append(query)
		return


	def appendNestedStringQueries(self, query_string):
		self.setQueryType(query_string)
		if self.querytype == 'query_string':
			query_string = self.escapeReservedCharacters(query_string)
		
		query_string = self.replaceWildcards(query_string)
		
		search_fields = []
		for field in self.nested_fields:
			search_fields.append(self.getStringQuerySearchField(field, self.nested_fields[field]))
		
		if len(search_fields) > 0:
			query = {
				'nested': {
					'path': self.nested_fields[field]['path'],
					'query': { 
						'bool': {
							'must': [
								{
									self.querytype: {
										'query': query_string,
										'fields': search_fields,
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
		if self.querytype == 'query_string':
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
							self.querytype: {
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
		if self.querytype == 'query_string':
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
									self.querytype: {
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
				if self.query_dict['inner_connector'] == 'OR':
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
