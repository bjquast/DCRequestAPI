import logging
import logging.config
logging.config.fileConfig('logging.conf')
logger = logging.getLogger('elastic_queries')

import pudb

from ElasticSearch.FieldDefinitions import FieldDefinitions

class HierarchyQueries():
	def __init__(self, hierarchy_pathes = {}, users_project_ids = [], source_fields = [], size = 1000):
		self.hierarchy_pathes = hierarchy_pathes
		self.users_project_ids = users_project_ids
		
		self.source_fields = source_fields
		self.size = size
		
		fielddefs = FieldDefinitions()
		self.fielddefinitions = fielddefs.fielddefinitions
		
		if len(self.source_fields) <= 0:
			self.source_fields = fielddefs.hierarchy_query_fields
		
		QueryConstructor.__init__(self, fielddefs.fielddefinitions, self.source_fields)
		
		self.hierarchies_query = {}
		
		self.sort_queries_by_definitions()
		self.setHierarchiesQuery()
		


	def sort_queries_by_definitions(self):
		# reset the fields, needed when sort_queries_by_definitions is used more than once as with StackedInnerQuery
		self.nested_restricted_fields = {}
		self.nested_fields = {}
		self.simple_restricted_fields = {}
		self.simple_fields = {}
		
		
		for fieldname in self.source_fields:
			if fieldname in self.fielddefinitions:
				if 'buckets' in self.fielddefinitions[fieldname] \
					and 'path' in self.fielddefinitions[fieldname]['buckets'] \
					and 'path_hierarchy_field' in self.fielddefinitions[fieldname]['buckets'] \
					and 'withholdflags' in self.fielddefinitions[fieldname]['buckets']:
					self.nested_restricted_fields[fieldname] = self.fielddefinitions[fieldname]['buckets']
				elif 'buckets' in self.fielddefinitions[fieldname] \
					and 'path' in self.fielddefinitions[fieldname]['buckets'] \
					and 'path_hierarchy_field' in self.fielddefinitions[fieldname]['buckets'] \
					and 'withholdflags' not in self.fielddefinitions[fieldname]['buckets']:
					self.nested_fields[fieldname] = self.fielddefinitions[fieldname]['buckets']
				elif 'buckets' in self.fielddefinitions[fieldname] \
					and 'path_hierarchy_field' in self.fielddefinitions[fieldname]['buckets'] \
					and 'withholdflags' in self.fielddefinitions[fieldname]['buckets']:
					self.simple_restricted_fields[fieldname] = self.fielddefinitions[fieldname]['buckets']
				elif 'buckets' in self.fielddefinitions[fieldname]:
					self.simple_fields[fieldname] = self.fielddefinitions[fieldname]['buckets']
		return



	def setHierarchiesQuery(self):
		self.hierarchies_query = {}
		self.setSimpleHierarchiesQuery()
		self.setRestrictedHierarchiesQuery()
		self.setNestedHierarchiesQuery()
		self.setRestrictedNestedHierarchiesQuery()
		return


	def setRestrictedHierarchiesQuery(self):
		
		
		return


	def setSimpleHierarchiesQuery(self):
		for field in self.simple_fields:
		
			path_regex = ''
			for hierarchy_path in self.hierarchy_pathes[field]:
				path_regex += '({0})?'.hierarchy_path
			path_regex += '>?[^>]*'
			
			self.hierarchies_query[field] = {
				"aggs": {
					"buckets": {
						"terms": {
							"field": self.simple_fields[field]['path_hierarchy_field'],
							'size': self.size,
							'include': path_regex
						}
					}
				}
			}
		return


	def setRestrictedHierarchiesQuery(self):
		for field in self.simple_restricted_fields:
		
			path_regex = ''
			for hierarchy_path in self.hierarchy_pathes[field]:
				path_regex += '({0})?'.hierarchy_path
			path_regex += '>?[^>]*'
			
			self.hierarchies_query[field] = {
				"filter": {
					"bool": {
						"must": [],
						'should': [
							{"terms": {"Projects.DB_ProjectID": self.users_project_ids}},
							{
								"bool": {
									"must": withholdterms
								}
							}
						],
						"minimum_should_match": 1
					}
				},
				"aggs": {
					"buckets": {
						"terms": {
							"field": self.simple_restricted_fields[field]['path_hierarchy_field'],
							'size': self.size,
							'include': path_regex
						}
					}
				}
			}
		
		return


	def setNestedHierarchiesQuery(self):
		for field in self.nested_fields:
		
			path_regex = ''
			for hierarchy_path in self.hierarchy_pathes[field]:
				path_regex += '({0})?'.hierarchy_path
			path_regex += '>?[^>]*'
			
			self.hierarchies_query[field] = {
				"nested": {
					"path": self.nested_fields[field]['path']
				},
				"aggs": {
					"buckets": {
						"terms": {
							"field": self.nested_fields[field]['path_hierarchy_field'],
							'size': self.size,
							'include': path_regex
						}
					}
				}
			}
		
		return


	def setNestedRestrictedHierarchiesQuery(self):
		for field in self.nested_restricted_fields:
		
			path_regex = ''
			for hierarchy_path in self.hierarchy_pathes[field]:
				path_regex += '({0})?'.hierarchy_path
			path_regex += '>?[^>]*'
			
			self.hierarchies_query[field] = {
				"nested": {
					"path": self.nested_restricted_fields[field]['path']
				},
				"aggs": {
					"buckets": {
						"filter": {
							"bool": {
								"must": [],
								'should': [
									{"terms": {"Projects.DB_ProjectID": self.users_project_ids}},
									{
										"bool": {
											"must": withholdterms
										}
									}
								],
								"minimum_should_match": 1
							}
						},
						"aggs": {
							"buckets": {
								"terms": {
									"field": self.nested_restricted_fields[field]['path_hierarchy_field'],
									'size': self.size,
									'include': path_regex
								}
							}
						}
					}
				}
			}
		
		return

		
		'''
			self.hierarchies_query[field] = {
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
		'''
		
		return


	def getTreeQuery(self):
		return self.hierarchies_query
