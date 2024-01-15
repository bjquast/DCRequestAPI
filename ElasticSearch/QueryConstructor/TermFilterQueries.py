import logging
import logging.config
logging.config.fileConfig('logging.conf')
logger = logging.getLogger('elastic_queries')

import json
import math

import pudb

from ElasticSearch.FieldDefinitions import fieldnames, fielddefinitions

class TermFilterQueries():
	def __init__(self, users_project_ids = []):
		self.users_project_ids = users_project_ids
		
		self.nested_fields = {}
		self.nested_restricted_fields = {}
		self.simple_fields = {}
		self.simple_restricted_fields = {}
		
		self.read_field_definitions()


	def read_field_definitions(self):
		for fieldname in fieldnames:
			if fieldname in fielddefinitions:
				if 'buckets' in fielddefinitions[fieldname] and 'path' in fielddefinitions[fieldname]['buckets'] and 'withholdflag' in fielddefinitions[fieldname]['buckets']:
					self.nested_restricted_fields[fieldname] = fielddefinitions[fieldname]['buckets']
				elif 'buckets' in fielddefinitions[fieldname] and 'path' in fielddefinitions[fieldname]['buckets'] and 'withholdflag' not in fielddefinitions[fieldname]['buckets']:
					self.nested_fields[fieldname] = fielddefinitions[fieldname]['buckets']
				elif 'buckets' in fielddefinitions[fieldname] and 'withholdflag' in fielddefinitions[fieldname]['buckets']:
					self.simple_restricted_fields[fieldname] = fielddefinitions[fieldname]['buckets']
				elif 'buckets' in fielddefinitions[fieldname]:
					self.simple_fields[fieldname] = fielddefinitions[fieldname]['buckets']
		return


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
		
		for filter_key in self.term_queries:
			if len(self.term_queries[filter_key]) > 1:
				should_query = {'bool': {'should': self.term_queries[filter_key], 'minimum_should_match': 1}}
				filter_queries.append(should_query)
			elif len(self.term_queries[filter_key]) == 1:
				filter_queries.append(self.term_queries[filter_key][0])
		
		return filter_queries


	def appendSimpleTermQuery(self, filter_key, filter_values):
		if filter_key not in self.term_queries:
			self.term_queries[filter_key] = []
		for filter_value in filter_values:
			termquery = {
				"term": {
					self.simple_fields[filter_key]['field_query']: {
						"value": filter_value, 
						"case_insensitive": "true"
					}
				}
			}
			
			self.term_queries[filter_key].append(termquery)
		
		return


	def appendSimpleRestrictedTermQuery(self, filter_key, filter_values):
		if filter_key not in self.term_queries:
			self.term_queries[filter_key] = []
		for filter_value in filter_values:
			termquery = {
					"bool": {
						"must": [
							{
								"term": {
									self.simple_restricted_fields[filter_key]['field_query']: {
										"value": filter_value, 
										"case_insensitive": "true"
									}
								}
							}
						],
						"should": [
							{"terms": {"Projects.ProjectID": self.users_project_ids}},
							{"term": {self.simple_restricted_fields[filter_key]['withholdflag']: "false"}}
						],
						"minimum_should_match": 1
					}
				}
			
			self.term_queries[filter_key].append(termquery)
		
		return


	def appendNestedTermQuery(self, filter_key, filter_values):
		if filter_key not in self.term_queries:
			self.term_queries[filter_key] = []
		
		for filter_value in filter_values:
			termquery = {
				"nested": {
					"path": self.nested_fields[filter_key]['path'],
					"query": {
						"term": {
							self.nested_fields[filter_key]['field_query']: {
								"value": filter_value, 
								"case_insensitive": "true"
							}
						}
					}
				}
			}
		
			self.term_queries[filter_key].append(termquery)
		
		return


	def appendNestedRestrictedTermQuery(self, filter_key, filter_values):
		if filter_key not in self.term_queries:
			self.term_queries[filter_key] = []
		
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
											"case_insensitive": "true"
										}
									}
								}
							],
							"should": [
								{"terms": {"Projects.ProjectID": self.users_project_ids}},
								{"term": {self.nested_restricted_fields[filter_key]['withholdflag']: "false"}}
							],
							"minimum_should_match": 1
						}
					}
				}
			}
			
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
