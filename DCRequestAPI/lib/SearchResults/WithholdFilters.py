import pudb


class WithholdFilters():
	def __init__(self):
		
		self.filter_definitions = {
			'EventWithhold': ['CollectionEventID', 'CollectorsEventNumber', 'LocalityDescription',
				'LocalityVerbatim', 'HabitatDescription', 'CollectingMethod', 'CountryCache',
				'CollectionDate', 'WGS84_Coordinate', 'WGS84_Accuracy m', 'Altitude mNN', 'Altitude_Accuracy m',
				'NamedArea', 'NamedAreaURL', 'NamedAreaNotes', 'EventWithholdingReason', 'EventWithholdingReasonDate'
			],
			'EventWithholdDate': ['CollectionDate',],
			# nested object, can it be implemented with path field only or do i need to name the attributes of the object implicitely?
			'CollectionAgents.CollectorsWithhold': [],
			'Images.ImageWithhold': [],
			'IUWithhold': ['OnlyObserved', 'LifeStage', 'Gender', 'NumberOfUnits', 'NumberOfUnitsModifier', 
				'UnitIdentifier', 'UnitDescription', 'IdentificationUnitNotes', 'IdentificationUnitCircumstances',
			]
		}


	def getWithholdFields(self):
		withhold_fields = [key for key in self.filter_definitions]
		return withhold_fields


	def applyFiltersToSources(self, iupartslist, users_projects):
		#pudb.set_trace()
		
		self.filtered_sources = []
		
		
		for source in iupartslist:
			project_ids = [project['ProjectID'] for project in source['Projects']]
			
			project_matched = False
			
			for users_project in users_projects:
				if users_project in project_ids:
					project_matched = True
					break
			
			if project_matched is False:
			
				for filter_name in self.filter_definitions:
					
					filter_keys = filter_name.split('.')
					self.filterComplexElements(source, filter_keys, filter_name)
			
			self.filtered_sources.append(source)
			
		return self.filtered_sources
		


	def filterComplexElements(self, doc_source, keys_list, filter_name):
		# keys_list[-1] must always be the name of the withhold field that decides whether to delete the data or not 
		#pudb.set_trace()
		while len(keys_list) > 0:
			key = keys_list.pop(0)
			if len(keys_list) > 0:
				if key in doc_source:
					if isinstance (doc_source[key], list) or isinstance (doc_source[key], tuple):
						allowed_items = []
						for i in range (len(doc_source[key])):
							doc_element = self.filterComplexElements(doc_source[key][i], keys_list, filter_name)
							if doc_element is not None:
								allowed_items.append(doc_element)
						doc_source[key] = allowed_items
					else:
						doc_source = self.filterComplexElements(doc_source[key], keys_list, filter_name)
			
			elif len(keys_list) == 0:
				if key in doc_source and doc_source[key] == 'true':
					if len(self.filter_definitions[filter_name]) > 0:
						for field_name in self.filter_definitions[filter_name]:
							try:
								del doc_source[field_name]
							except:
								pass
						return doc_source
					else:
						return None
		return doc_source

