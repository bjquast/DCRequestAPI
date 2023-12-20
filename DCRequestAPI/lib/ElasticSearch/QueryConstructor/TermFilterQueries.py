import logging
import logging.config
logging.config.fileConfig('logging.conf')
logger = logging.getLogger('elastic')

import json
import math

import pudb

from DCRequestAPI.lib.ElasticSearch.ES_Mappings import MappingsDict

class TermFilterQueries():
	def __init__(self, mapping):
		self.mapping = mapping


	def getTermFilterQueries(self, filters):
		filter_queries = []
		
		for filter_name in filters:
			
			filter_path = filter_name.replace('.', '.properties.').split('.')
			
			mapping = self.mapping
			for path_element in filter_path:
				mapping = mapping[path_element]
			
			filter_type = None
			if mapping['type'] == 'keyword':
				filter_type = 'term'
				filter_name_string = "{0}"
			
			elif 'keyword' in mapping['fields']:
				filter_type = 'term'
				filter_name_string = "{0}.keyword"
			
			if filter_type is not None:
				if len(filters[filter_name]) > 1:
					term_queries = []
					for filter_value in filters[filter_name]:
						term_queries.append({"term": {filter_name_string.format(filter_name): {"value": filter_value, "case_insensitive": "true"}}})
					should_query = {'bool': {'should': term_queries, 'minimum_should_match': 1}}
					
					filter_queries.append(should_query)
				
				elif len(filters[filter_name]) == 1:
					filter_queries.append({"term": {filter_name_string.format(filter_name): {"value": filters[filter_name][0], "case_insensitive": "true"}}})
		
		return filter_queries
