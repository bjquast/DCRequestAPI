import logging
import logging.config
logging.config.fileConfig('logging.conf')
logger = logging.getLogger('elastic_queries')

import pudb

from ElasticSearch.FieldDefinitions import FieldDefinitions

class TreeQueries():
	def __init__(self, field, parent_ids = [], users_project_ids = []):
		self.field = field
		self.parent_ids = parent_ids
		self.users_project_ids = users_project_ids
		fielddefs = FieldDefinitions()
		self.fielddefinitions = fielddefs.fielddefinitions
		self.tree_fields = fielddefs.tree_query_fields
		
		self.treequery = {}
		
		self.read_buckets_definition()
		if len(self.parent_ids) <= 0:
			self.setNestedRootQuery()
		else:
			self.setNestedChildsQuery()
		


	def read_buckets_definition(self):
		self.buckets_definition = None
		
		# currently only nested fields without restrictions are implemented
		if self.field in self.tree_fields and self.field in self.fielddefinitions:
			if 'buckets' in self.fielddefinitions[self.field] and 'path' in self.fielddefinitions[self.field]['buckets'] and 'withholdflag' not in self.fielddefinitions[self.field]['buckets']:
				self.buckets_definition = self.fielddefinitions[self.field]['buckets']
		return


	def setNestedRootQuery(self):
		self.treequery = {}
		if self.buckets_definition is None:
			return
		self.treequery = {
			self.field: {
				"nested": {
					"path": self.buckets_definition['path']
				}, 
				"aggs": {
					"buckets": {
						"filter": {
							"bool": {
								"must": [
									{
										"term": {
											"{0}.TreeLevel".format(self.buckets_definition['path']): self.buckets_definition['root_level']
										}
									}
								]
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



	def setNestedChildsQuery(self):
		self.treequery = {}
		if self.buckets_definition is None:
			return
		
		parent_id_queries = []
		for parent_id in self.parent_ids:
			query = {
				"term": {
					self.buckets_definition['parent_id_field_for_tree']: parent_id
				}
			}
			
			parent_id_queries.append(query)
		
		if len(parent_id_queries) > 0:
			self.treequery = {
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
		return self.treequery
