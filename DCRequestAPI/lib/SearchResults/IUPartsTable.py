import pudb

from ElasticSearch.FieldDefinitions import FieldDefinitions


class IUPartsTable():
	def __init__(self):
		self.coldefs = {}
		self.bucketdefs = {}
		self.default_sourcefields = []
		self.selected_sourcefields = []
		self.required_sourcefields = ['StableIdentifierURL', ]
		
		self.default_bucketfields = []
		self.selected_bucketfields = []
		
		fielddefs = FieldDefinitions()
		self.fieldnames = fielddefs.fieldnames
		self.bucketfields = fielddefs.bucketfields
		self.fielddefinitions = fielddefs.fielddefinitions
		
		self.readFieldDefinitions()
		self.readBucketDefinitions()
		#self.setSourceFields()


	def readBucketDefinitions(self):
		for bucketfield in self.bucketfields:
			if bucketfield in self.fielddefinitions:
				self.bucketdefs[bucketfield] = self.fielddefinitions[bucketfield]['names']
				self.default_bucketfields.append(bucketfield)
				self.selected_bucketfields.append(bucketfield)


	def setSelectedBucketFields(self, bucketfields = []):
		self.selected_bucketfields = []
		#if len(bucketfields) <= 0:
		#	for bucketfield in self.bucketfields:
		#		self.selected_bucketfields.append(bucketfield)
		
		#else:
		for bucketfield in bucketfields:
			if bucketfield in self.bucketfields:
				self.selected_bucketfields.append(bucketfield)
		return


	def setSelectedFilterSections(self, filtersections = []):
		self.selected_filter_sections = []
		
		for filtersection in filtersections:
			# check that filtersection is available in FieldDefinitions().bucketfields
			if filtersection in self.bucketfields:
				self.selected_filter_sections.append(filtersection)
		return


	def readFieldDefinitions(self):
		for fieldname in self.fieldnames:
			if fieldname in self.fielddefinitions:
				self.coldefs[fieldname] = self.fielddefinitions[fieldname]['names']
				self.default_sourcefields.append(fieldname)
				self.selected_sourcefields.append(fieldname)


	def setSelectedSourceFields(self, sourcefields = []):
		self.selected_sourcefields = []
		if len(sourcefields) <= 0:
			for fieldname in self.fieldnames:
				self.selected_sourcefields.append(fieldname)
		
		else:
			for sourcefield in sourcefields:
				if sourcefield in self.fieldnames:
					self.selected_sourcefields.append(sourcefield)
			if 'PartAccessionNumber' not in self.selected_sourcefields:
				self.selected_sourcefields.insert(0, 'PartAccessionNumber')
		return


	def getSelectedSourceFields(self):
		return self.selected_sourcefields


	def getDefaultSourceFields(self):
		return self.default_sourcefields


	def getComplexElements(self, doc_element, keys_list, valuelist = []):
		#pudb.set_trace()
		for key in keys_list:
			if key in doc_element:
				doc_element = doc_element[key]
				if isinstance (doc_element, list) or isinstance (doc_element, tuple):
					for element in doc_element:
						valuelist = self.getComplexElements(element, keys_list[1:], valuelist)
				elif len(keys_list) > 1:
					valuelist = self.getComplexElements(doc_element, keys_list[1:], valuelist)
				elif doc_element is None:
					pass
				else:
					valuelist.append(doc_element)
			else:
				return valuelist
		return valuelist


	def setRowContent(self, doc_sources = []):
		
		self.rows = []
		
		#pudb.set_trace()
		colkeys = list(self.selected_sourcefields)
		for key in self.required_sourcefields:
			if key not in colkeys:
				colkeys.append(key)
		
		
		for doc_source in doc_sources:
			source_dict = {}
			for colkey in colkeys:
				colkey_parts = colkey.split('.')
				if len(colkey_parts) > 1:
					valuelist = self.getComplexElements(doc_source, colkey_parts, valuelist = [])
					source_dict[colkey] = [val for val in valuelist]
				
				elif colkey in doc_source:
					doc_element = doc_source[colkey]
					if isinstance(doc_element, list) or isinstance(doc_element, tuple):
						source_dict[colkey] = doc_element
					else:
						source_dict[colkey] = [doc_element]
				else:
					source_dict[colkey] = [None]
			self.rows.append(source_dict)
		return


	def setStableIdentifierURL(self):
		for source_dict in self.rows:
			source_dict['PartAccessionNumber'] = ['<a href="{0}">{1}</a>'.format(source_dict['StableIdentifierURL'][0], source_dict['PartAccessionNumber'][0])]
			source_dict['StableIdentifierURL'] = ['<a href="{0}">{0}</a>'.format(source_dict['StableIdentifierURL'][0])]


	def getRowContent(self, doc_sources = []):
		self.setRowContent(doc_sources = doc_sources)
		self.setStableIdentifierURL()
		return self.rows



