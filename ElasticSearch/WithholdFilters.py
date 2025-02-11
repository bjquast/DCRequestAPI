import pudb

from configparser import ConfigParser

config = ConfigParser()
config.read('config.ini')

import logging, logging.config
logging.config.fileConfig('logging.conf')
logger = logging.getLogger('webapp')



class WithholdFilters():
	def __init__(self):
		
		self.filter_definitions = {
			'EventWithhold': {
				'path': ['EventWithhold'],
				'fields': ['CollectionEventID', 'CollectorsEventNumber', 'LocalityDescription',
					'LocalityVerbatim', 'HabitatDescription', 'CollectingMethod', 'CountryCache',
					'CollectionDate', 'WGS84_Coordinate', 'WGS84_Accuracy m', 'Altitude mNN', 'Altitude_Accuracy m',
					'NamedArea', 'NamedAreaURL', 'NamedAreaNotes', 'EventWithholdingReason', 'EventWithholdingReasonDate'
				]
			},
			'EventWithholdDate': { 
				'path': ['EventWithholdDate'],
				'fields': ['CollectionDate'],
			},
			'IUWithhold': {
				'path': ['IUWithhold'],
				'fields': ['OnlyObserved', 'LifeStage', 'Gender', 'NumberOfUnits', 'NumberOfUnitsModifier', 
					'UnitIdentifier', 'UnitDescription', 'IdentificationUnitNotes', 'IdentificationUnitCircumstances'
				],
			},
			# nested objects, names must contain the path to the respective field in elastic search index, because they must be added
			# to the source fields in ES_Searcher for the later filtering
			'CollectionAgents.CollectorsWithhold': {
				'path': ['CollectionAgents', 'CollectorsWithhold'],
				'fields': []
			},
			'Images.ImageWithhold': {
				'path': ['Images', 'ImageWithhold'],
				'fields': []
			},
			# Projects embargo settings
			'CollectionAgents.embargo_collector': {
				'path': ['CollectionAgents', 'embargo_collector'],
				'fields': []
			},
			'CollectionAgents.embargo_anonymize_collector': {
				'path': ['CollectionAgents', 'embargo_anonymize_collector'],
				'fields': []
			},
			'embargo_anonymize_depositor': {
				'path': ['embargo_anonymize_depositor'],
				'fields': ['DepositorsName']
			},
			'Identifications.embargo_anonymize_determiner': {
				'path': ['Identifications', 'embargo_anonymize_determiner'],
				'fields': ['ResponsibleName']
			},
			'embargo_event_but_country': {
				'path': ['embargo_event_but_country'],
				'fields': [
					'CollectionEventID', 'CollectorsEventNumber', 'LocalityDescription',
					'LocalityVerbatim', 'HabitatDescription', 'CollectingMethod',
					'CollectionDate', 'WGS84_Coordinate', 'WGS84_Accuracy m', 'Altitude mNN', 'Altitude_Accuracy m',
					'NamedArea', 'NamedAreaURL', 'NamedAreaNotes', 'EventWithholdingReason', 'EventWithholdingReasonDate'
				]
			},
			'embargo_coordinates': {
				'path': ['embargo_coordinates'],
				'fields': ['WGS84_Coordinate', 'WGS84_Accuracy m', 'Altitude mNN', 'Altitude_Accuracy m']
			},
			'embargo_event_but_country_after_1992': {
				'path': ['embargo_event_but_country_after_1992'],
				'fields': [
					'CollectionEventID', 'CollectorsEventNumber', 'LocalityDescription',
					'LocalityVerbatim', 'HabitatDescription', 'CollectingMethod',
					'CollectionDate', 'WGS84_Coordinate', 'WGS84_Accuracy m', 'Altitude mNN', 'Altitude_Accuracy m',
					'NamedArea', 'NamedAreaURL', 'NamedAreaNotes', 'EventWithholdingReason', 'EventWithholdingReasonDate'
				]
			},
			'embargo_coll_date': {
				'path': ['embargo_coll_date'],
				'fields': ['CollectionDate']
			},
		}


	def getWithholdFields(self):
		withhold_fields = [key for key in self.filter_definitions]
		return withhold_fields


	def applyFiltersToSources(self, docs, users_projects):
		#logger.debug('WithholFilters.applyFiltersToSources started')
		
		self.filtered_docs = []
		
		
		for doc in docs:
			source = doc['_source']
			project_ids = [project['DB_ProjectID'] for project in source['Projects']]
			
			project_matched = False
			
			for users_project in users_projects:
				if users_project in project_ids:
					project_matched = True
					break
			
			if project_matched is False:
				for filter_name in self.filter_definitions:
					path_list = list(self.filter_definitions[filter_name]['path'])
					source = self.filterElements(source, path_list, filter_name)
					
					
					'''
					filter_keys = filter_name.split('.')
					if len(filter_keys) == 1 and len(self.filter_definitions[filter_keys[0]]) > 0:
						source = self.filterSimpleElements(source, filter_name)
					
					elif len(filter_keys) > 1:
						source = self.filterComplexElements(source, filter_keys)
					'''
			
			self.filtered_docs.append(doc)
		
		#logger.debug('WithholFilters.applyFiltersToSources finished')
		return self.filtered_docs



	def filterElements(self, doc_element, path_list, filter_name):
		if len(path_list) > 1:
			key = path_list.pop(0)
			if key in doc_element:
				if isinstance (doc_element[key], list) or isinstance (doc_element[key], tuple):
					allowed_items = []
					for element in doc_element[key]:
						element = self.filterElements(element, path_list, filter_name)
						if element is not None:
							allowed_items.append(element)
					doc_element[key] = allowed_items
				else:
					doc_element[key] = self.filterElements(doc_element[key], path_list, filter_name)
		elif len(path_list) == 1:
			key = path_list[0]
			if key in doc_element and doc_element[key] == 'true':
				if 'fields' in self.filter_definitions[filter_name] and len(self.filter_definitions[filter_name]['fields']) > 0:
					for field_name in self.filter_definitions[filter_name]['fields']:
						try:
							del doc_element[field_name]
						except:
							pass
				else:
					return None
			else:
				return doc_element
		
		return doc_element


