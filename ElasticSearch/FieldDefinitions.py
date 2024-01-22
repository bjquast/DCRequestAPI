import pudb


fieldnames = [
	'PartAccessionNumber',
	'LastIdentificationCache',
	'Identifications.VernacularTerm',
	'FamilyCache',
	'OrderCache',
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
	'CollectionName',
	'Projects.Project',
	'CollectionSpecimenID',
	'Barcodes.Methods.region',
	'DatabaseAccronym',
]

fielddefinitions = {
	'PartAccessionNumber': {
		'names': {'en': 'Accessionnumber', },
		'buckets': {
			'field_query': 'PartAccessionNumber.keyword', 
			'size': 10,
		},
		
	},
	
	'LastIdentificationCache': {
		'names': {'en': 'Taxon / Species'},
		'buckets': {
			'field_query': 'LastIdentificationCache.keyword', 
			'size': 10,
		},
	},
	
	'Identifications.VernacularTerm': {
		'names': {'en': 'Vernacular name'},
		'buckets': {
			'field_query': 'Identifications.VernacularTerm',
			'size': 10,
		},
	},
	
	'FamilyCache': {
		'names': {'en': 'Family'},
		'buckets': {
			'field_query': 'FamilyCache.keyword', 
			'size': 10,
		},
	},
	
	'OrderCache': {
		'names': {'en': 'Order'},
		'buckets': {
			'field_query': 'OrderCache.keyword', 
			'size': 10,
		},
	},
	
	'MaterialCategory': {
		'names': {'en': 'Specimen type'},
		'buckets': {
			'field_query': 'MaterialCategory',
			'size': 10,
			'withholdflag': 'PartWithhold',
		},
	},
	
	'LocalityVerbatim': {
		'names': {'en': 'Sampling locality'},
		'buckets': {
			'field_query': 'LocalityVerbatim.keyword',
			'size': 10,
			'withholdflag': 'EventWithhold',
		},
	},
	
	'LocalityDescription': {
		'names': {'en': 'Locality description'},
		'buckets': {
			'field_query': 'LocalityDescription.keyword',
			'size': 10,
			'withholdflag': 'EventWithhold',
		},
	},
	
	'HabitatDescription': {
		'names': {'en': 'Habitat'},
		'buckets': {
			'field_query': 'HabitatDescription.keyword',
			'size': 10,
			'withholdflag': 'EventWithhold',
		},
	},
	
	'CollectingMethod': {
		'names': {'en': 'Collecting method'},
		'buckets': {
			'field_query': 'CollectingMethod.keyword',
			'size': 10,
			'withholdflag': 'EventWithhold',
		},
	},
	
	'CountryCache': {
		'names': {'en': 'Country'},
		'buckets': {
			'field_query': 'CountryCache.keyword',
			'size': 10,
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
			'size': 10,
			'withholdflag': 'CollectionAgents.CollectorsWithhold',
			'path': 'CollectionAgents',
		},
	},
	
	# IUWithhold is ignored here as it is used for withholding the complete IdentificationUnitPart when it is set
	'LifeStage': {
		'names': {'en': 'Life stage'},
		'buckets': {
			'field_query': 'LifeStage',
			'size': 10,
		},
	},
	
	'Gender': {
		'names': {'en': 'Sex'},
		'buckets': {
			'field_query': 'Gender',
			'size': 10,
		},
	},
	
	'NumberOfUnits': {
		'names': {'en': 'Number of specimens'},
		'buckets': {
			'field_query': 'NumberOfUnits',
			'size': 10,
		},
	},
	
	'CollectionName': {
		'names': {'en': 'Collection'},
		'buckets': {
			'field_query': 'CollectionName',
			'size': 10,
		},
	},
	
	'Projects.Project': {
		'names': {'en': 'Project(s)'},
		'buckets': {
			'field_query': 'Projects.Project',
			'size': 10,
		},
	},
	
	'DatabaseAccronym': {
		'names': {'en': 'Database'},
		'buckets': {
			'field_query': 'DatabaseAccronym',
			'size': 10,
		},
	},
	
	'CollectionSpecimenID': {
		'names': {'en': 'CollectionSpecimenID'},
	},
	
	'Barcodes.Methods.region': {
		'names': {'en': 'Barcode Marker'},
		'buckets': {
			'field_query': 'Barcodes.Methods.region.keyword',
			'size': 10
		},
		
	}
}
