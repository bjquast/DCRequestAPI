import logging
import logging.config
logging.config.fileConfig('logging.conf')
logger = logging.getLogger('elastic_queries')

import pudb

from ElasticSearch.FieldDefinitions import FieldDefinitions # fieldnames, fielddefinitions


class QueryConstructor():
	def __init__(self, fielddefinitions, source_fields):
		self.source_fields = source_fields
		
		self.nested_fields = {}
		self.nested_restricted_fields = {}
		self.simple_fields = {}
		self.simple_restricted_fields = {}
		
		self.fielddefinitions = fielddefinitions



	def sort_queries_by_definitions(self):
		
		for fieldname in self.source_fields:
			if fieldname in self.fielddefinitions:
				if 'buckets' in self.fielddefinitions[fieldname] and 'path' in self.fielddefinitions[fieldname]['buckets'] and 'withholdflag' in self.fielddefinitions[fieldname]['buckets']:
					self.nested_restricted_fields[fieldname] = self.fielddefinitions[fieldname]['buckets']
				elif 'buckets' in self.fielddefinitions[fieldname] and 'path' in self.fielddefinitions[fieldname]['buckets'] and 'withholdflag' not in self.fielddefinitions[fieldname]['buckets']:
					self.nested_fields[fieldname] = self.fielddefinitions[fieldname]['buckets']
				elif 'buckets' in self.fielddefinitions[fieldname] and 'withholdflag' in self.fielddefinitions[fieldname]['buckets']:
					self.simple_restricted_fields[fieldname] = self.fielddefinitions[fieldname]['buckets']
				elif 'buckets' in self.fielddefinitions[fieldname]:
					self.simple_fields[fieldname] = self.fielddefinitions[fieldname]['buckets']
		return


	def setSubFilters(self):
		# when the nested objects should be filtered by a value, e. g. the parent taxa by rank
		#pudb.set_trace()
		self.subfilters = {}
		for field in self.nested_fields:
			self._setSubFilter(self.nested_fields, field)
		
		for field in self.nested_restricted_fields:
			self._setSubFilter(self.nested_restricted_fields, field)
		
		return


	def _setSubFilter(self, field_defs, field):
		if 'sub_filters' in field_defs[field]:
			for sub_filter_element in field_defs[field]['sub_filters']:
				if field not in self.subfilters:
					self.subfilters[field] = {}
				
				if sub_filter_element[0] not in self.subfilters[field]:
					self.subfilters[field][sub_filter_element[0]] = []
				
				self.subfilters[field][sub_filter_element[0]].append(sub_filter_element[1])
		return


	def getCaseInsensitiveValue(self, query_def):
		case_insensitive = "true"
		if "type" in query_def and query_def['type'] not in ['text', 'keyword', 'keyword_lc']:
			case_insensitive = "false"
		
		return case_insensitive


	def replaceBooleanValues(self, query_def, filter_values):
		if "type" in query_def and query_def['type'] in ['boolean']:
			new_values = []
			for value in filter_values:
				if value in [True, 1, '1']:
					new_values.append("true")
				elif value in [False, 0, '0']:
					new_values.append("false")
				else:
					new_values.append(value)
				return new_values
		return filter_values

