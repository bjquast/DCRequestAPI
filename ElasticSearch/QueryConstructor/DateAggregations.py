import logging
import logging.config
logging.config.fileConfig('logging.conf')
logger = logging.getLogger('elastic_queries')

import pudb

from ElasticSearch.FieldDefinitions import FieldDefinitions
from ElasticSearch.QueryConstructor.QueryConstructor import QueryConstructor
from ElasticSearch.QueryConstructor.DateRangesGenerator import DateRangesGenerator


class DateAggregations(QueryConstructor):
	def __init__(self, users_project_ids = [], source_fields = [], size = 10, startdate = '1800-01-01', enddate = None, interval = 'year', interval_multiplicator = 1, buckets_sort_alphanum = False, buckets_sort_dir = None):
		pudb.set_trace()
		
		self.users_project_ids = users_project_ids
		self.source_fields = source_fields
		self.size = size
		
		self.buckets_sort_alphanum = buckets_sort_alphanum
		self.buckets_sort_dir = buckets_sort_dir
		self.setBucketsSorting()
		
		fielddefs = FieldDefinitions()
		if len(self.source_fields) <= 0:
			self.source_fields = fielddefs.date_fields
		
		QueryConstructor.__init__(self, fielddefs.fielddefinitions, self.source_fields)
		
		self.date_ranges = DateRangesGenerator(startdate = startdate, enddate = enddate, interval = interval, interval_multiplicator = interval_multiplicator).generate_ranges()
		self.sort_queries_by_definitions()


	def getAggregationsQuery(self):
		
		self.aggs_query = {}
		
		self.setAggregationsQuery()
		self.setNestedAggregationsQuery()
		self.setRestrictedAggregationsQuery()
		self.setNestedRestrictedAggregationsQuery()
		
		return self.aggs_query


	def setAggregationsQuery(self):
		for field in self.simple_fields:
			self.aggs_query[field] = {
				"filter": {
					"bool": {
						"must": []
					}
				},
				"aggs": {
					"range": {
						"date_range": {
							"size": self.size,
							"field": field,
							"format": self.time_format,
							"min_doc_count": 1,
							"order": self.sorting_dict,
							"ranges": self.date_ranges
						}
					}
				}
			}
		
		return


	def setNestedAggregationsQuery(self):
		for field in self.nested_fields:
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
							"range": {
								"date_range": {
									"size": self.size,
									"field": field,
									"format": self.time_format,
									"min_doc_count": 1,
									"order": self.sorting_dict,
									"ranges": self.date_ranges
								}
							}
						}
					}
				}
			}
		return


	def setNestedRestrictedAggregationsQuery(self):
		
		for field in self.nested_restricted_fields:
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
							"range": {
								"date_range": {
									"size": self.size,
									"field": field,
									"format": self.time_format,
									"min_doc_count": 1,
									"order": self.sorting_dict,
									"ranges": self.date_ranges
								}
							}
						}
					}
				}
			}
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
					"range": {
						"date_range": {
							"size": self.size,
							"field": field,
							"format": self.time_format,
							"min_doc_count": 1,
							"order": self.sorting_dict,
							"ranges": self.date_ranges
						}
					}
				}
			}
		return

	def getBucketSize(self):
		return self.size
