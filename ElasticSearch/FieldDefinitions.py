import pudb

from ElasticSearch.ES_Mappings import MappingsDict


# TODO: read the fields that must be withholded from withholdfilters and add the according fields for withholdflags
# for each item in self.fielddefinitions 

class FieldDefinitions():
	def __init__(self):
		self.setFieldNames()
		self.setFieldDefinitions()
		self.appendTaxonRankDefinitions()
		
		self.es_mappings = MappingsDict['iuparts']
		self.setFieldTypes()


	def setFieldNames(self):
		self.bucketfields = [
			'DatabaseAccronym',
			#'CollectionsTree.CollectionName',
			#'CollectionName',
			'CollectionsTree',
			'Projects.Project',
			'LastIdentificationCache',
			'VernacularTerms',
			'MatchedSynonyms.Synonym',
			'MatchedTaxaTree',
			'MatchedTaxaTree.Phylum',
			'MatchedTaxaTree.Subphylum',
			'MatchedTaxaTree.Class',
			'MatchedTaxaTree.Subclass',
			'MatchedTaxaTree.Order',
			'MatchedTaxaTree.Suborder',
			'MatchedTaxaTree.Family',
			'MatchedTaxaTree.Subfamily',
			'MatchedTaxaTree.Genus',
			#'MatchedTaxaTree.Subgenus',
			'TypeStatus',
			'CountryCache',
			'CollectingMethod',
			'CollectionAgents.CollectorsName',
			'LocalityVerbatim',
			'LocalityDescription',
			'HabitatDescription',
			'MaterialCategory',
			'LifeStage',
			'Gender',
			'NumberOfUnits',
			'Barcodes.Methods.region',
			'ImageAvailable' # not working with prefix query
		]
		
		self.fieldnames = [
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
			'CollectionAgents.CollectorsName',
			'LifeStage',
			'Gender',
			'NumberOfUnits',
			# NumberOfSpecimenImages does not work. because it is a numeric type it can not be set to case_insensitiv in TermFilterQuery. Think about RangeQuery implementation 
			# 'NumberOfSpecimenImages',
			'CollectionName',
			'Projects.Project',
			'CollectionSpecimenID',
			'IdentificationUnitID',
			'SpecimenPartID',
			'Barcodes.Methods.region',
			'DatabaseAccronym',
		]
		
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
		
		self.tree_query_fields = [
			'MatchedTaxaTree',
			'CollectionsTree'
		]
		
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
		
		self.default_filter_sections = [
			'DatabaseAccronym',
			#'CollectionsTree.CollectionName',
			#'CollectionName',
			'CollectionsTree',
			'Projects.Project',
			'LastIdentificationCache',
			'VernacularTerms',
			'MatchedSynonyms.Synonym',
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
			#'TypeStatus',
			'CountryCache',
			#'CollectingMethod',
			#'CollectionAgents.CollectorsName',
			'LocalityVerbatim',
			'LocalityDescription',
			#'HabitatDescription',
			#'MaterialCategory',
			#'LifeStage',
			#'Gender',
			#'NumberOfUnits',
			#'Barcodes.Methods.region',
			'ImageAvailable'
		]
		return


	def setFieldDefinitions(self):
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
				'names': {'en': 'Taxon in GBIF'},
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
					'path': 'MatchedTaxaTree',
					'root_level': 0 # the level to start the tree or trees (e. g. Animalia, Plantae, Fungi) from
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
			
			'ImageAvailable': {
				# this field is in iuparts object, not in Images
				'names': {'en': 'Image(s) available'},
				'buckets': {
					'field_query': 'ImageAvailable',
					'type': 'boolean'
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
					'parent_id_field_for_tree': 'CollectionsTree.ParentCollectionID',
					'root_level': 0 # the level to start the tree or trees
				},
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
			
			# a field not defined in mapping, generated automatically
			#if field == 'Barcodes.Methods.region':
			#	pudb.set_trace()
			
			# set a defauld value
			if 'buckets' in self.fielddefinitions[field]:
				self.fielddefinitions[field]['buckets']['query_string_field'] = field
			
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
							
							'''
							if 'types' in self.fielddefinitions[field]['buckets']:
								if 'text' in self.fielddefinitions[field]['buckets']['types']:
									self.fielddefinitions[field]['buckets']['query_string_field'] = '{0}.{1}'.format(field, 'text')
								elif 'keyword_lc' in self.fielddefinitions[field]['buckets']['types']:
									self.fielddefinitions[field]['buckets']['query_string_field'] = '{0}.{1}'.format(field, 'keyword_lc')
								elif 'keyword' in self.fielddefinitions[field]['buckets']['types']:
									self.fielddefinitions[field]['buckets']['query_string_field'] = '{0}.{1}'.format(field, 'keyword')
								else:
									self.fielddefinitions[field]['buckets']['query_string_field'] = field
							'''
		
		return


