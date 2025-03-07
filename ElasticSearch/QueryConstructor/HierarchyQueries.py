import logging
import logging.config
logging.config.fileConfig('logging.conf')
logger = logging.getLogger('elastic_queries')

import pudb

from ElasticSearch.FieldDefinitions import FieldDefinitions

class HierarchyQueries():
	def __init__(self, field, hierarchy_pathes = [], users_project_ids = []):
		self.field = field
		self.hierarchy_pathes = hierarchy_pathes
		self.users_project_ids = users_project_ids
		fielddefs = FieldDefinitions()
		self.fielddefinitions = fielddefs.fielddefinitions
		self.hierarchy_fields = fielddefs.hierarchy_query_fields
		
		self.hierarchies_query = {}
		
		self.read_buckets_definition()
		self.setHierarchiesQuery()
		


	def read_buckets_definition(self):
		
		if self.field in self.hierarchy_fields and self.field in self.fielddefinitions:
			if 'buckets' in self.fielddefinitions[self.field] and 'path_hierarchy_field' in self.fielddefinitions[self.field]['buckets'] and 'withholdflags' not in self.fielddefinitions[self.field]['buckets']:
				self.simple_fields = self.fielddefinitions[self.field]['buckets']
			if 'buckets' in self.fielddefinitions[self.field] and 'path_hierarchy_field' in self.fielddefinitions[self.field]['buckets'] and 'withholdflags' in self.fielddefinitions[self.field]['buckets']:
				self.simple_restricted_fields = self.fielddefinitions[self.field]['buckets']
			else:
				self.simple_fields = []
				self.simple_restricted_fields = []
		return



	def setHierarchiesQuery(self):
		self.hierarchies_query = {}
		if self.buckets_definition is None:
			return
		
		parent_id_queries = []
		for parent_id in self.hierarchy_pathes:
			query = {
				"term": {
					self.buckets_definition['parent_id_field_for_tree']: parent_id
				}
			}
			
			parent_id_queries.append(query)
		
		if len(parent_id_queries) > 0:
			self.hierarchies_query = {
				self.field: {
					"nested": {
						"path": self.buckets_definition['path']
					}, 
					"aggs": {
						"buckets": {
							"filter": {
								"bool": {
									"should": parent_id_queries,
									"minimum_should_match": 1
								}
							},
							"aggs": {
								"composite_buckets": {
									"composite": {
										"size": 500,
										"sources": [
											{
												"Value": {
													"terms": {
														"field": self.buckets_definition['field_query']
													}
												}
											},
											{
												"ItemID": {
													"terms": {
														"field": self.buckets_definition['id_field_for_tree']
													}
												}
											},
											{
												"ParentID": {
													"terms": {
														"field": self.buckets_definition['parent_id_field_for_tree'],
														"missing_bucket": True
													}
												}
											},
											{
												"TreeLevel": {
													"terms": {
														"field": "{0}.TreeLevel".format(self.buckets_definition['path'])
													}
												}
											}
										]
									}
								}
							}
						}
					}
				}
			}
		
		return


	def getTreeQuery(self):
		return self.hierarchies_query
