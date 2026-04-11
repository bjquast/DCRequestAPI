import logging
import logging.config
logging.config.fileConfig('logging.conf')
logger = logging.getLogger('elastic_queries')

import pudb

from ElasticSearch.FieldDefinitions import FieldDefinitions
from ElasticSearch.QueryConstructor.QueryConstructor import QueryConstructor


class AggsSuggestions(QueryConstructor):
	def __init__(self, users_project_ids = [], source_fields = [], size = 10, buckets_sort_alphanum = True, buckets_sort_dir = 'asc', prefix_or_match = 'prefix'):
		#pudb.set_trace()
		
		self.users_project_ids = users_project_ids
		self.source_fields = source_fields
		self.size = size
		self.buckets_sort_alphanum = buckets_sort_alphanum
		self.buckets_sort_dir = buckets_sort_dir.lower()
		self.prefix_or_match = prefix_or_match
		
		fielddefs = FieldDefinitions()
		if len(self.source_fields) <= 0:
			self.source_fields = fielddefs.term_fields
		
		QueryConstructor.__init__(self, fielddefs.fielddefinitions, self.source_fields)
		
		self.removeNonTextFromSourceList()
		self.sort_queries_by_definitions()
		self.setSubFilters()
		


	def getSearchQuery(self, field_defs, field, case_insensitive):
		if self.prefix_or_match == 'prefix':
			search_filter = {
				"prefix": {
					field_defs[field]['field_query']: {
						"value": self.value,
						"case_insensitive": case_insensitive
					}
				}
			}
		else:
			search_filter = {
				"match_bool_prefix": {
					field: self.value
				}
			}
		return search_filter


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
		if self.buckets_sort_alphanum is True:
			if self.buckets_sort_dir not in ['asc', 'desc']:
				self.buckets_sort_dir = 'asc'
			
			sorting = {"_key": self.buckets_sort_dir}
			
		return sorting


	def setSuggestionsQuery(self):
		
		for field in self.simple_fields:
			
			case_insensitive = self.getCaseInsensitiveValue(self.simple_fields[field])
			search_query = self.getSearchQuery(self.simple_fields, field, case_insensitive)
			
			self.aggs_query[field] = {
				"filter": {
					"bool": {
						"must": [
							search_query
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
			
			case_insensitive = self.getCaseInsensitiveValue(self.nested_fields[field])
			search_query = self.getSearchQuery(self.nested_fields, field, case_insensitive)
			
			self.aggs_query[field] = {
				'nested': {
					'path': self.nested_fields[field]['path']
				},
				"aggs": {
					"buckets": {
						"filter": {
							"bool": {
								"must": [
									search_query
								],
								"filter": []
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
			
			if field in self.subfilters:
				sub_filter = {
					'terms': self.subfilters[field]
				}
				self.aggs_query[field]['aggs']["buckets"]['filter']['bool']['filter'].append(sub_filter)
			
			sorting_dict = self.getSorting()
			if len(sorting_dict) > 0:
				self.aggs_query[field]['aggs']["buckets"]['aggs']['buckets']['terms']['order'] = sorting_dict
		return


	def setNestedRestrictedSuggestionsQuery(self):
		
		for field in self.nested_restricted_fields:
			
			case_insensitive = self.getCaseInsensitiveValue(self.nested_restricted_fields[field])
			search_query = self.getSearchQuery(self.nested_restricted_fields, field, case_insensitive)
			
			self.aggs_query[field] = {
				'nested': {
					'path': self.nested_restricted_fields[field]['path']
				},
				"aggs": {
					"buckets": {
						"filter": {
							"bool": {
								"must": [
									search_query
								],
								'should': [
									# need to use the DB_ProjectID within the path for nested objects otherwise the filter fails
									{"terms": {"{0}.DB_ProjectID".format(self.nested_restricted_fields[field]['path']): self.users_project_ids}},
									{"term": {self.nested_restricted_fields[field]['withholdflag']: "false"}}
								],
								"minimum_should_match": 1,
								"filter": []
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
			
			if field in self.subfilters:
				sub_filter = {
					'terms': self.subfilters[field]
				}
				self.aggs_query[field]['aggs']["buckets"]['filter']['bool']['filter'].append(sub_filter)
			
			sorting_dict = self.getSorting()
			if len(sorting_dict) > 0:
				self.aggs_query[field]['aggs']['buckets']['aggs']['buckets']['terms']['order'] = sorting_dict
		return


	def setRestrictedSuggestionsQuery(self):
		
		for field in self.simple_restricted_fields:
			
			case_insensitive = self.getCaseInsensitiveValue(self.simple_restricted_fields[field])
			search_query = self.getSearchQuery(self.simple_restricted_fields, field, case_insensitive)
			
			self.aggs_query[field] = {
				"filter": {
					"bool": {
						"must": [
							search_query
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
