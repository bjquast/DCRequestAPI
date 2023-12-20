import logging
import logging.config
logging.config.fileConfig('logging.conf')
logger = logging.getLogger('elastic')

import json
import math

import pudb

class BucketAggregations():
	def __init__(self, users_projects = []):
		self.users_projects = users_projects
		self.aggs_fields = {
			'LastIdentificationCache':  {'field_query': 'LastIdentificationCache', 'size': 20},
			'FamilyCache': {'field_query': 'FamilyCache', 'size': 20},
			'OrderCache': {'field_query': 'OrderCache', 'size': 20},
			'CollectionName': {'field_query': 'CollectionName', 'size': 20},
			'Projects.Project': {'field_query': 'Projects.Project', 'size': 20},
			'CountryCache': {'field_query': 'CountryCache.keyword', 'size': 20},
			'CollectingMethod': {'field_query': 'CollectingMethod.keyword', 'size': 20}
		}
		
		self.restricted_aggs_fields = {
			'CollectorsName': {'path': 'CollectionAgents', 'field_query': 'CollectionAgents.CollectorsName.keyword', 'withholdflag': 'CollectionAgents.CollectorsWithhold', 'size': 20}
		}


	def getAggregationsQuery(self):
		self.aggs_query = {}
		self.setAggregationsQuery()
		self.setRestrictedAggregationsQuery()
		
		return self.aggs_query
		
	def setAggregationsQuery(self):
		
		for field in self.aggs_fields:
			self.aggs_query[field] = {'terms': {'field': self.aggs_fields[field]['field_query'], 'size': self.aggs_fields[field]['size']}}
		
		return


	def setRestrictedAggregationsQuery(self):
		
		for field in self.restricted_aggs_fields:
			self.aggs_query[field] = {
				'nested': {
					'path': self.restricted_aggs_fields[field]['path']
				},
				'aggs': {
					'filter_{0}'.format(field): {
						'filter': {
							'bool': {
								'should': [
									{"terms": {"Projects.ProjectID": self.users_projects}},
									{"term": {self.restricted_aggs_fields[field]['withholdflag']: "false"}}
								],
								"minimum_should_match": 1
							}
						},
						'aggs': {
							'open_{0}'.format(field): {
								'terms': {'field': self.restricted_aggs_fields[field]['field_query'], 'size': self.restricted_aggs_fields[field]['size']}
							}
						}
					}
				}
			}
		
		return
		
		
