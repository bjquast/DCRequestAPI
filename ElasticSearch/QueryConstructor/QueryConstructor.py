import logging
import logging.config
logging.config.fileConfig('logging.conf')
logger = logging.getLogger('elastic_queries')

import pudb

from ElasticSearch.FieldDefinitions import FieldDefinitions


class QueryConstructor():
	def __init__(self, fielddefinitions, source_fields):
		self.source_fields = source_fields
		
		self.nested_fields = {}
		self.nested_restricted_fields = {}
		self.simple_fields = {}
		self.simple_restricted_fields = {}
		
		self.fielddefinitions = fielddefinitions


	def set_source_fields(self, source_fields = []):
		# allow to set the source fields later for queries with different source fields as in StackedInnerQuery
		if len(source_fields) > 0:
			self.source_fields = source_fields
		return


	def sort_queries_by_definitions(self):
		# reset the fields, needed when sort_queries_by_definitions is used more than once as with StackedInnerQuery
		self.nested_restricted_fields = {}
		self.nested_fields = {}
		self.simple_restricted_fields = {}
		self.simple_fields = {}
		
		for fieldname in self.source_fields:
			if fieldname in self.fielddefinitions:
				if 'buckets' in self.fielddefinitions[fieldname] \
					and 'path' in self.fielddefinitions[fieldname]['buckets'] \
					and 'field_query' in self.fielddefinitions[fieldname]['buckets'] \
					and 'withholdflags' in self.fielddefinitions[fieldname]['buckets']:
					self.nested_restricted_fields[fieldname] = self.fielddefinitions[fieldname]['buckets']
				elif 'buckets' in self.fielddefinitions[fieldname] \
					and 'path' in self.fielddefinitions[fieldname]['buckets'] \
					and 'field_query' in self.fielddefinitions[fieldname]['buckets'] \
					and 'withholdflags' not in self.fielddefinitions[fieldname]['buckets']:
					self.nested_fields[fieldname] = self.fielddefinitions[fieldname]['buckets']
				elif 'buckets' in self.fielddefinitions[fieldname] \
					and 'field_query' in self.fielddefinitions[fieldname]['buckets'] \
					and 'withholdflags' in self.fielddefinitions[fieldname]['buckets']:
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


	def getRangeType(self, query_def):
		if "type" in query_def and query_def['type'] == 'date':
			range_type = "date"
		elif "type" in query_def and query_def['type'] == 'number':
			range_type = "number"
		else:
			range_type = None
		return range_type


	def setBucketsSorting(self):
		"""
		set sorting params sorting for the aggregations
		sorting for search queries is set in ES_Searcher
		"""
		pudb.set_trace()
		self.sorting = {}
		try:
			self.buckets_sort_alphanum
			self.buckets_sort_dir
			
			if self.buckets_sort_alphanum is True:
				if self.buckets_sort_dir is None or self.buckets_sort_dir.lower() not in ['asc', 'desc']:
					self.buckets_sort_dir = 'asc'
				self.sorting = {"_key": self.buckets_sort_dir.lower()}
			else:
				if self.buckets_sort_dir is None or self.buckets_sort_dir.lower() not in ['asc', 'desc']:
					self.buckets_sort_dir = 'desc'
				self.sorting = {"_count": self.buckets_sort_dir.lower()}
		
		except AttributeError:
			self.sorting = {"_count": 'desc'}
		return


	def getStringQuerySearchField(self, key, query_def):
		# set the default value
		search_field = key
		if 'types' in query_def and 'text' in query_def['types']:
			search_field = key
		elif 'types' in query_def and 'keyword_lc' in query_def['types']:
			search_field = '{0}.{1}'.format(key, 'keyword_lc')
		elif 'types' in query_def and 'keyword' in query_def['types']:
			search_field = '{0}.{1}'.format(key, 'keyword')
		return search_field


	def removeNonTextFromSourceList(self):
		filtered_source_fields = []
		for source_field in self.source_fields:
			if source_field in self.fielddefinitions:
				if not 'type' in self.fielddefinitions[source_field]['buckets'] or self.fielddefinitions[source_field]['buckets']['type'] in ['text', 'keyword', 'keyword_lc']:
					filtered_source_fields.append(source_field)
		self.source_fields = filtered_source_fields
		return


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

