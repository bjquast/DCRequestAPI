import logging
import logging.config
logging.config.fileConfig('logging.conf')
logger = logging.getLogger('elastic_queries')

import pudb
import re

from ElasticSearch.FieldDefinitions import FieldDefinitions
from ElasticSearch.QueryConstructor.QueryConstructor import QueryConstructor

class HierarchyQueries(QueryConstructor):
	def __init__(self, hierarchy_pathes_dict = {}, users_project_ids = None, source_fields = None, size = 1000):
		self.hierarchy_pathes_dict = hierarchy_pathes_dict
		
		if users_project_ids is None:
			users_project_ids = []
		self.users_project_ids = users_project_ids
		
		if source_fields is None:
			source_fields = []
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
		
		escape_pattern = re.compile(r'([\(\)\[\]])')
		
		for hierarchy_path in self.hierarchy_pathes_dict[field]:
			if len(hierarchy_path) > 0:
				if hierarchy_path not in sub_pathes:
					hierarchy_path = escape_pattern.sub(r'\\\1', hierarchy_path)
					sub_pathes.append('({0})?'.format(hierarchy_path))
			
			path_elements = hierarchy_path.split('>')
			
			while len(path_elements) > 1:
				path_elements.pop()
				sub_path = '({0})?'.format('>'.join(path_elements))
				if len(sub_path) > 2:
					if sub_path not in sub_pathes:
						sub_pathes.append(sub_path)
		
		path_regex = ''.join(sub_pathes) + '>?[^>]*'
		
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
			
			withholdterms = [{"term": {withholdfield: "false"}} for withholdfield in self.simple_restricted_fields[field]['withholdflags']]
			
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
			
			withholdterms = [{"term": {withholdfield: "false"}} for withholdfield in self.nested_restricted_fields[field]['withholdflags']]
			
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
