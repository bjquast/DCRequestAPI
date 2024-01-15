import logging
import logging.config
logging.config.fileConfig('logging.conf')
logger = logging.getLogger('elastic_queries')

import json
import math

import pudb

from ElasticSearch.FieldDefinitions import fieldnames, fielddefinitions

class BucketAggregations():
	def __init__(self, users_project_ids = []):
		self.users_project_ids = users_project_ids
		
		self.aggs_fields = {}
		self.nested_aggs_fields = {}
		self.nested_restricted_aggs_fields = {}
		self.restricted_aggs_fields = {}
		
		self.read_field_definitions()


	def read_field_definitions(self):
		for fieldname in fieldnames:
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


	def setAggregationsQuery(self):
		
		for field in self.aggs_fields:
			self.aggs_query[field] = {'terms': {'field': self.aggs_fields[field]['field_query'], 'size': self.aggs_fields[field]['size']}}
		
		return


	def setNestedAggregationsQuery(self):
		for field in self.nested_aggs_fields:
			self.aggs_query[field] = {
				'nested': {
					'path': self.nested_aggs_fields[field]['path']
				},
				'aggs': {
					'buckets': {
						'terms': {'field': self.nested_aggs_fields[field]['field_query'], 'size': self.nested_aggs_fields[field]['size']}
					}
				}
			}
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
									{"terms": {"Projects.ProjectID": self.users_project_ids}},
									{"term": {self.nested_restricted_aggs_fields[field]['withholdflag']: "false"}}
								],
								"minimum_should_match": 1
							}
						},
						'aggs': {
							'buckets': {
								'terms': {'field': self.nested_restricted_aggs_fields[field]['field_query'], 'size': self.nested_restricted_aggs_fields[field]['size']}
							}
						}
					}
				}
			}
		
		return


	def setRestrictedAggregationsQuery(self):
		
		for field in self.restricted_aggs_fields:
			self.aggs_query[field] = {
				'filter': {
					'bool': {
						'should': [
							{"terms": {"Projects.ProjectID": self.users_project_ids}},
							{"term": {self.restricted_aggs_fields[field]['withholdflag']: "false"}}
						],
						"minimum_should_match": 1
					}
				},
				'aggs': {
					'buckets': {
						'terms': {'field': self.restricted_aggs_fields[field]['field_query'], 'size': self.restricted_aggs_fields[field]['size']}
					}
				}
			}
		return

