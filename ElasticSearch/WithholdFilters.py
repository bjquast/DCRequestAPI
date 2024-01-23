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


	def applyFiltersToSources(self, docs, users_projects):
		#pudb.set_trace()
		
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
					
					filter_keys = filter_name.split('.')
					if len(filter_keys) == 1 and len(self.filter_definitions[filter_keys[0]]) > 0:
						source = self.filterSimpleElements(source, filter_keys[0], filter_name)
					
					elif len(filter_keys) > 1:
						source = self.filterComplexElements(source, filter_keys, filter_name)
			
			self.filtered_docs.append(doc)
			
		return self.filtered_docs


	def filterSimpleElements(self, doc_element, key, filter_name):
			if key in doc_element and doc_element[key] == 'true':
				if len(self.filter_definitions[filter_name]) > 0:
					for field_name in self.filter_definitions[filter_name]:
						try:
							del doc_element[field_name]
						except:
							pass
			return doc_element


	def filterComplexElements(self, doc_element, keys_list, filter_name):
		# keys_list[-1] must always be the name of the withhold field that decides whether to delete the data or not 
		for key in keys_list:
			if len(keys_list) > 1:
				if key in doc_element:
					if isinstance (doc_element[key], list) or isinstance (doc_element[key], tuple):
						allowed_items = []
						for element in doc_element[key]:
							element = self.filterComplexElements(element, keys_list[1:], filter_name)
							if element is not None:
								allowed_items.append(element)
						doc_element[key] = allowed_items
					else:
						doc_element[key] = self.filterComplexElements(doc_element[key], keys_list[1:], filter_name)
			
			elif len(keys_list) == 1:
				if key in doc_element and doc_element[key] == 'true':
						return None
				else:
					return doc_element
		return doc_element

