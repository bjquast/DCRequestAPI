import logging
import logging.config
logging.config.fileConfig('logging.conf')
logger = logging.getLogger('elastic_queries')

import pudb

from ElasticSearch.QueryConstructor.QueryConstructor import QueryConstructor


class RangeQueries(QueryConstructor):
	def __init__(self, users_project_ids = []):
		QueryConstructor.__init__(self)
		
		self.users_project_ids = users_project_ids


	def setQueryList(self, range_requests):
		self.source_fields = []
		
		self.range_queries = []
		
		for range_request in range_requests:
			range_field = range_request['fields'][0]
			self.source_fields = range_request['fields']
			self.sort_queries_by_definitions()
			
			self.setRangeValues(range_request)
			
			if range_field in self.simple_fields:
				self.appendSimpleRangeQuery(range_field)
			elif range_field in self.simple_restricted_fields:
				self.appendSimpleRestrictedRangeQuery(range_field)
			elif range_field in self.nested_fields:
				self.appendNestedRangeQuery(range_field)
			elif range_field in self.nested_restricted_fields:
				self.appendNestedRestrictedRangeQuery(range_field)
		return


	def getQueries(self, range_requests, connector = 'AND'):
		self.connector = connector
		
		self.setQueryList(range_requests)
		
		connected_range_queries = []
		
		if self.connector.upper() == 'AND':
			must_query = {'bool': {'must':[]}}
			for query in self.range_queries:
				must_query['bool']['must'].append(query)
			connected_range_queries.append(must_query)
		
		else:
			should_query = {'bool': {'should':[], 'minimum_should_match': 1}}
			for query in self.range_queries:
				should_query['bool']['should'].append(query)
			connected_range_queries.append(should_query)
		
		return connected_range_queries


	def setRangeValues(self, range_request):
		self.gte_lte_values = {}
		if 'range_from' in range_request and range_request['range_from']:
			self.gte_lte_values['gte'] = range_request['range_from']
		if 'date_from' in range_request and range_request['date_from']:
			self.gte_lte_values['gte'] = range_request['date_from']
		if 'range_to' in range_request and range_request['range_to']:
			self.gte_lte_values['lte'] = range_request['range_to']
		if 'date_to' in range_request and range_request['date_to']:
			self.gte_lte_values['lte'] = range_request['date_to']
		return


	def appendSimpleRangeQuery(self, range_field):
		
		range_type = self.getRangeType(range_field)
		range_query = {
			"range": {
				self.simple_fields[range_field]['field_query']: self.gte_lte_values
			}
		}
		
		range_type = self.getRangeType(range_field)
		if range_type == 'date':
			range_query['range'][self.simple_fields[range_field]['field_query']]['format'] = "yyyy-MM-dd"
		
		self.range_queries.append(range_query)
		
		return


	def appendSimpleRestrictedRangeQuery(self, range_field, range_from, range_to):
		withholdterms = [{"term": {withholdfield: "false"}} for withholdfield in self.simple_restricted_fields[range_field]['withholdflags']]
		
		range_query = {
			"bool": {
				"must": [
					{
						"range": {
							self.simple_restricted_fields[range_field]['field_query']: self.gte_lte_values
						}
					}
				],
				"should": [
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
		
		range_type = self.getRangeType(range_field)
		if range_type == 'date':
			range_query['bool']['must'][0]['range'][self.simple_restricted_fields[range_field]['field_query']]['format'] = "yyyy-MM-dd"
		
		self.range_queries.append(range_query)
		
		return


	def appendNestedRangeQuery(self, range_field, range_from, range_to):
		
		range_query = {
			"nested": {
				"path": self.nested_fields[range_field]['path'],
				"query": {
					"bool": {
						"must": [
							{
								"range": {
									self.nested_fields[range_field]['field_query']: self.gte_lte_values
								}
							}
						]
					}
				}
			}
		}
		
		range_type = self.getRangeType(range_field)
		if range_type == 'date':
			range_query['nested']['query']['bool']['must'][0]['range'][self.nested_fields[range_field]['field_query']]['format'] = "yyyy-MM-dd"
		
		self.range_queries.append(range_query)
		
		
		return


	def appendNestedRestrictedRangeQuery(self, range_field, range_from, range_to):
		
		withholdterms = [{"term": {withholdfield: "false"}} for withholdfield in self.nested_restricted_fields[range_field]['withholdflags']]
		
		range_query = {
			"nested": {
				"path": self.nested_restricted_fields[range_name]['path'],
				"query": {
					"bool": {
						"must": [
							{
								"range": {
									self.nested_restricted_fields[range_field]['field_query']: self.gte_lte_values
								}
							}
						],
						"should": [
							# need to use the DB_ProjectID within the path for nested objects otherwise the filter fails
							{"terms": {"{0}.DB_ProjectID".format(self.nested_restricted_fields[range_name]['path']): self.users_project_ids}},
							{
								"bool": {
									"must": withholdterms
								}
							}
						],
						"minimum_should_match": 1
					}
				}
			}
		}
		
		range_type = self.getRangeType(range_field)
		if range_type == 'date':
			range_query['nested']['query']['bool']['must'][0]['range'][self.nested_restricted_fields[range_field]['field_query']]['format'] = "yyyy-MM-dd"
		
		self.range_queries.append(range_query)
		
		return


