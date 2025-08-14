import pudb

import threading
from ElasticSearch.ES_Mappings import MappingsDict


# TODO: read the fields that must be withholded from withholdfilters and add the according fields for withholdflags
# for each item in self.fielddefinitions 

# make it a singleton?!


class FieldConfig:
	"""
	Class that sets the fields for the different ElasticSearch query and aggregation types and for the web interface
	"""
	# code to make it a singleton
	_instance = None
	_lock = threading.Lock()

	def __new__(cls, *args, **kwargs):
		if cls._instance is None: 
			with cls._lock:
				# Another thread could have created the instance
				# before we acquired the lock. So check that the
				# instance is still nonexistent.
				if not cls._instance:
					cls._instance = super().__new__(cls)
		return cls._instance
	# end singleton code


	def __init__(self):
		self.setFields()
		self.setFieldDefinitions()
		self.appendTaxonRankDefinitions()
		
		self.es_mappings = MappingsDict['iuparts']
		self.setFieldTypes()


	def setResultFields(self):
		"""
		all fields that should be shown in the result table
		"""
		self.result_fields = [
			'PartAccessionNumber',
			#'StableIdentifierURL',
			'LastIdentificationCache',
			'VernacularTerms',
			'MatchedSynonyms.Synonym',
			#'FamilyCache',
			#'OrderCache',
			#'MatchedTaxon',
			'MatchedParentTaxa',
			'TypeStatus',
			'MaterialCategory',
			'LocalityVerbatim',
			'LocalityDescription',
			'HabitatDescription',
			'CollectingMethod',
			'CountryCache',
			'WGS84_Coordinate',
			'CollectionDate',
			'CollectionAgents.CollectorsName',
			'LifeStage',
			'Gender',
			'NumberOfUnits',
			'CollectionName',
			'Projects.Project',
			'CollectionSpecimenID',
			'IdentificationUnitID',
			'SpecimenPartID',
			'Barcodes.Methods.region',
			'DatabaseAccronym',
		]
		return


	def setFilterDefs(self):
		"""
		all filters that may occur in filters,
		this list exists to give the order of the filters
		the lists term_fields, self.hierarchy_filter_fields, date_fields
		provide the filters ordered by data type, default_filter_sections
		sets the list of filters when no filters are selected
		"""
		
		# each entry has a list with values for: [available, is shown by default in filters, type of filter]
		
		self.filter_defs = [
			{'DatabaseAccronym': [True, True, 'term']},
			{'AccessionDate': [True, False, 'date']},
			#{'CollectionsTree.CollectionName': [False, False, 'term']},
			{'CollectionName': [True, True, 'term']},
			#{'CollectionsTree': [False, False, 'term']},
			{'CollectionHierarchyString': [True, False, 'hierarchy']},
			{'Projects.Project': [True, True, 'term']},
			{'LastIdentificationCache': [True, True, 'term']},
			{'MatchedTaxon': [True, True, 'term']},
			{'VernacularTerms': [True, True, 'term']},
			{'MatchedSynonyms.Synonym': [True, True, 'term']},
			{'MatchedTaxaTree': [True, True, 'term']},
			{'MatchedTaxaTree.Phylum': [True, False, 'term']},
			{'MatchedTaxaTree.Subphylum': [True, False, 'term']},
			{'MatchedTaxaTree.Class': [True, False, 'term']},
			{'MatchedTaxaTree.Subclass': [True, False, 'term']},
			{'MatchedTaxaTree.Order': [True, False, 'term']},
			{'MatchedTaxaTree.Suborder': [True, False, 'term']},
			{'MatchedTaxaTree.Family': [True, False, 'term']},
			{'MatchedTaxaTree.Subfamily': [True, False, 'term']},
			{'MatchedTaxaTree.Genus': [True, False, 'term']},
			#{'MatchedTaxaTree.Subgenus': [False, False, 'term']},
			#{'MatchedTaxaHierarchyString': [False, False, 'hierarchy']},
			{'TypeStatus': [True, True, 'term']},
			{'CountryCache': [True, True, 'term']},
			{'CollectionDate': [True, True, 'date']},
			{'CollectingMethod': [True, False, 'term']},
			{'CollectionAgents.CollectorsName': [True, False, 'term']},
			{'LocalityVerbatim': [True, False, 'term']},
			{'LocalityDescription': [True, False, 'term']},
			{'HabitatDescription': [True, False, 'term']},
			{'MaterialCategory': [True, False, 'term']},
			{'LifeStage': [True, False, 'term']},
			{'Gender': [True, False, 'term']},
			{'NumberOfUnits': [True, False, 'term']},
			{'Barcodes.Methods.region': [True, False, 'term']},
			{'ImagesAvailable': [True, True, 'term']}
			
		]
		return


	def setFilterFields(self):
		"""
		set all filter fields that are available
		containing term filters, date filters hierarchy filters ...
		"""
		self.available_filter_fields = []
		for field in self.filter_defs:
			for key in field:
				if field[key][0] is True:
					self.available_filter_fields.append(key)
		return


	def setTermFields(self):
		self.term_fields = []
		
		for field in self.filter_defs:
			for key in field:
				if field[key][0] is True and field[key][2] == 'term':
					self.term_fields.append(key)
		return


	def setDateFields(self):
		"""
		all fields with type date that should be used in web interface
		"""
		self.date_fields = []
		
		for field in self.filter_defs:
			for key in field:
				if field[key][0] is True and field[key][2] == 'date':
					self.date_fields.append(key)
		return


	def setDefaultFilterSections(self):
		"""
		all fields that are in the filter section when no filters are selected
		"""
		self.default_filter_sections = []
		
		for field in self.filter_defs:
			for key in field:
				if field[key][0] is True and field[key][1] is True:
					self.default_filter_sections.append(key)
		return



	def setStackedQueryFields(self):
		"""
		all fields that can be used in stacked queries
		"""
		self.stacked_query_fields = [
			'PartAccessionNumber',
			'LastIdentificationCache',
			'VernacularTerms',
			'MatchedSynonyms.Synonym',
			#'FamilyCache',
			#'OrderCache',
			#'MatchedTaxon',
			'MatchedParentTaxa',
			'TypeStatus',
			'MaterialCategory',
			'LocalityVerbatim',
			'LocalityDescription',
			'HabitatDescription',
			'CollectingMethod',
			'CountryCache',
			'CollectionDate',
			'CollectionAgents.CollectorsName',
			'LifeStage',
			'Gender',
			'NumberOfUnits',
			'CollectionName',
			'Projects.Project',
			'CollectionSpecimenID',
			'IdentificationUnitID',
			'SpecimenPartID',
			'Barcodes.Methods.region',
			'DatabaseAccronym',
		]
		return


	def setHierarchyFilterFields(self):
		"""
		all fields used in hierarchy based filters
		"""
		self.hierarchy_filter_fields = [
			'MatchedTaxaHierarchyString',
			'CollectionHierarchyString'
		]
		return


	def setSuggestionFields(self):
		"""
		all fields used for suggestions for filters
		"""
		self.suggestion_fields = [
			#'CollectionsTree.CollectionName',
			'CollectionName',
			'Projects.Project',
			'LastIdentificationCache',
			'MatchedTaxon',
			'VernacularTerms',
			'MatchedSynonyms.Synonym',
			'TypeStatus',
			'MatchedTaxaTree',
			#'MatchedTaxaTree.Phylum',
			#'MatchedTaxaTree.Subphylum',
			#'MatchedTaxaTree.Class',
			#'MatchedTaxaTree.Subclass',
			#'MatchedTaxaTree.Order',
			#'MatchedTaxaTree.Suborder',
			#'MatchedTaxaTree.Family',
			#'MatchedTaxaTree.Subfamily',
			#'MatchedTaxaTree.Genus',
			#'MatchedTaxaTree.Subgenus',
			'MaterialCategory',
			'LocalityVerbatim',
			'LocalityDescription',
			'HabitatDescription',
			'CountryCache',
			'CollectingMethod',
			'CollectionAgents.CollectorsName',
			'MaterialCategory',
			'LifeStage',
			'Gender',
			'Barcodes.Methods.region',
		]
		return


	def setFields(self):
		"""
		selt the lists of names for the different parts of the web interface
		"""
		
		self.setResultFields()
		
		self.setFilterDefs()
		self.setFilterFields()
		self.setTermFields()
		self.setDefaultFilterSections()
		self.setStackedQueryFields()
		self.setHierarchyFilterFields()
		self.setSuggestionFields()
		self.setDateFields()
		
		return


	# read the definitions for specific fields
	def getTermFilterNames(self):
		term_filter_defs = {}
		for term_field in self.term_fields:
			if term_field in self.fielddefinitions:
				term_filter_defs[term_field] = self.fielddefinitions[term_field]['names']
		return term_filter_defs


	def getFilterNames(self):
		filter_defs = {}
		for field in self.available_filter_fields:
			if field in self.fielddefinitions:
				filter_defs[field] = self.fielddefinitions[field]['names']
		return filter_defs


	def getColNames(self):
		colnames = {}
		for fieldname in self.result_fields:
			if fieldname in self.fielddefinitions:
				colnames[fieldname] = self.fielddefinitions[fieldname]['names']
		return colnames


	def getHierarchyFilterNames(self):
		hierarchy_filter_names = {}
		for hierarchy_filter in self.hierarchy_filter_fields:
			if hierarchy_filter in self.fielddefinitions:
				hierarchy_filter_names[hierarchy_filter] = self.fielddefinitions[hierarchy_filter]['names']
		return hierarchy_filter_names


	def setFieldDefinitions(self):
		"""
		definitions of the fields for elastic search requests 
		and labels in web interface
		"""
		self.fielddefinitions = {
			'PartAccessionNumber': {
				'names': {'en': 'Accessionnumber', },
				'buckets': {
					'field_query': 'PartAccessionNumber.keyword', 
				},
				
			},
			
			'StableIdentifierURL': {
				'names': {'en': 'URL', },
				'buckets': {
					'field_query': 'StableIdentifierURL', 
				},
				
			},
			
			'LastIdentificationCache': {
				'names': {'en': 'Identified Taxon'},
				'buckets': {
					'field_query': 'LastIdentificationCache.keyword', 
				},
			},
			
			'VernacularTerms': {
				'names': {'en': 'Vernacular name'},
				'buckets': {
					'field_query': 'VernacularTerms.keyword',
				},
			},
			
			'FamilyCache': {
				'names': {'en': 'Family'},
				'buckets': {
					'field_query': 'FamilyCache.keyword', 
				},
			},
			
			'OrderCache': {
				'names': {'en': 'Order'},
				'buckets': {
					'field_query': 'OrderCache.keyword', 
				},
			},
			
			'MatchedTaxon': {
				'names': {'en': 'Accepted Taxon'},
				'buckets': {
					'field_query': 'MatchedTaxon', 
				},
			},
			
			'MatchedParentTaxa': {
				'names': {'en': 'Taxonomy'},
				'buckets': {
					'field_query': 'MatchedParentTaxa.keyword', 
				},
			},
			
			'MatchedTaxaTree': {
				'names': {'en': 'Taxonomy'},
				'buckets': {
					'field_query': 'MatchedTaxaTree.Taxon',
					'id_field_for_tree': 'MatchedTaxaTree.TaxonURI',
					'parent_id_field_for_tree': 'MatchedTaxaTree.ParentTaxonURI',
					'path': 'MatchedTaxaTree'
				}
			},
			
			'MatchedTaxaHierarchyString': {
				'names': {'en': 'Taxonomic Tree'},
				'buckets': {
					'field_query': 'MatchedTaxaHierarchyString.facet'
				}
			},
			
			'MatchedSynonyms.Synonym': {
				'names': {'en': 'Synonym'},
				'buckets': {
					'field_query': 'MatchedSynonyms.Synonym.keyword'
				},
			},
			
			'TypeStatus': {
				'names': {'en': 'Type status'},
				'buckets': {
					'field_query': 'TypeStatus.keyword'
				},
			},
			
			'MaterialCategory': {
				'names': {'en': 'Material category'},
				'buckets': {
					'field_query': 'MaterialCategory.keyword',
					'withholdflags': ['PartWithhold'],
				},
			},
			
			'AccessionDate': {
				'names': {'en': 'Date of accession'},
				'buckets': {
					'field_query': 'AccessionDate',
					'type': 'date'
				}
			},
			
			'SpecimenCreatedWhen': {
				'names': {'en': 'Date of database submission'},
				'buckets': {
					'field_query': 'SpecimenCreatedWhen',
					'type': 'date'
				}
			},
			
			'LocalityVerbatim': {
				'names': {'en': 'Sampling locality'},
				'buckets': {
					'field_query': 'LocalityVerbatim.keyword',
					'withholdflags': ['EventWithhold', 'embargo_event_but_country', 'embargo_event_but_country_after_1992'],
				},
			},
			
			'LocalityDescription': {
				'names': {'en': 'Locality description'},
				'buckets': {
					'field_query': 'LocalityDescription.keyword',
					'withholdflags': ['EventWithhold', 'embargo_event_but_country', 'embargo_event_but_country_after_1992'],
				},
			},
			
			'HabitatDescription': {
				'names': {'en': 'Habitat'},
				'buckets': {
					'field_query': 'HabitatDescription.keyword',
					'withholdflags': ['EventWithhold', 'embargo_event_but_country', 'embargo_event_but_country_after_1992'],
				},
			},
			
			'CollectingMethod': {
				'names': {'en': 'Collecting method'},
				'buckets': {
					'field_query': 'CollectingMethod.keyword',
					'withholdflags': ['EventWithhold', 'embargo_event_but_country', 'embargo_event_but_country_after_1992'],
				},
			},
			
			'CountryCache': {
				'names': {'en': 'Country'},
				'buckets': {
					'field_query': 'CountryCache.keyword',
					'withholdflags': ['EventWithhold'],
				},
			},
			
			'CollectionDate': {
				'names': {'en': 'Collection date'},
				'buckets': {
					'field_query': 'CollectionDate',
					'type': 'date'
				}
			},
			
			'WGS84_Coordinate': {
				# does not have buckets key, so it does not occur in aggregations, term filters and queries
				'names': {'en': 'Coordinate'},
			},
			
			'CollectionAgents.CollectorsName': {
				'names': {'en': 'Collector(s)'},
				'buckets': {
					'field_query': 'CollectionAgents.CollectorsName.keyword',
					'withholdflags': ['CollectionAgents.CollectorsWithhold', 'CollectionAgents.embargo_collector', 'CollectionAgents.embargo_anonymize_collector'],
					'path': 'CollectionAgents',
				},
			},
			
			# IUWithhold is ignored here as it is used for withholding the complete IdentificationUnitPart when it is set
			'LifeStage': {
				'names': {'en': 'Life stage'},
				'buckets': {
					'field_query': 'LifeStage.keyword',
				},
			},
			
			'Gender': {
				'names': {'en': 'Sex'},
				'buckets': {
					'field_query': 'Gender.keyword',
				},
			},
			
			'NumberOfUnits': {
				'names': {'en': 'Number of specimens'},
				'buckets': {
					'field_query': 'NumberOfUnits',
				},
			},
			
			'NumberOfSpecimenImages': {
				# this field is in iuparts object, not in Images
				'names': {'en': 'Number of images'},
				'buckets': {
					'field_query': 'NumberOfSpecimenImages',
					'type': 'number'
				},
			},
			
			'ImagesAvailable': {
				'names': {'en': 'Image(s)'},
				'buckets': {
					'field_query': 'ImagesAvailable',
					'withholdflags': ['ImagesWithhold']
				},
			},
			
			'CollectionName': {
				'names': {'en': 'Collection'},
				'buckets': {
					'field_query': 'CollectionName.keyword',
				},
			},
			
			'CollectionsTree': {
				'names': {'en': 'Collection(s)'},
				'buckets': {
					'field_query': 'CollectionsTree.CollectionName',
					'path': 'CollectionsTree',
					'id_field_for_tree': 'CollectionsTree.CollectionID',
					'parent_id_field_for_tree': 'CollectionsTree.ParentCollectionID'
				}
			},
			
			'CollectionHierarchyString': {
				'names': {'en': 'Collections (hierarchical)'},
				'buckets': {
					'field_query': 'CollectionHierarchyString.facet'
				}
			},
			
			'Projects.Project': {
				'names': {'en': 'Project(s)'},
				'buckets': {
					'field_query': 'Projects.Project.keyword',
				},
			},
			
			'DatabaseAccronym': {
				'names': {'en': 'Database'},
				'buckets': {
					'field_query': 'DatabaseAccronym.keyword',
				},
			},
			
			'CollectionSpecimenID': {
				'names': {'en': 'CollectionSpecimenID'},
				'buckets': {
					'field_query': 'CollectionSpecimenID'
				},
			},
			
			'IdentificationUnitID': {
				'names': {'en': 'IdentificationUnitID'},
				'buckets': {
					'field_query': 'IdentificationUnitID'
				},
			},
			
			'SpecimenPartID': {
				'names': {'en': 'SpecimenPartID'},
				'buckets': {
					'field_query': 'SpecimenPartID'
				},
			},
			
			'Barcodes.Methods.region': {
				'names': {'en': 'Barcode Marker'},
				'buckets': {
					'field_query': 'Barcodes.Methods.region.keyword',
				},
				
			}
			
		}
		
		return


	def appendTaxonRankDefinitions(self):
		rank_names = {
			'reg.': {'en': 'Regnum'}, 
			'phyl./div.': {'en': 'Phylum'}, 
			'subphyl./div.': {'en': 'Subphylum'}, 
			'cl.': {'en': 'Class'}, 
			'subcl.': {'en': 'Subclass'}, 
			'ord.': {'en': 'Order'}, 
			'subord.': {'en': 'Suborder'}, 
			'fam.': {'en': 'Family'}, 
			'subfam.': {'en': 'Subfamily'}, 
			'gen.': {'en': 'Genus'}, 
			'subgen.': {'en': 'Subgenus'},
		}
		
		
		for rank in ['reg.', 'phyl./div.', 'subphyl./div.', 'cl.', 'subcl.', 'ord.', 'subord.', 'fam.', 'subfam.', 'gen.', 'subgen.']:
		#for rank in ['Regnum', 'Phylum', 'Subphylum', 'Class', 'Subclass', 'Order', 'Suborder', 'Family', 'Subfamily', 'Genus', 'Subgenus']:
		
			self.fielddefinitions['MatchedTaxaTree.{0}'.format(rank_names[rank]['en'])] = {
				'names': {'en': rank_names[rank]['en']},
				'buckets': {
					'field_query': 'MatchedTaxaTree.Taxon',
					'filter': None,
					'path': 'MatchedTaxaTree',
					'sub_filters': [['MatchedTaxaTree.Rank', rank],]
				}
			}
		
		return


	def setFieldTypes(self):
		for field in self.fielddefinitions:
			
			field_keys = field.split('.')
			
			sub_dict = dict(self.es_mappings)
			for key in field_keys:
				if key in sub_dict['properties']:
					sub_dict = sub_dict['properties'][key]
			
					if 'type' in sub_dict:
						if 'buckets' in self.fielddefinitions[field]:
							self.fielddefinitions[field]['buckets']['types'] = [sub_dict['type']]
							if 'fields' in sub_dict:
								for typename in sub_dict['fields']:
									self.fielddefinitions[field]['buckets']['types'].append(typename)
		
		return


