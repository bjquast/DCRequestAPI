import logging
import logging.config
logging.config.fileConfig('logging.conf')
logger = logging.getLogger('elastic_queries')

import json
import math

import pudb

from ElasticSearch.FieldDefinitions import fieldnames, fielddefinitions

class BucketAggregations():
	def __init__(self, users_project_ids = [], source_fields = [], size = 10, sort_alphanum = False, sort_dir = 'asc'):
		self.users_project_ids = users_project_ids
		self.source_fields = source_fields
		self.size = size
		self.sort_alphanum = sort_alphanum
		self.sort_dir = sort_dir.lower()
		
		self.sortstring = None
		
		self.aggs_fields = {}
		self.nested_aggs_fields = {}
		self.nested_restricted_aggs_fields = {}
		self.restricted_aggs_fields = {}
		
		self.read_field_definitions()


	def read_field_definitions(self):
		if len(self.source_fields) > 0:
			pass
		else:
			self.source_fields = fieldnames
				
		for fieldname in self.source_fields:
			if fieldname in fielddefinitions:
				if 'buckets' in fielddefinitions[fieldname] and 'path' in fielddefinitions[fieldname]['buckets'] and 'withholdflag' in fielddefinitions[fieldname]['buckets']:
					self.nested_restricted_aggs_fields[fieldname] = fielddefinitions[fieldname]['buckets']
				elif 'buckets' in fielddefinitions[fieldname] and 'path' in fielddefinitions[fieldname]['buckets'] and 'withholdflag' not in fielddefinitions[fieldname]['buckets']:
					self.nested_aggs_fields[fieldname] = fielddefinitions[fieldname]['buckets']
				elif 'buckets' in fielddefinitions[fieldname] and 'withholdflag' in fielddefinitions[fieldname]['buckets']:
					self.restricted_aggs_fields[fieldname] = fielddefinitions[fieldname]['buckets']
				elif 'buckets' in fielddefinitions[fieldname]:
					self.aggs_fields[fieldname] = fielddefinitions[fieldname]['buckets']
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
		
		for field in self.aggs_fields:
			self.aggs_query[field] = {'terms': {'field': self.aggs_fields[field]['field_query'], 'size': self.size}}
			sorting_dict = self.getSorting()
			if len(sorting_dict) > 0:
				self.aggs_query[field]['terms']['order'] = sorting_dict
		
		return


	def setNestedAggregationsQuery(self):
		for field in self.nested_aggs_fields:
			self.aggs_query[field] = {
				'nested': {
					'path': self.nested_aggs_fields[field]['path']
				},
				'aggs': {
					'buckets': {
						'terms': {'field': self.nested_aggs_fields[field]['field_query'], 'size': self.size}
					}
				}
			}
			sorting_dict = self.getSorting()
			if len(sorting_dict) > 0:
				self.aggs_query[field]['aggs']['buckets']['terms']['order'] = sorting_dict
		return


	def setNestedRestrictedAggregationsQuery(self):
		
		for field in self.nested_restricted_aggs_fields:
			self.aggs_query[field] = {
				'nested': {
					'path': self.nested_restricted_aggs_fields[field]['path']
				},
				'aggs': {
					'buckets': {
						'filter': {
							'bool': {
								'should': [
									# need to use the DB_ProjectID within the path for nested objects otherwise the filter fails
									{"terms": {"{0}.DB_ProjectID".format(self.nested_restricted_aggs_fields[field]['path']): self.users_project_ids}},
									{"term": {self.nested_restricted_aggs_fields[field]['withholdflag']: "false"}}
								],
								"minimum_should_match": 1
							}
						},
						'aggs': {
							'buckets': {
								'terms': {'field': self.nested_restricted_aggs_fields[field]['field_query'], 'size': self.size}
							}
						}
					}
				}
			}
			
			sorting_dict = self.getSorting()
			if len(sorting_dict) > 0:
				self.aggs_query[field]['aggs']['buckets']['aggs']['buckets']['terms']['order'] = sorting_dict
		return


	def setRestrictedAggregationsQuery(self):
		
		for field in self.restricted_aggs_fields:
			self.aggs_query[field] = {
				'filter': {
					'bool': {
						'should': [
							{"terms": {"Projects.DB_ProjectID": self.users_project_ids}},
							{"term": {self.restricted_aggs_fields[field]['withholdflag']: "false"}}
						],
						"minimum_should_match": 1
					}
				},
				'aggs': {
					'buckets': {
						'terms': {'field': self.restricted_aggs_fields[field]['field_query'], 'size': self.size}
					}
				}
			}
			sorting_dict = self.getSorting()
			if len(sorting_dict) > 0:
				self.aggs_query[field]['aggs']['buckets']['terms']['order'] = sorting_dict
		return

