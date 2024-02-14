import pudb

from ElasticSearch.FieldDefinitions import fieldnames, fielddefinitions


class IUPartsListTable():
	def __init__(self):
		self.coldefs = {}
		self.default_sourcefields = []
		self.selected_sourcefields = []
		
		self.readFieldDefinitions()
		#self.setSourceFields()


	def readFieldDefinitions(self):
		for fieldname in fieldnames:
			if fieldname in fielddefinitions:
				self.coldefs[fieldname] = fielddefinitions[fieldname]['names']
				self.default_sourcefields.append(fieldname)
				self.selected_sourcefields.append(fieldname)


	def setSelectedSourceFields(self, sourcefields = []):
		self.selected_sourcefields = []
		if len(sourcefields) <= 0:
			for fieldname in fieldnames:
				self.selected_sourcefields.append(fieldname)
		
		else:
			for sourcefield in sourcefields:
				if sourcefield in fieldnames:
					self.selected_sourcefields.append(sourcefield)
			if 'PartAccessionNumber' not in self.selected_sourcefields:
				self.selected_sourcefields.insert(0, 'PartAccessionNumber')
			if 'StableIdentifierURL' not in self.selected_sourcefields:
				self.selected_sourcefields.insert(1, 'StableIdentifierURL')
		return


	def getSelectedSourceFields(self):
		return self.selected_sourcefields


	def getDefaultSourceFields(self):
		return self.default_sourcefields


	def setRowContent(self, doc_sources = [], users_project_ids = []):
		
		self.rows = []
		
		#pudb.set_trace()
		
		for doc_source in doc_sources:
			values = []
			for colkey in self.selected_sourcefields:
				colkey_parts = colkey.split('.')
				if len(colkey_parts) > 1:
					valuelist = self.getComplexElements(doc_source, colkey_parts, valuelist = [])
					value = ',\n'.join([str(val) for val in valuelist])
					values.append(value)
				elif colkey in doc_source:
					doc_element = doc_source[colkey]
					if isinstance(doc_element, list) or isinstance(doc_element, tuple):
						value = ',\n'.join(doc_element)
						values.append(value)
					else:
						values.append(doc_element)
				else:
					values.append(None)
			self.rows.append(values)
		return


	def getRowContent(self, doc_sources = [], users_project_ids = []):
		self.setRowContent(doc_sources = doc_sources, users_project_ids = users_project_ids)
		return self.rows


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
