import logging
import logging.config
logging.config.fileConfig('logging.conf')
logger = logging.getLogger('elastic_queries')

import pudb

from ElasticSearch.QueryConstructor.QueryConstructor import QueryConstructor

class StringQueries(QueryConstructor):
	def __init__(self, users_project_ids = [], source_fields = [], connector = 'AND'):
		QueryConstructor.__init__(self)
		
		self.users_project_ids = users_project_ids
		self.source_fields = source_fields
		if len(self.source_fields) <= 0:
			self.source_fields = self.fieldconf.term_fields
		
		self.connector = connector
		self.string_type = 'simple_query_string'
		
		self.sort_queries_by_definitions()
		
	
	def setQueryList(self, query_dicts):
		# TODO: when the source_fields and connectors are set in the constructor, there is no reason to have a list of query dicts here?
		# TODO: the string to search for should be enough
		self.query_list = []
		for query_dict in query_dicts:
			self.query_string = query_dict['term']
			self.__setQueryType()
			if self.string_type == 'query_string':
				self.__escapeReservedCharacters()
			self.__replaceWildcards()
			
			self.appendSimpleStringQueries()
			self.appendSimpleRestrictedStringQueries()
			self.appendNestedStringQueries()
			self.appendNestedRestrictedStringQueries()
		return


	def getQueries(self, query_dicts):
		"""
		get the queries put together by the connector value set in the constructor.
		TODO: not tested yet!
		"""
		string_queries = []
		self.setQueryList(query_dicts)
		
		if self.connector.upper() == 'AND':
			must_query = {'bool': {'must': []}}
			if len(self.query_list) == 1:
				must_query['bool']['must'] = self.query_list
			
			elif len(self.query_list) > 1:
				# query in more fields must be added as should query because the string is found when it is only in one of the fields
				should_sub_dict = {
					'bool': {
							'should': [],
							'minimum_should_match': 1
						}
				}
				should_sub_dict['bool']['should'] = self.query_list
				must_query['bool']['must'].append(should_sub_dict)
			string_queries.append(must_query)
		
		elif self.connector.upper() == 'OR':
			should_query = {'bool': {'should':[], 'minimum_should_match': 1}}
			for query in self.query_list:
				should_query['bool']['should'].append(query)
			string_queries.append(should_query)
		
		return string_queries

	
	'''
	def getUnconnectedQueryList(self, query_dicts):
		"""
		just return a list of ES query dictionaries, do not connect them by the connector
		this is in contrast to TermFilterQueries where the queries are connected within the class
		"""
		self.setQueryList(query_dicts)
		return self.query_list
	'''

	def __setQueryType(self):
		if self.query_string.startswith('*') or self.query_string.startswith('?') or self.query_string.startswith('%'):
			self.string_type = 'query_string'
			#self.escapeReservedCharacters
		else:
			self.string_type = 'simple_query_string'
		return

	
	def __escapeReservedCharacters(self):
		reserved_characters = ['+', '-', '=', '&', '|', '!', '(', ')', '{', '}', '[', ']', '^', '~', ':', '/']
		count = self.query_string.count('"')
		if count % 2 != 0:
			reserved_characters.append('"')
		
		for character in reserved_characters:
			self.query_string = self.query_string.replace(character, r'\{0}'.format(character))
		for character in ['>', '<']:
			self.query_string = self.query_string.replace(character, '?')
			pass
			#self.query_string = self.query_string.replace(character, '*')
		return

	def __replaceWildcards(self):
		wildcards = ['%']
		for character in wildcards:
			self.query_string = self.query_string.replace(character, r'*')
		return

	
	def appendSimpleStringQueries(self):
		search_fields = []
		for field in self.simple_fields:
			search_fields.append(self.getStringQuerySearchField(field, self.simple_fields[field]))
		
		if len(search_fields) > 0:
			query = {
				self.string_type: {
					'query': self.query_string,
					'fields': search_fields,
					'default_operator': 'AND'
				}
			}
			self.query_list.append(query)
		return

	
	def appendNestedStringQueries(self):
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
										'query': self.query_string,
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
	
	def appendSimpleRestrictedStringQueries(self):
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
								'query': self.query_string,
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
	
	def appendNestedRestrictedStringQueries(self):
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
										'query': self.query_string,
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
