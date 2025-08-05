import pudb

from ElasticSearch.FieldConfig import FieldConfig

class FieldParameterSetter():
	def __init__(self):
		self.fieldconf = FieldConfig()
		self.fielddefinitions = self.fieldconf.fielddefinitions
		
		self.setFields()
		self.setDefaultSelectedFields()
		
		'''
		self.coldefs = {}
		self.bucketdefs = {}
		self.hierarchy_filter_names = {}
		self.default_sourcefields = []
		self.selected_sourcefields = []
		self.required_sourcefields = ['StableIdentifierURL', ]
		
		
		
		# these methods get the names, not the definitions, perhaps they should be reworked to resemble fieldconf.getHierarchyFilterNames()
		self.readFieldConfig()
		self.readBucketDefinitions()
		
		# get a dict with names for hierarchy fields 
		self.hierarchy_filter_names = fieldconf.getHierarchyFilterNames()
		'''


	def setFields(self):
		# fields to show in the result table, source_fields for ES
		self.result_fields = self.fieldconf.result_fields
		
		# fields that are available for the stacked query
		self.stacked_query_fields = self.fieldconf.stacked_query_fields
		
		# filters where user can choose from
		self.available_filter_fields = self.fieldconf.available_filter_fields
		# filters to show when user have not selected any
		self.default_filter_sections = self.fieldconf.default_filter_sections
		
		# fields sorted by the different types of filters
		self.term_fields = self.fieldconf.term_fields
		self.hierarchy_filter_fields = self.fieldconf.hierarchy_filter_fields
		self.date_fields = self.fieldconf.date_fields
		
		# fields just taken from fieldconf
		self.stacked_query_fields = self.fieldconf.stacked_query_fields
		return


	def setDefaultSelectedFields(self):
		# set a list of default fields for all selectable fields
		self.selected_sourcefields = self.result_fields
		self.selected_filter_fields = []
		self.selected_filter_sections = self.default_filter_sections
		self.selected_hierarchy_fields = self.hierarchy_filter_fields
		self.selected_date_fields = self.date_fields
		self.selected_term_fields = []
		return


	# methods to select fields with fallback to defaults
	def setSelectedSourceFields(self, sourcefields = []):
		if len(sourcefields) <= 0:
			self.selected_sourcefields = self.result_fields
		else:
			self.selected_sourcefields = []
			for sourcefield in sourcefields:
				if sourcefield in self.result_fields:
					self.selected_sourcefields.append(sourcefield)
			if 'PartAccessionNumber' not in self.selected_sourcefields:
				self.selected_sourcefields.insert(0, 'PartAccessionNumber')
		return


	def setSelectedFilterFields(self, filter_fields = []):
		if len(filter_fields) <= 0:
			self.selected_filter_fields = []
		else:
			self.selected_filter_fields = []
			for filter_field in filter_fields:
				if filter_field in self.available_filter_fields:
					self.selected_filter_fields.append(filter_field)
		return


	def appendSelectedFilterFields(self, filter_fields = []):
		new_selected_fields = []
		for field in self.available_filter_fields:
			if field in filter_fields or field in self.selected_filter_fields:
				new_selected_fields.append(field)
		if len(new_selected_fields) <= 0:
			self.selected_filter_fields = self.default_filter_sections
		else:
			self.selected_filter_fields = new_selected_fields
		return


	def setSelectedFilterSections(self, filter_sections = []):
		if len(filter_sections) <= 0:
			self.selected_filter_sections = self.default_filter_sections
		else:
			self.selected_filter_sections = []
			for filter_section in filter_sections:
				if filter_section in self.available_filter_fields:
					self.selected_filter_sections.append(filter_section)
		return


	def setSelectedHierarchyFields(self, hierarchy_fields = []):
		if len(hierarchy_fields) <= 0:
			self.selected_hierarchy_fields = self.hierarchy_filter_fields
		else:
			self.selected_hierarchy_fields = []
			for hierarchy_field in hierarchy_fields:
				if hierarchy_field in self.hierarchy_filter_fields:
					self.selected_hierarchy_fields.append(hierarchy_field)
		return


	def setSelectedDateFields(self, date_fields = []):
		if len(date_fields) <= 0:
			self.selected_date_fields = self.date_fields
		else:
			self.selected_date_fields = []
			for date_field in date_fields:
				if date_field in self.date_fields:
					self.selected_date_fields.append(date_field)
		return


	def setSelectedTermFields(self, term_fields = []):
		# self.selected_term_fields should be empty by default
		self.selected_term_fields = []
		for term_field in term_fields:
			if term_field in self.term_fields:
				self.selected_term_fields.append(term_field)
		return


	'''
	def __setSelectedFields(self, to_select, selected_fields, default_fields, all_fields):
		if len(to_select) <= 0:
			selected_fields = default_fields
		else:
			selected_fields = []
			for field in to_selected:
				if field in all_fields:
					selected_fields.append(field)
		return
	'''


