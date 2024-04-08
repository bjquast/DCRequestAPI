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
		
		self.readQueryDict()
		
		fielddefs = FieldDefinitions()
		
		QueryConstructor.__init__(self, fielddefs.fielddefinitions, self.query_dict['fields'])
		self.sort_queries_by_definitions()
		
		


	def readQueryDict(self):
		
		if len(self.query_dict['terms']) > 0 and len(self.query_dict['terms']) == len(self.query_dict['fields']):
			
			# check if 'all fields' are selected and if so: add a term and field for each available field
			for i in range(len(self.query_dict['terms'])):
				if self.query_dict['fields'][i] == 'all fields':
					new_fields = self.source_fields
					new_terms = [self.query_dict['terms'][i] for _ in self.source_fields]
					
					# insert the new lists into the old ones by slicing
					self.query_dict['fields'][i:i] = new_fields
					self.query_dict['terms'][i:i] = new_terms
		else:
			raise ValueError('count of terms and fields must be the same')
			self.query_dict['terms'] = []
		
		return


	def appendSimpleStringQueries(self, query_string):
		for field in self.simple_fields:
			query = {
				'query_string': {
					'query': query_string,
					'default_field': field
				}
			}
			self.query_list.append(query)
		return


	def appendNestedStringQueries(self, query_string):
		for field in self.nested_fields:
			query = {
				'nested': {
					'path': self.nested_fields[field]['path'],
					'query': { 
						'bool': {
							'must': [
								{
									'query_string': {
										'query': query_string,
										'default_field': field
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
			query = {
				'bool': {
					'must': [
						{
							'query_string': {
								'query': query_string,
								'default_field': field
							}
						}
					],
					'filter': [
						{
							'bool': {
								'should': [
									{"terms": {"Projects.DB_ProjectID": self.users_project_ids}},
									{"term": {self.simple_restricted_fields[field]['withholdflag']: "false"}}
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
			query = {
				'nested': {
					'path': self.nested_restricted_fields[field]['path'],
					'query': {
						'bool': {
							'must': [
								{
									'query_string': {
										'query': query_string,
										'default_field': field
									}
								}
							],
							'filter': [
								{
									'bool': {
										'should': [
											# need to use the DB_ProjectID within the path for nested objects otherwise the filter fails
											{"terms": {"{0}.DB_ProjectID".format(self.nested_restricted_fields[field]['path']): self.users_project_ids}},
											{"term": {self.nested_restricted_fields[field]['withholdflag']: "false"}}
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
		#pudb.set_trace()
		self.query_list = []
		
		for i in range(len(self.query_dict['terms'])):
			if self.query_dict['terms'][i] is not None and len(self.query_dict['terms'][i]) > 0:
			
				if len(self.simple_fields) > 0:
					self.appendSimpleStringQueries(self.query_dict['terms'][i])
				
				if len(self.nested_fields) > 0:
					self.appendNestedStringQueries(self.query_dict['terms'][i])
				
				if len(self.simple_restricted_fields) > 0:
					self.appendSimpleRestrictedStringQueries(self.query_dict['terms'][i])
				
				if len(self.nested_restricted_fields) > 0:
					self.appendNestedRestrictedStringQueries(self.query_dict['terms'][i])
			
		
		if self.query_dict['inner_connector'] == 'OR':
			self.string_query = {
				'bool': {
					'should': [],
					"minimum_should_match": 1
				}
			}
			
			self.string_query['bool']['should'].extend(self.query_list)
			
			if len(self.string_query['bool']['should']) <= 0:
				self.string_query = None
		
		else:
			self.string_query = {
				'bool': {
					'must': []
				}
			}
			
			
			if len(self.query_list) > 0:
				query_dict = {
					'bool': {
						'should': [],
						'minimum_should_match': 1
					}
				}
				
				query_dict['bool']['should'].extend(self.query_list)
				self.string_query['bool']['must'].append(query_dict)
			
			if len(self.string_query['bool']['must']) <= 0:
				self.string_query = None
		
		pudb.set_trace()
		return self.string_query



class StackedOuterQuery():
	def __init__(self):
		self.query_stack = {}


	def addAsOuterShouldQuery(self, inner_queries):
		outer_query['bool'] = {}
		outer_query['bool']['should'] = []
		
		if len(inner_queries) > 0:
			for query in inner_queries:
				outer_query['bool']['should'].append(query)
			
			outer_query['bool']['should'] = self.query_stack
			outer_query['bool']['minimum_should_match'] = 1
			self.query_stack = outer_query
		return


	def addAsOuterMustQuery(self, inner_queries):
		outer_query['bool'] = {}
		outer_query['bool']['must'] = []
		
		if len(inner_queries) > 0:
			for query in inner_queries:
				outer_query['bool']['must'].append(query)
			
			outer_query['bool']['must'] = self.query_stack
			self.query_stack = outer_query
		return
