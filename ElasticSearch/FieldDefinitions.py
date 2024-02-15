import pudb


fieldnames = [
	'PartAccessionNumber',
	#'StableIdentifierURL',
	'LastIdentificationCache',
	'VernacularTerms',
	'FamilyCache',
	'OrderCache',
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

fielddefinitions = {
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
			'field_query': 'VernacularTerms',
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
			'field_query': 'MatchedParentTaxa', 
		},
	},
	
	'TypeStatus': {
		'names': {'en': 'Type status'},
		'buckets': {
			'field_query': 'TypeStatus.keyword_lc'
		},
	},
	
	'MaterialCategory': {
		'names': {'en': 'Specimen type'},
		'buckets': {
			'field_query': 'MaterialCategory',
			'withholdflag': 'PartWithhold',
		},
	},
	
	'LocalityVerbatim': {
		'names': {'en': 'Sampling locality'},
		'buckets': {
			'field_query': 'LocalityVerbatim.keyword',
			'withholdflag': 'EventWithhold',
		},
	},
	
	'LocalityDescription': {
		'names': {'en': 'Locality description'},
		'buckets': {
			'field_query': 'LocalityDescription.keyword',
			'withholdflag': 'EventWithhold',
		},
	},
	
	'HabitatDescription': {
		'names': {'en': 'Habitat'},
		'buckets': {
			'field_query': 'HabitatDescription.keyword',
			'withholdflag': 'EventWithhold',
		},
	},
	
	'CollectingMethod': {
		'names': {'en': 'Collecting method'},
		'buckets': {
			'field_query': 'CollectingMethod.keyword',
			'withholdflag': 'EventWithhold',
		},
	},
	
	'CountryCache': {
		'names': {'en': 'Country'},
		'buckets': {
			'field_query': 'CountryCache.keyword',
			'withholdflag': 'EventWithhold',
		},
	},
	
	'WGS84_Coordinate': {
		'names': {'en': 'Coordinate'},
	},
	
	'CollectionAgents.CollectorsName': {
		'names': {'en': 'Collector(s)'},
		'buckets': {
			'field_query': 'CollectionAgents.CollectorsName.keyword',
			'withholdflag': 'CollectionAgents.CollectorsWithhold',
			'path': 'CollectionAgents',
		},
	},
	
	# IUWithhold is ignored here as it is used for withholding the complete IdentificationUnitPart when it is set
	'LifeStage': {
		'names': {'en': 'Life stage'},
		'buckets': {
			'field_query': 'LifeStage',
		},
	},
	
	'Gender': {
		'names': {'en': 'Sex'},
		'buckets': {
			'field_query': 'Gender',
		},
	},
	
	'NumberOfUnits': {
		'names': {'en': 'Number of specimens'},
		'buckets': {
			'field_query': 'NumberOfUnits',
		},
	},
	
	'NumberOfSpecimenImages': {
		'names': {'en': 'Number of images'},
		'buckets': {
			'field_query': 'NumberOfSpecimenImages',
			'type': 'number'
		},
	},
	
	'CollectionName': {
		'names': {'en': 'Collection'},
		'buckets': {
			'field_query': 'CollectionName',
		},
	},
	
	'Projects.Project': {
		'names': {'en': 'Project(s)'},
		'buckets': {
			'field_query': 'Projects.Project',
		},
	},
	
	'DatabaseAccronym': {
		'names': {'en': 'Database'},
		'buckets': {
			'field_query': 'DatabaseAccronym',
		},
	},
	
	'CollectionSpecimenID': {
		'names': {'en': 'CollectionSpecimenID'},
	},
	
	'IdentificationUnitID': {
		'names': {'en': 'IdentificationUnitID'},
	},
	
	'SpecimenPartID': {
		'names': {'en': 'SpecimenPartID'},
	},
	
	'Barcodes.Methods.region': {
		'names': {'en': 'Barcode Marker'},
		'buckets': {
			'field_query': 'Barcodes.Methods.region.keyword',
		},
		
	}
}
