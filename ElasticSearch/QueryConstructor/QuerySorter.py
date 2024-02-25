import logging
import logging.config
logging.config.fileConfig('logging.conf')
logger = logging.getLogger('elastic_queries')

import pudb

from ElasticSearch.FieldDefinitions import FieldDefinitions # fieldnames, fielddefinitions


class QuerySorter():
	def __init__(self, source_fields = []):
		self.source_fields = source_fields
		
		self.nested_fields = {}
		self.nested_restricted_fields = {}
		self.simple_fields = {}
		self.simple_restricted_fields = {}

		fielddefs = FieldDefinitions()
		self.fieldnames = fielddefs.fieldnames
		self.fielddefinitions = fielddefs.fielddefinitions



	def sort_queries_by_definitions(self):
		if len(self.source_fields) > 0:
			pass
		else:
			self.source_fields = self.fieldnames
		
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



