import logging
import logging.config
logging.config.fileConfig('logging.conf')
logger = logging.getLogger('elastic_queries')

import pudb

from ElasticSearch.FieldDefinitions import FieldDefinitions
from ElasticSearch.QueryConstructor.QueryConstructor import QueryConstructor


class StackedInnerQuery(QueryConstructor):
	def __init__(self, query_dict, users_project_ids = []):
		self.query_dict = query_dict
		self.users_project_ids = users_project_ids
		
		fielddefs = FieldDefinitions()
		self.source_fields = fielddefs.fieldnames
		
		self.readQueryDict()
		
		QueryConstructor.__init__(self, fielddefs.fielddefinitions, self.query_dict['fields'])
		



	def readQueryDict(self):
		self.single_query_dicts = []
		
		if len(self.query_dict['terms']) > 0 and len(self.query_dict['terms']) == len(self.query_dict['fields']):
			
			# check if 'all fields' are selected
			for i in range(len(self.query_dict['terms'])):
				if self.query_dict['fields'][i] == 'all fields':
					
					query_dict = {
						'term': self.query_dict['terms'][i],
						'fields': self.source_fields
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


	def appendSimpleStringQueries(self, query_string):
		for field in self.simple_fields:
			search_field = self.getStringQuerySearchField(field, self.simple_fields[field])
			
			query = {
				'simple_query_string': {
					'query': query_string,
					'fields': [search_field]
				}
			}
			self.query_list.append(query)
		return


	def appendNestedStringQueries(self, query_string):
		for field in self.nested_fields:
			search_field = self.getStringQuerySearchField(field, self.nested_fields[field])
			
			query = {
				'nested': {
					'path': self.nested_fields[field]['path'],
					'query': { 
						'bool': {
							'must': [
								{
									'simple_query_string': {
										'query': query_string,
										'fields': [search_field]
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
		for field in self.simple_restricted_fields:
			search_field = self.getStringQuerySearchField(field, self.simple_restricted_fields[field])
			withholdterms = [{"term": {withholdfield: "false"}} for withholdfield in self.simple_restricted_fields[field]['withholdflags']]
			
			query = {
				'bool': {
					'must': [
						{
							'simple_query_string': {
								'query': query_string,
								'fields': [search_field]
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
									'simple_query_string': {
										'query': query_string,
										'fields': [search_field]
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
