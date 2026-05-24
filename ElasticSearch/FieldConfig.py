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
			'MediaTypes.MediaType',
			'DatabaseAccronym',
			'SpecimenCreatedWhen',
			'AccessionDate',
		]
		return


	def setFilterDefs(self):
		"""
		all filters that may occur in filters,
		this list exists to give the order of the filters
		the lists term_fields, self.hierarchy_fields, date_fields
		provide the filters ordered by data type, default_filter_sections
		sets the list of filters when no filters are selected
		"""
		
		# each entry has a list with values for: [available, is shown by default in filters, used in stacked query, type of filter]
		
		self.filter_defs = [
			{'PartAccessionNumber': [False, False, True, 'term']},
			{'DatabaseAccronym': [True, True, True, 'term']},
			{'AccessionDate': [True, False, False, 'date']},
			{'SpecimenCreatedWhen': [True, False, True, 'date']},
			{'CollectionName': [True, True, True, 'term']},
			{'Projects.Project': [True, True, True, 'term']},
			{'LastIdentificationCache': [True, True, True, 'term']},
			{'MatchedTaxon': [True, True, False, 'term']},
			{'MatchedParentTaxa': [False, False, True, 'term']},
			{'VernacularTerms': [True, True, True, 'term']},
			{'MatchedSynonyms.Synonym': [True, True, True, 'term']},
			{'MatchedTaxaTree': [True, True, False, 'term']},
			{'MatchedTaxaTree.Phylum': [True, False, False, 'term']},
			{'MatchedTaxaTree.Subphylum': [True, False, False, 'term']},
			{'MatchedTaxaTree.Class': [True, False, False, 'term']},
			{'MatchedTaxaTree.Subclass': [True, False, False, 'term']},
			{'MatchedTaxaTree.Order': [True, False, False, 'term']},
			{'MatchedTaxaTree.Suborder': [True, False, False, 'term']},
			{'MatchedTaxaTree.Family': [True, False, False, 'term']},
			{'MatchedTaxaTree.Subfamily': [True, False, False, 'term']},
			{'MatchedTaxaTree.Genus': [True, False, False, 'term']},
			{'TypeStatus': [True, True, True, 'term']},
			{'CountryCache': [True, True, True, 'term']},
			{'CollectionDate': [True, True, True, 'date']},
			{'CollectingMethod': [True, False, True, 'term']},
			{'CollectionAgents.CollectorsName': [True, False, True, 'term']},
			{'LocalityVerbatim': [True, False, True, 'term']},
			{'LocalityDescription': [True, False, True, 'term']},
			{'HabitatDescription': [True, False, True, 'term']},
			{'MaterialCategory': [True, False, True, 'term']},
			{'LifeStage': [True, False, True, 'term']},
			{'Gender': [True, False, True, 'term']},
			{'NumberOfUnits': [True, False, True, 'term']},
			{'Barcodes.Methods.region': [True, False, True, 'term']},
			{'MediaTypes.MediaType': [True, True, False, 'term']},
			{'ImagesAvailable': [False, True, False, 'term']},
			{'CollectionSpecimenID': [False, False, True, 'term']},
			{'IdentificationUnitID': [False, False, True, 'term']},
			{'SpecimenPartID': [False, False, True, 'term']},
			
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
				if field[key][0] is True and field[key][3] == 'term':
					self.term_fields.append(key)
		return


	def setDateFields(self):
		"""
		all fields with type date that should be used in web interface
		"""
		self.date_fields = []
		
		for field in self.filter_defs:
			for key in field:
				if field[key][0] is True and field[key][3] == 'date':
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
		sorted as to be shown in select box
		"""
		self.stacked_query_fields = [
			'PartAccessionNumber',
			'LastIdentificationCache',
			'SpecimenCreatedWhen',
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
			'MediaTypes.MediaType',
			'DatabaseAccronym',
		]
		return


	def setHierarchyFilterFields(self):
		"""
		all fields used in hierarchy based filters
		"""
		self.hierarchy_fields = [
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
			'MediaTypes.MediaType',
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
		for hierarchy_filter in self.hierarchy_fields:
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
				'description': 'The accession number of a part of a collected specimen. Such a specimen part may contain individual objects from a collected specimen (e.g. organisms or minerals) or parts from the dissection of such objects (e.g. the leg of a spider). Specimen parts may hold several individuals or parts of them, but they must belong to the same specimen',
				'buckets': {
					'field_query': 'PartAccessionNumber.keyword', 
				},
				
			},
			
			'StableIdentifierURL': {
				'names': {'en': 'URL', },
				'description': 'The URL refering to a specimen part in the collection database. It is composed of a base URL for each database and the ids in the tables CollectionSpecimen, IdentificationUnit, CollectionSpecimenPart',
				'buckets': {
					'field_query': 'StableIdentifierURL', 
				},
				
			},
			
			'LastIdentificationCache': {
				'names': {'en': 'Identified Taxon'},
				'description': 'The newest assignment of a scientific name to an object. Because of scientific progress names of species or other objects might change over the time. The names (identifications) given before are kept in the database. LastIdentificationCache holds the current most identification.',
				'buckets': {
					'field_query': 'LastIdentificationCache.keyword', 
				},
			},
			
			'VernacularTerms': {
				'names': {'en': 'Vernacular name'},
				'description': 'Commonly used names of an object (e.g. species, mineral, or fossil) in different languages.',
				'buckets': {
					'field_query': 'VernacularTerms.keyword',
				},
			},
			
			'FamilyCache': {
				'names': {'en': 'Family'},
				'description': 'The taxonomic name of an organism at Family rank',
				'buckets': {
					'field_query': 'FamilyCache.keyword', 
				},
			},
			
			'OrderCache': {
				'names': {'en': 'Order'},
				'description': 'The taxonomic name of an organism at Order rank',
				'buckets': {
					'field_query': 'OrderCache.keyword', 
				},
			},
			
			'MatchedTaxon': {
				'names': {'en': 'Accepted Taxon'},
				'description': 'The accepted scientific name of an object as is supported by curated taxonomies like GBIF backbone taxonomy or Catalog of Life',
				'buckets': {
					'field_query': 'MatchedTaxon', 
				},
			},
			
			'MatchedParentTaxa': {
				'names': {'en': 'Taxonomy'},
				'description': 'The accepted taxonomic hierarchy of an object as is supported by curated taxonomies like GBIF backbone taxonomy or Catalog of Life. The field contains a list of taxon names at all ranks including the taxon in the MatchedTaxon field',
				'buckets': {
					'field_query': 'MatchedParentTaxa.keyword', 
				},
			},
			
			'MatchedTaxaTree': {
				'names': {'en': 'Taxonomy'},
				'description': 'Names and ids of a taxonomic hierarchy of an object as is supported by curated taxonomies like GBIF backbone taxonomy or Catalog of Life',
				'buckets': {
					'field_query': 'MatchedTaxaTree.Taxon',
					'id_field_for_tree': 'MatchedTaxaTree.TaxonURI',
					'parent_id_field_for_tree': 'MatchedTaxaTree.ParentTaxonURI',
					'path': 'MatchedTaxaTree'
				}
			},
			
			'MatchedTaxaHierarchyString': {
				'names': {'en': 'Taxonomic Tree'},
				'description': 'String representation of the taxonomic hierarchy of an object. Taxonomical names are sorted by their level and separated by ">".',
				'buckets': {
					'field_query': 'MatchedTaxaHierarchyString.facet'
				}
			},
			
			'MatchedSynonyms.Synonym': {
				'names': {'en': 'Synonym'},
				'description': 'Known synonyms of the accepted name of an object collected from curated taxonomies like GBIF backbone taxonomy or Catalog of Life',
				'buckets': {
					'field_query': 'MatchedSynonyms.Synonym.keyword'
				},
			},
			
			'TypeStatus': {
				'names': {'en': 'Type status'},
				'description': 'When the identified organism is used as reference material for the formal description of a species. There are different kinds of types like Holotype, Syntype, Paratype.',
				'buckets': {
					'field_query': 'TypeStatus.keyword'
				},
			},
			
			'MaterialCategory': {
				'names': {'en': 'Material category'},
				'description': 'The matierial type of the object in the collection, for example: microscopic slide, preserved specimen, bones, pelt. An object might only be observed and thus the material category would be "observed"',
				'buckets': {
					'field_query': 'MaterialCategory.keyword',
					'withholdflags': ['PartWithhold'],
				},
			},
			
			'AccessionDate': {
				'names': {'en': 'Accession date'},
				'description': 'The date when the specimen has been added to the collection',
				'buckets': {
					'field_query': 'AccessionDate',
					'type': 'date'
				}
			},
			
			'SpecimenCreatedWhen': {
				'names': {'en': 'Data aquisition date'},
				'description': 'The date when the data of the specimen have been added to the database.',
				'buckets': {
					'field_query': 'SpecimenCreatedWhen',
					'type': 'date'
				}
			},
			
			'LocalityVerbatim': {
				'names': {'en': 'Locality name'},
				'description': 'A common name of the locality where the specimen has been collected, like "Loch Ness", "Badger\'s drift".',
				'buckets': {
					'field_query': 'LocalityVerbatim.keyword',
					'withholdflags': ['EventWithhold', 'embargo_event_but_country', 'embargo_event_but_country_after_1992'],
				},
			},
			
			'LocalityDescription': {
				'names': {'en': 'Locality description'},
				'description': 'A more precise description of the locality where the specimen has been collected. For example the locality information given on a label of the collected object',
				'buckets': {
					'field_query': 'LocalityDescription.keyword',
					'withholdflags': ['EventWithhold', 'embargo_event_but_country', 'embargo_event_but_country_after_1992'],
				},
			},
			
			'HabitatDescription': {
				'names': {'en': 'Habitat'},
				'description': 'Information about the habitat from which the specimen has been collected.',
				'buckets': {
					'field_query': 'HabitatDescription.keyword',
					'withholdflags': ['EventWithhold', 'embargo_event_but_country', 'embargo_event_but_country_after_1992'],
				},
			},
			
			'CollectingMethod': {
				'names': {'en': 'Collecting method'},
				'description': 'Name and short description of the method by which the specimen has been collected.',
				'buckets': {
					'field_query': 'CollectingMethod.keyword',
					'withholdflags': ['EventWithhold', 'embargo_event_but_country', 'embargo_event_but_country_after_1992'],
				},
			},
			
			'CountryCache': {
				'names': {'en': 'Country'},
				'description': 'The country of the specimen\'s collection site.',
				'buckets': {
					'field_query': 'CountryCache.keyword',
					'withholdflags': ['EventWithhold'],
				},
			},
			
			'CollectionDate': {
				'names': {'en': 'Collection date'},
				'description': 'The date when the specimen has been collected.',
				'buckets': {
					'field_query': 'CollectionDate',
					'type': 'date',
					'withholdflags': ['EventWithhold', 'embargo_event_but_country', 'embargo_event_but_country_after_1992', 'embargo_coll_date'],
				}
			},
			
			'WGS84_Coordinate': {
				# does not have buckets key, so it does not occur in aggregations, term filters and queries
				'names': {'en': 'Coordinate'},
			},
			
			'CollectionAgents.CollectorsName': {
				'names': {'en': 'Collector(s)'},
				'description': 'The name(s) of one or more collectors of the specimen',
				'buckets': {
					'field_query': 'CollectionAgents.CollectorsName.keyword',
					'withholdflags': ['CollectionAgents.CollectorsWithhold', 'CollectionAgents.embargo_collector', 'CollectionAgents.embargo_anonymize_collector'],
					'path': 'CollectionAgents',
				},
			},
			
			# IUWithhold is ignored here as it is used for withholding the complete IdentificationUnitPart when it is set
			'LifeStage': {
				'names': {'en': 'Life stage'},
				'description': 'The life stage of the organism in the specimen part, e.g. "juvenil", "adult", "larva".',
				'buckets': {
					'field_query': 'LifeStage.keyword',
				},
			},
			
			'Gender': {
				'names': {'en': 'Sex'},
				'description': 'The sex of the organism in the specimen part.',
				'buckets': {
					'field_query': 'Gender.keyword',
				},
			},
			
			'NumberOfUnits': {
				'names': {'en': 'Number of specimens'},
				'description': 'The number of individual identified objects in the collected specimen.',
				'buckets': {
					'field_query': 'NumberOfUnits',
				},
			},
			
			'NumberOfSpecimenImages': {
				# this field is in iuparts object, not in Images
				'names': {'en': 'Number of images'},
				'description': 'The number of images in the database depicting the object.',
				'buckets': {
					'field_query': 'NumberOfSpecimenImages',
					'type': 'number'
				},
			},
			
			'ImagesAvailable': {
				'names': {'en': 'Image(s)'},
				'description': 'Flag if there is a media file available for the object.',
				'buckets': {
					'field_query': 'ImagesAvailable',
					'withholdflags': ['ImagesWithhold']
				},
			},
			
			'MediaTypes.MediaType': {
				'names': {'en': 'Media'},
				'description': 'Types of media files associated with the object in the collection database.',
				'buckets': {
					'field_query': 'MediaTypes.MediaType',
					'withholdflags': ['MediaTypes.MediaTypeWithhold'],
					'path': 'MediaTypes'
				}
			},
			
			'CollectionName': {
				'names': {'en': 'Collection'},
				'description': 'Name of the collection where the object is stored',
				'buckets': {
					'field_query': 'CollectionName.keyword',
				},
			},
			
			'CollectionsTree': {
				'names': {'en': 'Collection(s)'},
				'description': 'Names and ids of the collections in the database.',
				'buckets': {
					'field_query': 'CollectionsTree.CollectionName',
					'path': 'CollectionsTree',
					'id_field_for_tree': 'CollectionsTree.CollectionID',
					'parent_id_field_for_tree': 'CollectionsTree.ParentCollectionID'
				}
			},
			
			'CollectionHierarchyString': {
				'names': {'en': 'Collections (hierarchical)'},
				'description': 'String representation of the collection hierarchy of an object. Collections are sorted by their organisational level and separated by ">"',
				'buckets': {
					'field_query': 'CollectionHierarchyString.facet'
				}
			},
			
			'Projects.Project': {
				'names': {'en': 'Project(s)'},
				'description': 'Projects in which the objects are used',
				'buckets': {
					'field_query': 'Projects.Project.keyword',
				},
			},
			
			'DatabaseAccronym': {
				'names': {'en': 'Database'},
				'description': 'The accronym of the collection database that holds the data on a specimen.',
				'buckets': {
					'field_query': 'DatabaseAccronym.keyword',
				},
			},
			
			'CollectionSpecimenID': {
				'names': {'en': 'CollectionSpecimenID'},
				'description': 'The ID of the specimen (= sample) in the collection database.',
				'buckets': {
					'field_query': 'CollectionSpecimenID'
				},
			},
			
			'IdentificationUnitID': {
				'names': {'en': 'IdentificationUnitID'},
				'description': 'The ID of an identified individual or object in the collection database.',
				'buckets': {
					'field_query': 'IdentificationUnitID'
				},
			},
			
			'SpecimenPartID': {
				'names': {'en': 'SpecimenPartID'},
				'description': 'The ID of a part of a specimen in the collection database',
				'buckets': {
					'field_query': 'SpecimenPartID'
				},
			},
			
			'Barcodes.Methods.region': {
				'names': {'en': 'Barcode Marker'},
				'description': 'The region or locus of a gene that has been used to generate a RNA- or DNA-barcode from. Typical regions are: "COI", "ITS", "LSU", "SSU"',
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
				'description': 'Taxon assigned to the object at the rank {0}'.format(rank_names[rank]['en']),
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
			
			mapping = dict(self.es_mappings)
			for key in field_keys:
				if key in mapping['properties']:
					mapping = mapping['properties'][key]
			
					if 'type' in mapping:
						if 'buckets' in self.fielddefinitions[field]:
							self.fielddefinitions[field]['buckets']['types'] = [mapping['type']]
							if 'fields' in mapping:
								for typename in mapping['fields']:
									self.fielddefinitions[field]['buckets']['types'].append(typename)
		return


