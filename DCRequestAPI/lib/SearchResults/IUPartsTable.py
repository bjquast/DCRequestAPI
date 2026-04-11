import pudb

from ElasticSearch.FieldConfig import FieldConfig


class IUPartsTable():
	def __init__(self, selected_sourcefields):
		self.fieldconf = FieldConfig()
		self.required_sourcefields = ['StableIdentifierURL', ]
		self.selected_sourcefields = selected_sourcefields

	def __getComplexElements(self, doc_element, keys_list, valuelist = []):
		for key in keys_list:
			if key in doc_element:
				doc_element = doc_element[key]
				if isinstance (doc_element, list) or isinstance (doc_element, tuple):
					for element in doc_element:
						valuelist = self.__getComplexElements(element, keys_list[1:], valuelist)
				elif len(keys_list) > 1:
					valuelist = self.__getComplexElements(doc_element, keys_list[1:], valuelist)
				elif doc_element is None:
					pass
				else:
					valuelist.append(doc_element)
			else:
				return valuelist
		return valuelist


	def setRowContent(self, doc_sources = []):
		self.rows = []
		colkeys = list(self.selected_sourcefields)
		for key in self.required_sourcefields:
			if key not in colkeys:
				colkeys.append(key)
		
		for doc_source in doc_sources:
			source_dict = {}
			for colkey in colkeys:
				colkey_parts = colkey.split('.')
				if len(colkey_parts) > 1:
					valuelist = self.__getComplexElements(doc_source, colkey_parts, valuelist = [])
					source_dict[colkey] = [val for val in valuelist]
				
				elif colkey in doc_source:
					doc_element = doc_source[colkey]
					if isinstance(doc_element, list) or isinstance(doc_element, tuple):
						source_dict[colkey] = doc_element
					elif doc_element is None:
						source_dict[colkey] = []
					else:
						source_dict[colkey] = [doc_element]
				else:
					source_dict[colkey] = []
			self.rows.append(source_dict)
		return


	def setStableIdentifierURL(self):
		for source_dict in self.rows:
			source_dict['PartAccessionNumber'] = ['<a href="{0}">{1}</a>'.format(source_dict['StableIdentifierURL'][0], source_dict['PartAccessionNumber'][0])]
			source_dict['StableIdentifierURL'] = ['<a href="{0}">{0}</a>'.format(source_dict['StableIdentifierURL'][0])]


	def getRowContent(self, doc_sources = [], setStableIDURL = True):
		self.setRowContent(doc_sources = doc_sources)
		if setStableIDURL is True:
			self.setStableIdentifierURL()
		return self.rows



