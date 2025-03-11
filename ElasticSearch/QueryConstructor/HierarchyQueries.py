import logging
import logging.config
logging.config.fileConfig('logging.conf')
logger = logging.getLogger('elastic_queries')

import pudb
import re

from ElasticSearch.FieldDefinitions import FieldDefinitions
from ElasticSearch.QueryConstructor.QueryConstructor import QueryConstructor

class HierarchyQueries():
	def __init__(self, hierarchy_pathes_dict = {}, users_project_ids = [], source_fields = [], size = 1000):
		self.hierarchy_pathes_dict = hierarchy_pathes_dict
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
					and 'field_query' in self.fielddefinitions[fieldname]['buckets'] \
					and 'withholdflags' in self.fielddefinitions[fieldname]['buckets']:
					self.nested_restricted_fields[fieldname] = self.fielddefinitions[fieldname]['buckets']
				elif 'buckets' in self.fielddefinitions[fieldname] \
					and 'path' in self.fielddefinitions[fieldname]['buckets'] \
					and 'field_query' in self.fielddefinitions[fieldname]['buckets'] \
					and 'withholdflags' not in self.fielddefinitions[fieldname]['buckets']:
					self.nested_fields[fieldname] = self.fielddefinitions[fieldname]['buckets']
				elif 'buckets' in self.fielddefinitions[fieldname] \
					and 'field_query' in self.fielddefinitions[fieldname]['buckets'] \
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
		self.setNestedRestrictedHierarchiesQuery()
		return


	def getPathRegexp(self, field):
		path_regex = ''
		sub_pathes = []
		
		
		for hierarchy_path in self.hierarchy_pathes_dict[field]:
			sub_pathes.append('({0})?>?[^>]*'.format(hierarchy_path))
			
			path_elements = hierarchy_path.split('>')
			
			while len(path_elements) > 2:
				path_elements.pop()
				sub_pathes.append('>'.join(path_elements))
		
		for hierarchy_path in sub_pathes:
			path_regex += '({0})?'.format(hierarchy_path)
		
		return path_regex


	def setSimpleHierarchiesQuery(self):
		for field in self.simple_fields:
			if field in self.hierarchy_pathes_dict:
				path_regex = self.getPathRegexp(field)
			else:
				path_regex = '>?[^>]*'
				
			self.hierarchies_query[field] = {
				"terms": {
					"field": self.simple_fields[field]['field_query'],
					'size': self.size,
					'include': path_regex
				}
			}
		return


	def setRestrictedHierarchiesQuery(self):
		for field in self.simple_restricted_fields:
			if field in self.hierarchy_pathes_dict:
				path_regex = self.getPathRegexp(field)
			else:
				path_regex = '>?[^>]*'
			
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
							"field": self.simple_restricted_fields[field]['field_query'],
							'size': self.size,
							'include': path_regex
						}
					}
				}
			}
		
		return


	def setNestedHierarchiesQuery(self):
		for field in self.nested_fields:
			if field in self.hierarchy_pathes_dict:
				path_regex = self.getPathRegexp(field)
			else:
				path_regex = '>?[^>]*'
			
			self.hierarchies_query[field] = {
				"nested": {
					"path": self.nested_fields[field]['path']
				},
				"aggs": {
					"buckets": {
						"terms": {
							"field": self.nested_fields[field]['field_query'],
							'size': self.size,
							'include': path_regex
						}
					}
				}
			}
		
		return


	def setNestedRestrictedHierarchiesQuery(self):
		for field in self.nested_restricted_fields:
			if field in self.hierarchy_pathes_dict:
				path_regex = self.getPathRegexp(field)
			else:
				path_regex = '>?[^>]*'
			
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
									"field": self.nested_restricted_fields[field]['field_query'],
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


	def getHierarchiesQuery(self):
		return self.hierarchies_query
