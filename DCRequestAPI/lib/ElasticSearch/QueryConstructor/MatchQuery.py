import logging
import logging.config
logging.config.fileConfig('logging.conf')
logger = logging.getLogger('elastic')

import json
import math

import pudb

class MatchQuery():
	def __init__(self, users_projects = []):
		self.users_projects = users_projects
		
		self.open_fields = [
			'PartAccessionNumber',
			'SpecimenAccessionNumber',
			'CollectingMethod',
			'PreparationMethod',
			'MaterialCategory',
			'LifeStage',
			'Gender',
			'LastIdentificationCache',
			'FamilyCache',
			'OrderCache',
			'Projects.Project',
			'CollectionName',
			'Barcodes.Methods.region'
		]
		
		self.withholded_fields = {
			'Event': {
				'fields': [
					'NamedArea',
					'CollectorsEventNumber',
					'LocalityDescription',
					'LocalityVerbatim',
					'HabitatDescription',
					'CountryCache',
					'CollectingMethod',
				],
				'withholdflag': 'EventWithhold'
			},
			'CollectionAgents': {
				'nested': {
					'path': 'CollectionAgents'
				},
				'fields': [
					'CollectionAgents.CollectorsName',
				],
				'withholdflag': 'CollectionAgents.CollectorsWithhold'
			},
		}
		
		
		'''
			'EventDate': {
				'fields': ['CollectionDate'],
				'withholdflag': 'EventWithholdDate'
			}
		'''


	def getMatchQuery(self, query_string):
		
		if query_string is not None and len(query_string) > 0:
			
			if len(self.withholded_fields) <= 0:
				self.match_query = {
					'multi_match': {
						'query': query_string, 
						'fields': self.open_fields
					}
				}
				
			
			else:
				self.match_query = {
					'bool': {
						'should': [
								{
								'multi_match': {
									'query': query_string, 
									'fields': self.open_fields
								}
							},
						]
					}
				}
				
				withholded_queries = []
				for w_field in self.withholded_fields:
					query = {
						'bool': {
							'must': [
								{
									'multi_match': {
										'query': query_string, 
										'fields': self.withholded_fields[w_field]['fields']
									}
								}
							],
							'filter': [
								{
									'bool': {
										'should': [
											{"terms": {"Projects.ProjectID": self.users_projects}},
											{"term": {self.withholded_fields[w_field]['withholdflag']: "false"}}
										],
										"minimum_should_match": 1
									}
								}
							]
						}
					}
					
					if 'nested' in self.withholded_fields[w_field]:
						outer_query = {
							'nested': {
								'path': self.withholded_fields[w_field]['nested']['path'],
								'query': query
							}
						}
						query = outer_query
					
					withholded_queries.append(query)
				
				self.match_query['bool']['should'].extend(withholded_queries)
			
		
		return self.match_query
		
