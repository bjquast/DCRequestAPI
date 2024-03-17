import logging
import logging.config
logging.config.fileConfig('logging.conf')
logger = logging.getLogger('elastic_queries')

import pudb

from ElasticSearch.FieldDefinitions import FieldDefinitions
from ElasticSearch.QueryConstructor.QuerySorter import QuerySorter

class TreeQueries(QuerySorter):
	def __init__(self, users_project_ids = [], source_fields = []):
		self.users_project_ids = users_project_ids
		self.source_fields = source_fields
		
		fielddefs = FieldDefinitions()
		if len(self.source_fields) <= 0:
			self.source_fields = fielddefs.tree_query_fields
		
		QuerySorter.__init__(self, fielddefs.fielddefinitions, self.source_fields)
		self.sort_queries_by_definitions()


	def setNestedRootQuery(self, rootlevel = 0):
		for field in in self.nested_fields:
		rootquery = {
			"""
			
			
			"""
		}
