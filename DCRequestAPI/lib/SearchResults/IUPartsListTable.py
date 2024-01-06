import pudb

from DCRequestAPI.lib.ElasticSearch.FieldDefinitions import fieldnames, fielddefinitions
from DCRequestAPI.lib.SearchResults.WithholdFilters import WithholdFilters


class IUPartsListTable():
	def __init__(self):
		self.colnames = {}
		
		self.withholdfilters = WithholdFilters()
		self.withhold_fields = self.withholdfilters.getWithholdFields()
		
		self.readFieldDefinitions()


	def readFieldDefinitions(self):
		
		for fieldname in fieldnames:
			if fieldname in fielddefinitions:
				self.colnames[fieldname] = fielddefinitions[fieldname]['names']


	def getSourceFields(self):
		source_fields = [colname for colname in self.colnames]
		source_fields.extend(self.withhold_fields)
		
		if 'Projects.ProjectID' not in self.colnames:
			source_fields.append('Projects.ProjectID')
		
		return source_fields


	def setColHeaders(self, colnames = [], lang = 'en'):
		self.colheaders = []
		
		if len(colnames) <= 0:
			for colname in self.colnames:
				self.colheaders.append(self.colnames[colname][lang])
		else:
			for colname in colnames:
				if colname in self.colnames:
					self.colheaders.append(self.colnames[colname][lang])
		return


	def getColHeaders(self, colnames = [], lang = 'en'):
		self.setColHeaders(colnames = colnames, lang = lang)
		return self.colheaders


	def setRowContent(self, doc_sources = [], users_project_ids = []):
		doc_sources = self.withholdfilters.applyFiltersToSources(doc_sources, users_project_ids)
		
		self.rows = []
		pudb.set_trace()
		for doc_source in doc_sources:
			values = []
			for colname in self.colnames:
				colname_keys = colname.split('.')
				if len(colname_keys) > 1:
					valuelist = self.getComplexElements(doc_source, colname_keys, valuelist = [])
					value = ',\n'.join(valuelist)
					values.append(value)
				else:
					doc_element = doc_source[colname]
					if isinstance(doc_element, list) or isinstance(doc_element, tuple):
						value = ',\n'.join.doc_element
						values.append(value)
					else:
						values.append(doc_element)
			self.rows.append(values)
		return


	def getRowContent(self, doc_sources = [], users_project_ids = []):
		self.setRowContent(doc_sources = doc_sources, users_project_ids = users_project_ids)
		return self.rows


	def getComplexElements(self, doc_element, keys_list, valuelist = []):
		#pudb.set_trace()
		while len(keys_list) > 0:
			key = keys_list.pop(0)
			if key in doc_element:
				doc_element = doc_element[key]
				if isinstance (doc_element, list) or isinstance (doc_element, tuple):
					for element in doc_element:
						valuelist = self.getComplexElements(element, keys_list, valuelist)
				elif len(keys_list) > 1:
					valuelist = self.getComplexElements(doc_element, keys_list, valuelist)
				elif doc_element is None:
					pass
				else:
					valuelist.append(doc_element)
			else:
				pass
		return valuelist
