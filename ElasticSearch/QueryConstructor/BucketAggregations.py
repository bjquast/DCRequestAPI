import logging
import logging.config
logging.config.fileConfig('logging.conf')
logger = logging.getLogger('elastic_queries')

import pudb

from ElasticSearch.FieldDefinitions import FieldDefinitions
from ElasticSearch.QueryConstructor.QueryConstructor import QueryConstructor


class BucketAggregations(QueryConstructor):
	def __init__(self, users_project_ids = [], source_fields = [], size = 10, buckets_search_term = None, buckets_sort_alphanum = False, buckets_sort_dir = None, prefix_or_match = 'prefix', add_include_filter = False):
		
		self.users_project_ids = users_project_ids
		self.source_fields = source_fields
		self.size = size
		
		self.buckets_search_term = buckets_search_term
		if self.buckets_search_term == '':
			self.buckets_search_term = None
		
		self.buckets_sort_alphanum = buckets_sort_alphanum
		self.buckets_sort_dir = buckets_sort_dir
		self.setBucketsSorting()
		
		self.prefix_or_match = prefix_or_match
		
		self.add_include_filter = add_include_filter
		self.setIncludeFilter()
		
		fielddefs = FieldDefinitions()
		if len(self.source_fields) <= 0:
			self.source_fields = fielddefs.bucketfields
		
		QueryConstructor.__init__(self, fielddefs.fielddefinitions, self.source_fields)
		if self.buckets_search_term is not None:
			self.removeNonTextFromSourceList()
		self.sort_queries_by_definitions()
		self.setSubFilters()


	def getSearchQuery(self, field_defs, field, case_insensitive):
		search_filter = {}
		if self.buckets_search_term is not None:
			if self.prefix_or_match == 'prefix':
				search_filter = {
					"prefix": {
						field_defs[field]['field_query']: {
							"value": self.buckets_search_term,
							"case_insensitive": case_insensitive
						}
					}
				}
			else:
				search_filter = {
					"match_bool_prefix": {
						field: self.buckets_search_term
					}
				}
		return search_filter


	def getAggregationsQuery(self):
		
		self.aggs_query = {}
		
		self.setAggregationsQuery()
		self.setNestedAggregationsQuery()
		self.setRestrictedAggregationsQuery()
		self.setNestedRestrictedAggregationsQuery()
		
		return self.aggs_query


	def setAggregationsQuery(self):
		
		for field in self.simple_fields:
			
			case_insensitive = self.getCaseInsensitiveValue(self.simple_fields[field])
			search_query = self.getSearchQuery(self.simple_fields, field, case_insensitive)
			
			self.aggs_query[field] = {
				"filter": {
					"bool": {
						"must": []
					}
				},
				"aggs": {
					"buckets": {
						"terms": {
							"field": self.simple_fields[field]['field_query'],
							"size": self.size,
							"order": self.bucket_sorting
						}
					}
				}
			}
			
			if len(search_query) > 0:
				self.aggs_query[field]['filter']['bool']['must'].append(search_query)
			
			if self.include_filter_term is not None:
				self.aggs_query[field]['aggs']["buckets"]['terms']['include'] = self.include_filter_term
		
		return


	def setNestedAggregationsQuery(self):
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
								"must": [],
								"filter": []
							}
						},
						"aggs": {
							"buckets": {
								"terms": {
									"field": self.nested_fields[field]['field_query'],
									"size": self.size,
									"order": self.bucket_sorting
								}
							}
						}
					}
				}
			}
			
			if len(search_query) > 0:
				self.aggs_query[field]['aggs']["buckets"]['filter']['bool']['must'].append(search_query)
			
			if field in self.subfilters:
				sub_filter = {
					'terms': self.subfilters[field]
				}
				self.aggs_query[field]['aggs']["buckets"]['filter']['bool']['filter'].append(sub_filter)
			
			if self.include_filter_term is not None:
				self.aggs_query[field]['aggs']["buckets"]['aggs']["buckets"]['terms']['include'] = self.include_filter_term
			
		return


	def setNestedRestrictedAggregationsQuery(self):
		
		for field in self.nested_restricted_fields:
			
			case_insensitive = self.getCaseInsensitiveValue(self.nested_restricted_fields[field])
			search_query = self.getSearchQuery(self.nested_restricted_fields, field, case_insensitive)
			withholdterms = [{"term": {withholdfield: "false"}} for withholdfield in self.nested_restricted_fields[field]['withholdflags']]
			
			self.aggs_query[field] = {
				'nested': {
					'path': self.nested_restricted_fields[field]['path']
				},
				"aggs": {
					"buckets": {
						"filter": {
							"bool": {
								"must": [],
								'should': [
									# need to use the DB_ProjectID within the path for nested objects otherwise the filter fails
									{"terms": {"{0}.DB_ProjectID".format(self.nested_restricted_fields[field]['path']): self.users_project_ids}},
									{
										"bool": {
											"must": withholdterms
										}
									}
								],
								"minimum_should_match": 1,
								"filter": []
							}
						},
						"aggs": {
							"buckets": {
								"terms": {
									"field": self.nested_restricted_fields[field]['field_query'],
									"size": self.size,
									"order": self.bucket_sorting
								}
							}
						}
					}
				}
			}
			
			if len(search_query) > 0:
				self.aggs_query[field]['aggs']["buckets"]['filter']['bool']['must'].append(search_query)
			
			if field in self.subfilters:
				sub_filter = {
					'terms': self.subfilters[field]
				}
				self.aggs_query[field]['aggs']["buckets"]['filter']['bool']['filter'].append(sub_filter)
			
			if self.include_filter_term is not None:
				self.aggs_query[field]['aggs']["buckets"]['aggs']["buckets"]['terms']['include'] = self.include_filter_term
			
		return


	def setRestrictedAggregationsQuery(self):
		
		for field in self.simple_restricted_fields:
			
			case_insensitive = self.getCaseInsensitiveValue(self.simple_restricted_fields[field])
			search_query = self.getSearchQuery(self.simple_restricted_fields, field, case_insensitive)
			withholdterms = [{"term": {withholdfield: "false"}} for withholdfield in self.simple_restricted_fields[field]['withholdflags']]
			
			self.aggs_query[field] = {
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
							"size": self.size,
							"order": self.bucket_sorting
						}
					}
				}
			}
			
			if len(search_query) > 0:
				self.aggs_query[field]['filter']['bool']['must'].append(search_query)
			
			if self.include_filter_term is not None:
				self.aggs_query[field]['aggs']["buckets"]['terms']['include'] = self.include_filter_term
			
		return


	def setIncludeFilter(self):
		self.include_filter_term = None
		# a hack because there is no case insensitive flag for the include filter
		if self.add_include_filter is True and self.buckets_search_term:
			pattern = ''
			for letter in self.buckets_search_term:
				if letter.isalpha():
					pattern = pattern + '[{0}{1}]'.format(letter.lower(), letter.upper())
				else:
					pattern = pattern + letter
			self.include_filter_term = '{0}.*'.format(pattern)
		return


	def getBucketSize(self):
		return self.size
