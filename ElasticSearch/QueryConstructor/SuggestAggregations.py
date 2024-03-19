import logging
import logging.config
logging.config.fileConfig('logging.conf')
logger = logging.getLogger('elastic_queries')

import pudb

from ElasticSearch.FieldDefinitions import FieldDefinitions
from ElasticSearch.QueryConstructor.QuerySorter import QuerySorter


class SuggestAggregations(QuerySorter):
	def __init__(self, users_project_ids = [], source_fields = [], size = 10, sort_alphanum = True, sort_dir = 'asc'):
		#pudb.set_trace()
		
		self.users_project_ids = users_project_ids
		self.source_fields = source_fields
		self.size = size
		self.sort_alphanum = sort_alphanum
		self.sort_dir = sort_dir.lower()
		self.sortstring = None
		
		fielddefs = FieldDefinitions()
		if len(self.source_fields) <= 0:
			self.source_fields = fielddefs.suggestion_fields
		
		QuerySorter.__init__(self, fielddefs.fielddefinitions, self.source_fields)
		self.sort_queries_by_definitions()


	def getSuggestionsQuery(self, value):
		self.value = value
		self.aggs_query = {}
		
		self.setSuggestionsQuery()
		self.setNestedSuggestionsQuery()
		self.setRestrictedSuggestionsQuery()
		self.setNestedRestrictedSuggestionsQuery()
		
		return self.aggs_query


	def getSorting(self):
		sorting = {}
		if self.sort_alphanum is True:
			if self.sort_dir not in ['asc', 'desc']:
				self.sort_dir = 'asc'
			
			sorting = {"_key": self.sort_dir}
			
		return sorting


	def setSuggestionsQuery(self):
		
		for field in self.simple_fields:
			self.aggs_query[field] = {
				"filter": {
					"bool": {
						"must": [
							{
								"prefix": {
									field: self.value
								}
							}
						]
					}
				},
				"aggs": {
					"buckets": {
						"terms": {
							"field": self.simple_fields[field]['field_query'],
							'size': self.size
						}
					}
				}
			}
			sorting_dict = self.getSorting()
			if len(sorting_dict) > 0:
				self.aggs_query[field]['aggs']['buckets']['terms']['order'] = sorting_dict
		
		return


	def setNestedSuggestionsQuery(self):
		for field in self.nested_fields:
			self.aggs_query[field] = {
				'nested': {
					'path': self.nested_fields[field]['path']
				},
				"aggs": {
					"buckets": {
						"filter": {
							"bool": {
								"must": [
									{
										"prefix": {
											field: self.value
										}
									}
								]
							}
						},
						"aggs": {
							"buckets": {
								"terms": {
									"field": self.nested_fields[field]['field_query'],
									'size': self.size
								}
							}
						}
					}
				}
			}
			
			sorting_dict = self.getSorting()
			if len(sorting_dict) > 0:
				self.aggs_query[field]['aggs']["buckets"]['aggs']['buckets']['terms']['order'] = sorting_dict
		return


	def setNestedRestrictedSuggestionsQuery(self):
		
		for field in self.nested_restricted_fields:
			self.aggs_query[field] = {
				'nested': {
					'path': self.nested_restricted_fields[field]['path']
				},
				"aggs": {
					"buckets": {
						"filter": {
							"bool": {
								"must": [
									{
										"prefix": {
											field: self.value
										}
									}
								],
								'should': [
									# need to use the DB_ProjectID within the path for nested objects otherwise the filter fails
									{"terms": {"{0}.DB_ProjectID".format(self.nested_restricted_fields[field]['path']): self.users_project_ids}},
									{"term": {self.nested_restricted_fields[field]['withholdflag']: "false"}}
								],
								"minimum_should_match": 1
							}
						},
						"aggs": {
							"buckets": {
								"terms": {
									"field": self.nested_restricted_fields[field]['field_query'],
									'size': self.size
								}
							}
						}
					}
				}
			}
			
			sorting_dict = self.getSorting()
			if len(sorting_dict) > 0:
				self.aggs_query[field]['aggs']['buckets']['aggs']['buckets']['terms']['order'] = sorting_dict
		return


	def setRestrictedSuggestionsQuery(self):
		
		for field in self.simple_restricted_fields:
			self.aggs_query[field] = {
				"filter": {
					"bool": {
						"must": [
							{
								"prefix": {
									field: self.value
								}
							}
						],
						'should': [
							{"terms": {"Projects.DB_ProjectID": self.users_project_ids}},
							{"term": {self.simple_restricted_fields[field]['withholdflag']: "false"}}
						],
						"minimum_should_match": 1
					}
				},
				"aggs": {
					"buckets": {
						"terms": {
							"field": self.simple_restricted_fields[field]['field_query'],
							'size': self.size
						}
					}
				}
			}
			
			sorting_dict = self.getSorting()
			if len(sorting_dict) > 0:
				self.aggs_query[field]['aggs']['buckets']['terms']['order'] = sorting_dict
		return


	def getBucketSize(self):
		return self.size
