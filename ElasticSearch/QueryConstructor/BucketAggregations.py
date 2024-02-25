import logging
import logging.config
logging.config.fileConfig('logging.conf')
logger = logging.getLogger('elastic_queries')

import pudb

from ElasticSearch.QueryConstructor.QuerySorter import QuerySorter

class BucketAggregations(QuerySorter):
	def __init__(self, users_project_ids = [], source_fields = [], size = 10, sort_alphanum = False, sort_dir = 'asc'):
		self.users_project_ids = users_project_ids
		self.source_fields = source_fields
		self.size = size
		self.sort_alphanum = sort_alphanum
		self.sort_dir = sort_dir.lower()
		
		self.sortstring = None
		
		QuerySorter.__init__(self, source_fields)
		self.sort_queries_by_definitions()
		self.setSubFiltersInNestedAggregations()


	def setSubFiltersInNestedAggregations(self):
		# when the nested objects should be filtered by a value, e. g. the parent taxa by rank
		#pudb.set_trace()
		self.subfilters = {}
		for field in self.nested_fields:
			if 'sub_filters' in self.nested_fields[field]:
				for sub_filter_element in self.nested_fields[field]['sub_filters']:
					if field not in self.subfilters:
						self.subfilters[field] = {}
					
					if sub_filter_element[0] not in self.subfilters[field]:
						self.subfilters[field][sub_filter_element[0]] = []
					
					self.subfilters[field][sub_filter_element[0]].append(sub_filter_element[1])
		
		return
		


	def getAggregationsQuery(self):
		self.aggs_query = {}
		
		self.setAggregationsQuery()
		self.setNestedAggregationsQuery()
		self.setRestrictedAggregationsQuery()
		self.setNestedRestrictedAggregationsQuery()
		
		return self.aggs_query


	def getSorting(self):
		sorting = {}
		if self.sort_alphanum is True:
			if self.sort_dir not in ['asc', 'desc']:
				self.sort_dir = 'asc'
			
			sorting = {"_key": self.sort_dir}
			
		return sorting


	def setAggregationsQuery(self):
		
		for field in self.simple_fields:
			self.aggs_query[field] = {'terms': {'field': self.simple_fields[field]['field_query'], 'size': self.size}}
			sorting_dict = self.getSorting()
			if len(sorting_dict) > 0:
				self.aggs_query[field]['terms']['order'] = sorting_dict
		
		return


	def setNestedAggregationsQuery(self):
		for field in self.nested_fields:
			self.aggs_query[field] = {
				'nested': {
					'path': self.nested_fields[field]['path']
				},
				'aggs': {
					'buckets': {
						'aggs': {
							'buckets': {
								'terms': {'field': self.nested_fields[field]['field_query'], 'size': self.size}
							}
						},
						'filter': {
							'bool': {
								'must': []
							}
						}
					}
				}
			}
			
			
			if field in self.subfilters:
				terms_sub_filter = {
					'terms': self.subfilters[field]
				}
				self.aggs_query[field]['aggs']['buckets']['filter']['bool']['must'].append(terms_sub_filter)
			
			sorting_dict = self.getSorting()
			if len(sorting_dict) > 0:
				self.aggs_query[field]['aggs']['buckets']['aggs']['buckets']['terms']['order'] = sorting_dict
		return


	def setNestedRestrictedAggregationsQuery(self):
		
		for field in self.nested_restricted_fields:
			self.aggs_query[field] = {
				'nested': {
					'path': self.nested_restricted_fields[field]['path']
				},
				'aggs': {
					'buckets': {
						'filter': {
							'bool': {
								'should': [
									# need to use the DB_ProjectID within the path for nested objects otherwise the filter fails
									{"terms": {"{0}.DB_ProjectID".format(self.nested_restricted_fields[field]['path']): self.users_project_ids}},
									{"term": {self.nested_restricted_fields[field]['withholdflag']: "false"}}
								],
								"minimum_should_match": 1
							}
						},
						'aggs': {
							'buckets': {
								'terms': {'field': self.nested_restricted_fields[field]['field_query'], 'size': self.size}
							}
						}
					}
				}
			}
			
			if field in self.subfilters:
				if 'must' not in self.aggs_query[field]['aggs']['buckets']['filter']['bool']:
					self.aggs_query[field]['aggs']['buckets']['filter']['bool']['must'] = []
				terms_sub_filter = {
					'terms': self.subfilters[field]
				}
				self.aggs_query[field]['aggs']['buckets']['filter']['bool']['must'].append(terms_sub_filter)
			
			sorting_dict = self.getSorting()
			if len(sorting_dict) > 0:
				self.aggs_query[field]['aggs']['buckets']['aggs']['buckets']['terms']['order'] = sorting_dict
		return


	def setRestrictedAggregationsQuery(self):
		
		for field in self.simple_restricted_fields:
			self.aggs_query[field] = {
				'filter': {
					'bool': {
						'should': [
							{"terms": {"Projects.DB_ProjectID": self.users_project_ids}},
							{"term": {self.simple_restricted_fields[field]['withholdflag']: "false"}}
						],
						"minimum_should_match": 1
					}
				},
				'aggs': {
					'buckets': {
						'terms': {'field': self.simple_restricted_fields[field]['field_query'], 'size': self.size}
					}
				}
			}
			sorting_dict = self.getSorting()
			if len(sorting_dict) > 0:
				self.aggs_query[field]['aggs']['buckets']['terms']['order'] = sorting_dict
		return

