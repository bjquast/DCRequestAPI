import logging
import logging.config
logging.config.fileConfig('logging.conf')
logger = logging.getLogger('elastic')

import json
import math

import pudb

from DCRequestAPI.lib.ElasticSearch.FieldDefinitions import fieldnames, fielddefinitions

class TermFilterQueries():
	def __init__(self, mapping):
		self.mapping = mapping


	def getTermFilterQueries(self, filters):
		pudb.set_trace()
		filter_queries = []
		
		for filter_name in filters:
			
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
