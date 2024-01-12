import pudb

from DCRequestAPI.lib.ElasticSearch.FieldDefinitions import fieldnames, fielddefinitions


class IUPartsListTable():
	def __init__(self):
		self.coldefs = {}
		
		self.readFieldDefinitions()
		self.setColDefsOrder()


	def setColDefsOrder(self, colkeys = []):
		self.ordered_coldefs = []
		if len(colkeys) <= 0:
			for fieldname in fieldnames:
				self.ordered_coldefs.append(fieldname)
		
		else:
			for colkey in colkeys:
				if colkey in fieldnames:
					self.ordered_coldefs.append(colkey)
		return


	def readFieldDefinitions(self):
		
		for fieldname in fieldnames:
			if fieldname in fielddefinitions:
				self.coldefs[fieldname] = fielddefinitions[fieldname]['names']


	def getSourceFields(self):
		source_fields = [colkey for colkey in self.coldefs]
		
		if 'Projects.ProjectID' not in self.coldefs:
			source_fields.append('Projects.ProjectID')
		
		return source_fields


	def getColHeaders(self, lang = 'en'):
		self.colheaders = []
		for colkey in self.ordered_coldefs:
			self.colheaders.append(self.coldefs[colkey])
		return self.colheaders


	def setRowContent(self, doc_sources = [], users_project_ids = []):
		
		self.rows = []
		
		for doc_source in doc_sources:
			values = []
			for colkey in self.coldefs:
				colkey_parts = colkey.split('.')
				if len(colkey_parts) > 1:
					valuelist = self.getComplexElements(doc_source, colkey_parts, valuelist = [])
					value = ',\n'.join(valuelist)
					values.append(value)
				elif colkey in doc_source:
					doc_element = doc_source[colkey]
					if isinstance(doc_element, list) or isinstance(doc_element, tuple):
						value = ',\n'.join.doc_element
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
