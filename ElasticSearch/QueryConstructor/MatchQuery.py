import logging
import logging.config
logging.config.fileConfig('logging.conf')
logger = logging.getLogger('elastic_queries')

import pudb

from ElasticSearch.FieldDefinitions import FieldDefinitions
from ElasticSearch.QueryConstructor.QueryConstructor import QueryConstructor


class MatchQuery(QueryConstructor):
	def __init__(self, users_project_ids = [], source_fields = [], operator = 'AND', connector = 'AND'):
		self.users_project_ids = users_project_ids
		self.source_fields = source_fields
		self.operator = operator.upper()
		if self.operator not in ['AND', 'OR']:
			self.operator = 'AND'
		
		self.connector = connector
		if self.connector not in ['AND', 'OR']:
			self.connector = 'AND'
			
		
		fielddefs = FieldDefinitions()
		if len(self.source_fields) <= 0:
			self.source_fields = fielddefs.fieldnames
		
		QueryConstructor.__init__(self, fielddefs.fielddefinitions, self.source_fields)
		self.sort_queries_by_definitions()



	def appendSimpleMatchQuery(self, i, query_string):
		simple_multi_match = {
			'multi_match': {
				'query': query_string, 
				'fields': [fieldname for fieldname in self.simple_fields],
				'operator': self.operator
			}
		}
		self.match_queries_dict[i].append(simple_multi_match)
		return


	def appendNestedMatchQueries(self, i, query_string):
		for fieldname in self.nested_fields:
			query = {
				'nested': {
					'path': self.nested_fields[fieldname]['path'],
					'query': { 
						'bool': {
							'must': [
								{
									'match': {
										fieldname: {
											'query': query_string,
											'operator': self.operator
										}
									}
								}
							]
						}
					}
				}
			}
			
			self.match_queries_dict[i].append(query)
		return


	def appendSimpleRestrictedMatchQueries(self, i, query_string):
		for fieldname in self.simple_restricted_fields:
			query = {
				'bool': {
					'must': [
						{
							'match': {
								fieldname: {
									'query': query_string,
									'operator': self.operator
								}
							}
						}
					],
					'filter': [
						{
							'bool': {
								'should': [
									{"terms": {"Projects.DB_ProjectID": self.users_project_ids}},
									{"term": {self.simple_restricted_fields[fieldname]['withholdflag']: "false"}}
								],
								"minimum_should_match": 1
							}
						}
					]
				}
			}
			self.match_queries_dict[i].append(query)
		return


	def appendNestedRestrictedMatchQueries(self, i, query_string):
		for fieldname in self.nested_restricted_fields:
			query = {
				'nested': {
					'path': self.nested_restricted_fields[fieldname]['path'],
					'query': {
						'bool': {
							'must': [
								{
									'match': {
										fieldname: {
											'query': query_string,
											'operator': self.operator
										}
									}
								}
							],
							'filter': [
								{
									'bool': {
										'should': [
											# need to use the DB_ProjectID within the path for nested objects otherwise the filter fails
											{"terms": {"{0}.DB_ProjectID".format(self.nested_restricted_fields[fieldname]['path']): self.users_project_ids}},
											{"term": {self.nested_restricted_fields[fieldname]['withholdflag']: "false"}}
										],
										"minimum_should_match": 1
									}
								}
							]
						}
					}
				}
			}
			self.match_queries_dict[i].append(query)
		return


	def getMatchQuery(self, query_strings = []):
		#pudb.set_trace()
		self.match_query = None
		self.query_strings = query_strings
		
		if len(self.query_strings) > 0:
			
			#self.match_queries_list = []
			self.match_queries_dict = {}
			
			# use i as key not the query string it self because it might be anything?!
			for i in range(len(self.query_strings)):
				if self.query_strings[i] is not None and len(self.query_strings[i]) > 0:
					
					self.match_queries_dict[i] = []
					
					if len(self.simple_fields) > 0:
						self.appendSimpleMatchQuery(i, self.query_strings[i])
					
					if len(self.nested_fields) > 0:
						self.appendNestedMatchQueries(i, self.query_strings[i])
					
					if len(self.simple_restricted_fields) > 0:
						self.appendSimpleRestrictedMatchQueries(i, self.query_strings[i])
					
					if len(self.nested_restricted_fields) > 0:
						self.appendNestedRestrictedMatchQueries(i, self.query_strings[i])
			
			if self.connector == 'OR':
				self.match_query = {
					'bool': {
						'should': [],
						'minimum_should_match': 1
					}
				}
				
				for i in self.match_queries_dict:
					self.match_query['bool']['should'].extend(self.match_queries_dict[i])
				
				if len(self.match_query['bool']['should']) <= 0:
					self.match_query = None
			
			else:
				self.match_query = {
					'bool': {
						'must': []
					}
				}
				# must be a sequence of should queries to allow for a match in a single field
				for i in self.match_queries_dict:
					if len(self.match_queries_dict[i]) > 0:
						query_dict = {
							'bool': {
								'should': [],
								'minimum_should_match': 1
							}
						}
						
						query_dict['bool']['should'].extend(self.match_queries_dict[i])
						self.match_query['bool']['must'].append(query_dict)
				
				if len(self.match_query['bool']['must']) <= 0:
					self.match_query = None
			
			return self.match_query
		

