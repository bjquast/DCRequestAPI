import logging
import logging.config
logging.config.fileConfig('logging.conf')
logger = logging.getLogger('elastic_queries')

import pudb

from ElasticSearch.QueryConstructor.QueryConstructor import QueryConstructor


class DateHistogramAggregations(QueryConstructor):
	def __init__(self, users_project_ids = [], source_fields = [], size = 10, interval = 'year', buckets_sort_alphanum = False, buckets_sort_dir = None):
		QueryConstructor.__init__(self)
		
		self.source_fields = source_fields
		if len(self.source_fields) <= 0:
			self.source_fields = self.fieldconf.date_fields
		
		self.users_project_ids = users_project_ids
		self.source_fields = source_fields
		self.size = size
		
		self.buckets_sort_alphanum = buckets_sort_alphanum
		self.buckets_sort_dir = buckets_sort_dir
		self.setBucketsSorting()
		
		self.__setCalendarInterval(interval)
		
		self.es_date_format = 'yyyy-MM-dd'
		
		self.sort_queries_by_definitions()


	def __setCalendarInterval(self, interval):
		if interval.lower() == 'month':
			self.calendar_interval = '1M'
		else:
			self.calendar_interval = '1y'
		return


	def __setExtendedBounds(self, min_bound = None, max_bound = None):
		# is that useful? extended bounds are needed when the 0 values at the start and end of an histogram should be 
		# added to the aggs. because the aggs here are limited to buckets with min_doc_count = 1 the extended bounds do not make sense?!
		self.extended_bounds = {}
		if min_bound is not None:
			self.extended_bounds['min'] = min_bound
		if max_bound is not None:
			self.extended_bounds['max'] = max_bound
		return


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
					"buckets": {
						"date_histogram": {
							"field": field,
							"format": self.es_date_format,
							"calendar_interval":  self.calendar_interval,
							"min_doc_count": 1,
							#"extended_bounds": self.extended_bounds
						},
						"aggs": {
							"limit": {
								"bucket_sort": {
									"sort": [
										self.bucket_sorting
									],
									"size": self.size
								}
							}
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
							"buckets": {
								"date_histogram": {
									"field": field,
									"format": self.es_date_format,
									"calendar_interval":  self.calendar_interval,
									"min_doc_count": 1,
									#"extended_bounds": self.extended_bounds
								},
								"aggs": {
									"limit": {
										"bucket_sort": {
											"sort": [
												self.bucket_sorting
											],
											"size": self.size
										}
									}
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
							"buckets": {
								"date_histogram": {
									"field": field,
									"format": self.es_date_format,
									"calendar_interval":  self.calendar_interval,
									"min_doc_count": 1,
									#"extended_bounds": self.extended_bounds
								},
								"aggs": {
									"limit": {
										"bucket_sort": {
											"sort": [
												self.bucket_sorting
											],
											"size": self.size
										}
									}
								}
							}
						}
					}
				}
			}
		return


	def setRestrictedAggregationsQuery(self):
		
		for field in self.simple_restricted_fields:
			
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
						"date_histogram": {
							"field": field,
							"format": self.es_date_format,
							"calendar_interval":  self.calendar_interval,
							"min_doc_count": 1,
							#"extended_bounds": self.extended_bounds
						},
						"aggs": {
							"limit": {
								"bucket_sort": {
									"sort": [
										self.bucket_sorting
									],
									"size": self.size
								}
							}
						}
					}
				}
			}
		return

	def getBucketSize(self):
		return self.size
