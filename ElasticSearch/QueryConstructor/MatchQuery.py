import logging
import logging.config
logging.config.fileConfig('logging.conf')
logger = logging.getLogger('elastic_queries')

import pudb


from ElasticSearch.QueryConstructor.QuerySorter import QuerySorter


class MatchQuery(QuerySorter):
	def __init__(self, users_project_ids = [], source_fields = []):
		self.users_project_ids = users_project_ids
		
		QuerySorter.__init__(self, source_fields)
		self.sort_queries_by_definitions()



	def appendSimpleMatchQuery(self):
		simple_multi_match = {
			'multi_match': {
				'query': self.query_string, 
				'fields': [fieldname for fieldname in self.simple_fields]
			}
		}
		self.should_queries.append(simple_multi_match)
		return


	def appendNestedMatchQueries(self):
		
		for fieldname in self.nested_fields:
			query = {
				'nested': {
					'path': self.nested_fields[fieldname]['path'],
					'query': { 
						'bool': {
							'must': [
								{
									'match': {
										fieldname: self.query_string
									}
								}
							]
						}
					}
				}
			}
			
			self.should_queries.append(query)
		return


	def appendSimpleRestrictedMatchQueries(self):
		for fieldname in self.simple_restricted_fields:
			query = {
				'bool': {
					'must': [
						{
							'match': {
								fieldname: self.query_string
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
			self.should_queries.append(query)
		return


	def appendNestedRestrictedMatchQueries(self):
		for fieldname in self.nested_restricted_fields:
			query = {
				'nested': {
					'path': self.nested_restricted_fields[fieldname]['path'],
					'query': {
						'bool': {
							'must': [
								{
									'match': {
										fieldname: self.query_string
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
			self.should_queries.append(query)
		return


	def getMatchQuery(self, query_string):
		#pudb.set_trace()
		self.match_query = None
		self.query_string = query_string
		
		if self.query_string is not None and len(self.query_string) > 0:
			
			self.should_queries = []
			
			if len(self.simple_fields) > 0:
				self.appendSimpleMatchQuery()
			
			if len(self.nested_fields) > 0:
				self.appendNestedMatchQueries()
			
			if len(self.simple_restricted_fields) > 0:
				self.appendSimpleRestrictedMatchQueries()
			
			if len(self.nested_restricted_fields) > 0:
				self.appendNestedRestrictedMatchQueries()
			
			if len(self.should_queries) > 0:
				self.match_query = {
					'bool': {
						'should': [],
						"minimum_should_match": 1
					}
				}
				
				self.match_query['bool']['should'].extend(self.should_queries)
			
			else:
				self.match_query = None
			
			return self.match_query
		

