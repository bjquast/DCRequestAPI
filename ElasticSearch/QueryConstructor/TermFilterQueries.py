import logging
import logging.config
logging.config.fileConfig('logging.conf')
logger = logging.getLogger('elastic_queries')

import pudb

from ElasticSearch.FieldDefinitions import FieldDefinitions
from ElasticSearch.QueryConstructor.QueryConstructor import QueryConstructor


class TermFilterQueries(QueryConstructor):
	def __init__(self, users_project_ids = [], source_fields = [], connector = 'AND'):
		self.users_project_ids = users_project_ids
		self.source_fields = source_fields
		self.connector = connector
		
		fielddefs = FieldDefinitions()
		if len(self.source_fields) <= 0:
			self.source_fields = fielddefs.bucketfields
			self.source_fields.extend(fielddefs.hierarchy_query_fields)
		
		QueryConstructor.__init__(self, fielddefs.fielddefinitions, self.source_fields)
		self.sort_queries_by_definitions()
		self.setSubFilters()


	def getTermFilterQueries(self, filters):
		self.term_queries = {}
		
		for filter_key in filters:
			if filter_key in self.simple_fields:
				filter_values = filters[filter_key]
				self.appendSimpleTermQuery(filter_key, filter_values)
			if filter_key in self.simple_restricted_fields:
				filter_values = filters[filter_key]
				self.appendSimpleRestrictedTermQuery(filter_key, filter_values)
			elif filter_key in self.nested_fields:
				filter_values = filters[filter_key]
				self.appendNestedTermQuery(filter_key, filter_values)
			elif filter_key in self.nested_restricted_fields:
				filter_values = filters[filter_key]
				self.appendNestedRestrictedTermQuery(filter_key, filter_values)
		
		filter_queries = []
		
		if self.connector.upper() == 'AND':
			for filter_key in self.term_queries:
				if len(self.term_queries[filter_key]) > 1:
					should_query = {'bool': {'should': self.term_queries[filter_key], 'minimum_should_match': 1}}
					filter_queries.append(should_query)
				elif len(self.term_queries[filter_key]) == 1:
					filter_queries.append(self.term_queries[filter_key][0])
		
		elif self.connector.upper() == 'OR':
			should_query = {'bool': {'should':[], 'minimum_should_match': 1}}
			for filter_key in self.term_queries:
				should_query['bool']['should'].extend(self.term_queries[filter_key])
			filter_queries.append(should_query)
		
		return filter_queries


	def appendSimpleTermQuery(self, filter_key, filter_values):
		
		if filter_key not in self.term_queries:
			self.term_queries[filter_key] = []
		
		case_insensitive = self.getCaseInsensitiveValue(self.simple_fields[filter_key])
		filter_values = self.replaceBooleanValues(self.simple_fields[filter_key], filter_values)
		
		for filter_value in filter_values:
			termquery = {
				"term": {
					self.simple_fields[filter_key]['field_query']: {
						"value": filter_value, 
						"case_insensitive": case_insensitive
					}
				}
			}
			
			self.term_queries[filter_key].append(termquery)
		
		return


	def appendSimpleRestrictedTermQuery(self, filter_key, filter_values):
		if filter_key not in self.term_queries:
			self.term_queries[filter_key] = []
		
		case_insensitive = self.getCaseInsensitiveValue(self.simple_restricted_fields[filter_key])
		filter_values = self.replaceBooleanValues(self.simple_restricted_fields[filter_key], filter_values)
		withholdterms = [{"term": {withholdfield: "false"}} for withholdfield in self.simple_restricted_fields[filter_key]['withholdflags']]
		
		for filter_value in filter_values:
			termquery = {
					"bool": {
						"must": [
							{
								"term": {
									self.simple_restricted_fields[filter_key]['field_query']: {
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
			
			self.term_queries[filter_key].append(termquery)
		
		return


	def appendNestedTermQuery(self, filter_key, filter_values):
		if filter_key not in self.term_queries:
			self.term_queries[filter_key] = []
		
		case_insensitive = self.getCaseInsensitiveValue(self.nested_fields[filter_key])
		filter_values = self.replaceBooleanValues(self.nested_fields[filter_key], filter_values)
		
		for filter_value in filter_values:
			termquery = {
				"nested": {
					"path": self.nested_fields[filter_key]['path'],
					"query": {
						"bool": {
							"must": [
								{
									"term": {
										self.nested_fields[filter_key]['field_query']: {
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
			
			if filter_key in self.subfilters:
				terms_sub_filter = {
					'terms': self.subfilters[filter_key]
				}
				termquery['nested']['query']['bool']['filter'].append(terms_sub_filter)
		
			self.term_queries[filter_key].append(termquery)
		
		return


	def appendNestedRestrictedTermQuery(self, filter_key, filter_values):
		if filter_key not in self.term_queries:
			self.term_queries[filter_key] = []
		
		case_insensitive = self.getCaseInsensitiveValue(self.nested_restricted_fields[filter_key])
		filter_values = self.replaceBooleanValues(self.nested_restricted_fields[filter_key], filter_values)
		withholdterms = [{"term": {withholdfield: "false"}} for withholdfield in self.nested_restricted_fields[filter_key]['withholdflags']]
		
		for filter_value in filter_values:
			termquery = {
				"nested": {
					"path": self.nested_restricted_fields[filter_key]['path'],
					"query": {
						"bool": {
							"must": [
								{
									"term": {
										self.nested_restricted_fields[filter_key]['field_query']: {
											"value": filter_value, 
											"case_insensitive": case_insensitive
										}
									}
								}
							],
							"should": [
								# need to use the DB_ProjectID within the path for nested objects otherwise the filter fails
								{"terms": {"{0}.DB_ProjectID".format(self.nested_restricted_fields[filter_key]['path']): self.users_project_ids}},
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
			
			if filter_key in self.subfilters:
				terms_sub_filter = {
					'terms': self.subfilters[filter_key]
				}
				termquery['nested']['query']['bool']['filter'].append(terms_sub_filter)
			
			self.term_queries[filter_key].append(termquery)
		
		return


	
	'''
			filter_path = filter_name.replace('.', '.properties.').split('.')
			
			try:
				mapping = self.mapping
				for path_element in filter_path:
					element_mapping = mapping[path_element]
			
			except KeyError:
				continue
			
			filter_type = None
			if element_mapping['type'] == 'keyword':
				filter_type = 'term'
				filter_name_string = "{0}"
			
			elif 'fields' in element_mapping and 'keyword' in element_mapping['fields']:
				filter_type = 'term'
				filter_name_string = "{0}.keyword"
			
			else:
				continue
			
			if len(filters[filter_name]) > 1:
				term_queries = []
				for filter_value in filters[filter_name]:
					term_queries.append({"term": {filter_name_string.format(filter_name): {"value": filter_value, "case_insensitive": "true"}}})
				should_query = {'bool': {'should': term_queries, 'minimum_should_match': 1}}
				
				filter_queries.append(should_query)
			
			elif len(filters[filter_name]) == 1:
				filter_queries.append({"term": {filter_name_string.format(filter_name): {"value": filters[filter_name][0], "case_insensitive": "true"}}})
		
		return filter_queries
		
		'''
