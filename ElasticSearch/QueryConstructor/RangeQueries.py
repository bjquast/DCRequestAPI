import logging
import logging.config
logging.config.fileConfig('logging.conf')
logger = logging.getLogger('elastic_queries')

import pudb

from ElasticSearch.FieldDefinitions import FieldDefinitions
from ElasticSearch.QueryConstructor.QueryConstructor import QueryConstructor


class RangeQueries(QueryConstructor):
	def __init__(self, users_project_ids = [], source_fields = []):
		self.users_project_ids = users_project_ids
		self.source_fields = source_fields
		
		fielddefs = FieldDefinitions()
		if len(self.source_fields) <= 0:
			self.source_fields = fielddefs.range_fields
		
		QueryConstructor.__init__(self, fielddefs.fielddefinitions, self.source_fields)
		self.sort_queries_by_definitions()


	def setRangeQueries(self, range_filters):
		self.range_queries = {}
		
		for range_name in range_filters:
			if range_name in self.range_fields:
				range_bottom, range_top = range_filters[range_name]
				self.appendSimpleRangeQuery(range_name, range_bottom, range_top)
			if range_name in self.simple_restricted_fields:
				range_bottom, range_top = range_filters[range_name]
				self.appendSimpleRestrictedRangeQuery(range_name, range_bottom, range_top)
			elif range_name in self.nested_fields:
				range_bottom, range_top = range_filters[range_name]
				self.appendNestedRangeQuery(range_name, range_bottom, range_top)
			elif range_name in self.nested_restricted_fields:
				range_bottom, range_top = range_filters[range_name]
				self.appendNestedRestrictedRangeQuery(range_name, range_bottom, range_top)
		
		return


	def appendSimpleRangeQuery(self, range_name, range_bottom, range_top):
		
		range_type = self.getRangeType(self.simple_fields[range_name])
		if range_type == 'date':
			range_query = {
				"range": {
					self.simple_fields[range_name]['field_query']: {
						"gte": range_bottom, 
						"lte": range_top
					}
				}
			}
			
			self.range_queries[range_name].append(range_query)
		
		elif range_type == 'number':
			range_query = {
				"range": {
					self.simple_fields[range_name]['field_query']: {
						"gte": range_bottom, 
						"lte": range_top
					}
				}
			}
			
			self.range_queries[range_name].append(range_query)
		
		return


	def appendSimpleRestrictedRangeQuery(self, range_name, filter_values):
		if range_name not in self.term_queries:
			self.term_queries[range_name] = []
		
		case_insensitive = self.getCaseInsensitiveValue(self.simple_restricted_fields[range_name])
		filter_values = self.replaceBooleanValues(self.simple_restricted_fields[range_name], filter_values)
		withholdterms = [{"term": {withholdfield: "false"}} for withholdfield in self.simple_restricted_fields[range_name]['withholdflags']]
		
		for filter_value in filter_values:
			termquery = {
					"bool": {
						"must": [
							{
								"term": {
									self.simple_restricted_fields[range_name]['field_query']: {
										"value": filter_value, 
										"case_insensitive": case_insensitive
									}
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
			
			self.term_queries[range_name].append(termquery)
		
		return


	def appendNestedRangeQuery(self, range_name, filter_values):
		if range_name not in self.term_queries:
			self.term_queries[range_name] = []
		
		case_insensitive = self.getCaseInsensitiveValue(self.nested_fields[range_name])
		filter_values = self.replaceBooleanValues(self.nested_fields[range_name], filter_values)
		
		for filter_value in filter_values:
			termquery = {
				"nested": {
					"path": self.nested_fields[range_name]['path'],
					"query": {
						"bool": {
							"must": [
								{
									"term": {
										self.nested_fields[range_name]['field_query']: {
											"value": filter_value, 
											"case_insensitive": case_insensitive
										}
									}
								}
							],
							"filter": []
						}
					}
				}
			}
			
			if range_name in self.subfilters:
				terms_sub_filter = {
					'terms': self.subfilters[range_name]
				}
				termquery['nested']['query']['bool']['filter'].append(terms_sub_filter)
		
			self.term_queries[range_name].append(termquery)
		
		return


	def appendNestedRestrictedRangeQuery(self, range_name, filter_values):
		if range_name not in self.term_queries:
			self.term_queries[range_name] = []
		
		case_insensitive = self.getCaseInsensitiveValue(self.nested_restricted_fields[range_name])
		filter_values = self.replaceBooleanValues(self.nested_restricted_fields[range_name], filter_values)
		withholdterms = [{"term": {withholdfield: "false"}} for withholdfield in self.nested_restricted_fields[range_name]['withholdflags']]
		
		for filter_value in filter_values:
			termquery = {
				"nested": {
					"path": self.nested_restricted_fields[range_name]['path'],
					"query": {
						"bool": {
							"must": [
								{
									"term": {
										self.nested_restricted_fields[range_name]['field_query']: {
											"value": filter_value, 
											"case_insensitive": case_insensitive
										}
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
							"minimum_should_match": 1,
							"filter": []
						}
					}
				}
			}
			
			if range_name in self.subfilters:
				terms_sub_filter = {
					'terms': self.subfilters[range_name]
				}
				termquery['nested']['query']['bool']['filter'].append(terms_sub_filter)
			
			self.term_queries[range_name].append(termquery)
		
		return


