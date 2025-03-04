MappingsDict = dict()

#MappingsDict['settings'] = {'index': {'number_of_shards': 3, 'number_of_replicas': 1}}


# normalizer to generate lowercase index of keywords
# analyzer to keep accessionnumbers with - together
MappingsDict['settings'] = {
	'analysis': {
		'normalizer': {
			'use_lowercase': {
				'filter': ['lowercase']
			}
		},
		'analyzer': {
			'whitespace_lc': {
				'tokenizer': 'whitespace',
				'filter': ['lowercase']
			}
		}
	}
}


# do not use nested when there is no withholdflag in a sub-structure because it may duplicate the number of hits in aggregations when a term appears more than once in a substructure, e.g. identifications?

MappingsDict['iuparts'] = {
	'properties': {
		# the ID of this IdentificationUnit, CollectionSpecimen and SpecimenPart in Database (sha2 hash of the combined IDs)
		# should be the stored organism part
		'idshash':
			{'type': 'keyword'},
		'IdentificationUnitID':
			{
				'type': 'long',
				'fields': {
					'keyword': {'type': 'keyword', 'ignore_above': 256}
				}
			},
		'SpecimenPartID':
			{
				'type': 'long',
				'fields': {
					'keyword': {'type': 'keyword', 'ignore_above': 256}
				}
			},
		'CollectionSpecimenID':
			{
				'type': 'long',
				'fields': {
					'keyword': {'type': 'keyword', 'ignore_above': 256}
				}
			},
		'DatabaseURI':
			{'type': 'keyword'},
		'DatabaseAccronym': {
			'type': 'text', 'fields': {
				'keyword': {'type': 'keyword', 'ignore_above': 256},
				'keyword_lc': {'type': 'keyword', 'normalizer': 'use_lowercase', 'ignore_above': 256}
			}
		},
		'DatabaseID': 
			{'type': 'keyword'},
		'PartAccessionNumber':
			{
				'type': 'text',
				'analyzer': 'whitespace_lc',
				'fields': {
					'keyword': {'type': 'keyword', 'ignore_above': 256},
					'keyword_lc': {'type': 'keyword', 'normalizer': 'use_lowercase', 'ignore_above': 256}
				}
			},
		'SpecimenAccessionNumber':
			{
				'type': 'text', 
				'analyzer': 'whitespace_lc',
				'fields': {
					'keyword': {'type': 'keyword', 'ignore_above': 256},
					'keyword_lc': {'type': 'keyword', 'normalizer': 'use_lowercase', 'ignore_above': 256}
				}
			},
		'AccessionDate':
			{"type": "date",
			"format": "yyyy-MM-dd HH:mm:ss",
			'ignore_malformed': True},
		'DepositorsName': {
			'type': 'text', 'fields': {
				'keyword': {'type': 'keyword', 'ignore_above': 256},
				'keyword_lc': {'type': 'keyword', 'normalizer': 'use_lowercase', 'ignore_above': 256}
			}
		},
		
		'StableIdentifierURL': {'type': 'keyword'},
		'LastUpdated': {"type": "date",
			"format": "yyyy-MM-dd HH:mm:ss.SSS",
			'ignore_malformed': True
		},
		
		# database management
		'SpecimenWithholdingReason':
			{'type': 'text', 'fields': {'keyword': {'type': 'keyword', 'ignore_above': 256}}},
		'SpecimenWithhold': {'type': 'boolean'},
		'SpecimenVersion': {'type': 'integer'},
		'SpecimenCreatedWhen':{
			"type": "date",
			"format": "yyyy-MM-dd HH:mm:ss.SSS",
			'ignore_malformed': True
		},
		'SpecimenCreatedBy': {'type': 'keyword'},
		'SpecimenUpdatedWhen':{
			"type": "date",
			"format": "yyyy-MM-dd HH:mm:ss.SSS",
			'ignore_malformed': True
		},
		'SpecimenUpdatedBy': {'type': 'keyword'},
		
		# Embargos from DiversityProjects
		'embargo_anonymize_depositor': {'type': 'boolean'},
		'embargo_event_but_country': {'type': 'boolean'},
		'embargo_coordinates': {'type': 'boolean'},
		'embargo_event_but_country_after_1992': {'type': 'boolean'},
		'embargo_coll_date': {'type': 'boolean'},
		
		# Storage
		'PreparationMethod': {'type': 'text', 'fields': {
					'keyword': {'type': 'keyword', 'ignore_above': 256},
					'keyword_lc': {'type': 'keyword', 'normalizer': 'use_lowercase', 'ignore_above': 256}
				}
			},
		'PreparationDate': {
			"type": "date",
			"format": "yyyy-MM-dd HH:mm:ss",
			'ignore_malformed': True
		},
		'MaterialCategory': {'type': 'text', 'fields': {
					'keyword': {'type': 'keyword', 'ignore_above': 256},
					'keyword_lc': {'type': 'keyword', 'normalizer': 'use_lowercase', 'ignore_above': 256}
				}
			},
		'StorageLocation': {'type': 'text', 'fields': {
					'keyword': {'type': 'keyword', 'ignore_above': 256},
					'keyword_lc': {'type': 'keyword', 'normalizer': 'use_lowercase', 'ignore_above': 256}
				}
			},
		'StorageContainer': {'type': 'text', 'fields': {
					'keyword': {'type': 'keyword', 'ignore_above': 256},
					'keyword_lc': {'type': 'keyword', 'normalizer': 'use_lowercase', 'ignore_above': 256}
				}
			},
		'StockNumber': {'type': 'float'},
		'StockNumberUnit': {'type': 'keyword', 'fields': {'keyword_lc': {'type': 'keyword', 'normalizer': 'use_lowercase', 'ignore_above': 256}}},
		'StockVerbatim': {'type': 'text', 'fields': {
					'keyword': {'type': 'keyword', 'ignore_above': 256},
					'keyword_lc': {'type': 'keyword', 'normalizer': 'use_lowercase', 'ignore_above': 256}
				}
			},
		'PartWithholdingReason': {'type': 'keyword'},
		'PartWithhold': {'type': 'boolean'},
		
		
		# Event
		'CollectionEventID':
			{'type': 'long'},
		'CollectorsEventNumber':
			{'type': 'text', 'fields': {
					'keyword': {'type': 'keyword', 'ignore_above': 256},
					'keyword_lc': {'type': 'keyword', 'normalizer': 'use_lowercase', 'ignore_above': 256}
				}
			},
		'LocalityDescription':
			{'type': 'text', 'fields': {
					'keyword': {'type': 'keyword', 'ignore_above': 256},
					'keyword_lc': {'type': 'keyword', 'normalizer': 'use_lowercase', 'ignore_above': 256}
				}
			},
		'LocalityVerbatim':
			{'type': 'text', 'fields': {
					'keyword': {'type': 'keyword', 'ignore_above': 256},
					'keyword_lc': {'type': 'keyword', 'normalizer': 'use_lowercase', 'ignore_above': 256}
				}
			},
		'HabitatDescription':
			{'type': 'text', 'fields': {
					'keyword': {'type': 'keyword', 'ignore_above': 256},
					'keyword_lc': {'type': 'keyword', 'normalizer': 'use_lowercase', 'ignore_above': 256}
				}
			},
		'CollectingMethod':
			{'type': 'text', 'fields': {
					'keyword': {'type': 'keyword', 'ignore_above': 256},
					'keyword_lc': {'type': 'keyword', 'normalizer': 'use_lowercase', 'ignore_above': 256}
				}
			},
		'CountryCache':
			{'type': 'text', 'fields': {
					'keyword': {'type': 'keyword', 'ignore_above': 256},
					'keyword_lc': {'type': 'keyword', 'normalizer': 'use_lowercase', 'ignore_above': 256}
				}
			},
		'CollectionDate': {
			"type": "date",
			"format": "yyyy-MM-dd HH:mm:ss",
			'ignore_malformed': True
		},
		'WGS84_Coordinate':
			{'type': 'geo_point',
			"ignore_malformed": True},
		'WGS84_Accuracy m':
			{'type': 'float',
			"ignore_malformed": True},
		'Altitude mNN':
			{'type': 'float',
			"ignore_malformed": True},
		'Altitude_Accuracy m':
			{'type': 'float',
			"ignore_malformed": True},
		'NamedArea':
			{'type': 'text', 'fields': {
					'keyword': {'type': 'keyword', 'ignore_above': 256},
					'keyword_lc': {'type': 'keyword', 'normalizer': 'use_lowercase', 'ignore_above': 256}
				}
			},
		'NamedAreaURL':
			{'type': 'text', 'fields': {
					'keyword': {'type': 'keyword', 'ignore_above': 256},
					'keyword_lc': {'type': 'keyword', 'normalizer': 'use_lowercase', 'ignore_above': 256}
				}
			},
		'NamedAreaNotes':
			{'type': 'text', 'fields': {
					'keyword': {'type': 'keyword', 'ignore_above': 256},
					'keyword_lc': {'type': 'keyword', 'normalizer': 'use_lowercase', 'ignore_above': 256}
				}
			},
		'EventWithholdingReason':
			{'type': 'text', 'fields': {'keyword': {'type': 'keyword', 'ignore_above': 256}}},
		'EventWithhold': {'type': 'boolean'},
		'EventWithholdingReasonDate':
			{'type': 'text', 'fields': {'keyword': {'type': 'keyword', 'ignore_above': 256}}},
		'EventWithholdDate': {'type': 'boolean'},
		
		
		
		# ExternalDatasource
		'ExternalIdentifier':
			{'type': 'text', 'fields': {
					'keyword': {'type': 'keyword', 'ignore_above': 256},
					'keyword_lc': {'type': 'keyword', 'normalizer': 'use_lowercase', 'ignore_above': 256}
				}
			},
		'ExternalDatasourceName':
			{'type': 'text', 'fields': {
					'keyword': {'type': 'keyword', 'ignore_above': 256},
					'keyword_lc': {'type': 'keyword', 'normalizer': 'use_lowercase', 'ignore_above': 256}
				}
			},
		'ExternalDatasourceURI':
			{'type': 'text', 'fields': {
					'keyword': {'type': 'keyword', 'ignore_above': 256},
					'keyword_lc': {'type': 'keyword', 'normalizer': 'use_lowercase', 'ignore_above': 256}
				}
			},
		'ExternalDatasourceInstitution':
			{'type': 'text', 'fields': {
					'keyword': {'type': 'keyword', 'ignore_above': 256},
					'keyword_lc': {'type': 'keyword', 'normalizer': 'use_lowercase', 'ignore_above': 256}
				}
			},
		'ExternalAttribute_NameID':
			{'type': 'text', 'fields': {
					'keyword': {'type': 'keyword', 'ignore_above': 256},
					'keyword_lc': {'type': 'keyword', 'normalizer': 'use_lowercase', 'ignore_above': 256}
				}
			},
		
		
		# Identifications Object
		'Identifications': {
			'type': 'nested',
			'properties': {
				'IdentificationSequenceID': {'type': 'short'},
				'IdentificationDate': {
					"type": "date",
					"format": "yyyy-MM-dd HH:mm:ss",
					'ignore_malformed': True
				},
				'TaxonomicName': {'type': 'keyword', 'fields': {'keyword_lc': {'type': 'keyword', 'normalizer': 'use_lowercase', 'ignore_above': 256}}},
				'VernacularTerm': {'type': 'keyword', 'fields': {'keyword_lc': {'type': 'keyword', 'normalizer': 'use_lowercase', 'ignore_above': 256}}},
				'ParentTaxa': {'type': 'keyword', 'fields': {'keyword_lc': {'type': 'keyword', 'normalizer': 'use_lowercase', 'ignore_above': 256}}},
				'TaxonNameURI': {'type': 'keyword'},
				'TypeStatus': {'type': 'keyword', 'fields': {'keyword_lc': {'type': 'keyword', 'normalizer': 'use_lowercase', 'ignore_above': 256}}},
				'TypeNotes': {'type': 'text', 'fields': {
						'keyword': {'type': 'keyword', 'ignore_above': 256},
						'keyword_lc': {'type': 'keyword', 'normalizer': 'use_lowercase', 'ignore_above': 256}
					}
				},
				'ResponsibleName': {'type': 'keyword', 'fields': {'keyword_lc': {'type': 'keyword', 'normalizer': 'use_lowercase', 'ignore_above': 256}}},
				# Embargos from DiversityProjects
				'embargo_anonymize_determiner': {'type': 'boolean'}
			}
		},
		'LastIdentificationCache': {
			'type': 'text', 'fields': {
				'keyword': {'type': 'keyword', 'ignore_above': 256},
				'keyword_lc': {'type': 'keyword', 'normalizer': 'use_lowercase', 'ignore_above': 256}
			}
		},
		'FamilyCache': {'type': 'text', 'fields': {
				'keyword': {'type': 'keyword', 'ignore_above': 256},
				'keyword_lc': {'type': 'keyword', 'normalizer': 'use_lowercase', 'ignore_above': 256}
			}
		},
		'OrderCache': {'type': 'text', 'fields': {
				'keyword': {'type': 'keyword', 'ignore_above': 256},
				'keyword_lc': {'type': 'keyword', 'normalizer': 'use_lowercase', 'ignore_above': 256}
			}
		},
		'HierarchyCache': {'type': 'text'},
		'TaxonNameURI': {'type': 'keyword', 'ignore_above': 256},
		'TaxonNameURI_sha': {'type': 'keyword', 'ignore_above': 256},
		'OnlyObserved': {'type': 'boolean'},
		'LifeStage': {
			'type': 'text', 'fields': {
				'keyword': {'type': 'keyword', 'ignore_above': 256},
				'keyword_lc': {'type': 'keyword', 'normalizer': 'use_lowercase', 'ignore_above': 256}
			}
		},
		'Gender': {
			'type': 'text', 'fields': {
				'keyword': {'type': 'keyword', 'ignore_above': 256},
				'keyword_lc': {'type': 'keyword', 'normalizer': 'use_lowercase', 'ignore_above': 256}
			}
		},
		'NumberOfUnits': {'type': 'keyword', 'fields': {'keyword_lc': {'type': 'keyword', 'normalizer': 'use_lowercase', 'ignore_above': 256}}},
		'NumberOfUnitsModifier': {'type': 'keyword'},
		'UnitIdentifier': {'type': 'keyword'},
		'UnitDescription': {'type': 'text'},
		'IdentificationUnitNotes': {'type': 'text'},
		'IdentificationUnitCircumstances': {'type': 'text'},
		'IUWithholdingReason': {'type': 'text', 'fields': {'keyword': {'type': 'keyword', 'ignore_above': 256}}},
		'IUWithhold': {'type': 'boolean'},
		'IUDisplayOrder': {'type': 'integer'},
		
		# Collectors
		'CollectionAgents': {
			'type': 'nested',
			'properties': {
				'CollectorsName': {'type': 'text', 'fields': {
						'keyword': {'type': 'keyword', 'ignore_above': 256},
						'keyword_lc': {'type': 'keyword', 'normalizer': 'use_lowercase', 'ignore_above': 256}
					}
				},
				'CollectorsAgentURI': {'type': 'keyword'},
				'CollectorsOrder': {'type': 'integer'},
				'CollectorsSpecimenFieldNumber': {'type': 'keyword', 'fields': {'keyword_lc': {'type': 'keyword', 'normalizer': 'use_lowercase', 'ignore_above': 256}}},
				'CollectorsDataWithholding': {'type': 'text', 'fields': {'keyword': {'type': 'keyword', 'ignore_above': 256}}},
				'CollectorsWithhold': {'type': 'boolean'},
				# have to add the ProjectID here as it is the only way to filter nested objects by ProjectID for aggregations?!
				'ProjectID': {'type': 'integer'},
				'DB_ProjectID': {'type': 'keyword'},
				# Embargos from DiversityProjects
				'embargo_collector': {'type': 'boolean'},
				'embargo_anonymize_collector': {'type': 'boolean'}
			}
		},
		
		# Taxa matched in GBIF or TNT taxonomy
		'MatchedTaxon': {'type': 'keyword', 'fields': {'keyword_lc': {'type': 'keyword', 'normalizer': 'use_lowercase', 'ignore_above': 256}}},
		'MatchedTaxonAuthor': {'type': 'keyword', 'fields': {'keyword_lc': {'type': 'keyword', 'normalizer': 'use_lowercase', 'ignore_above': 256}}},
		'MatchedTaxonRank': {'type': 'keyword', 'fields': {'keyword_lc': {'type': 'keyword', 'normalizer': 'use_lowercase', 'ignore_above': 256}}},
		'MatchedTaxonURI': {'type': 'keyword'},
		'MatchedTaxonURL': {'type': 'keyword'},
		'MatchedParentTaxa': {
			'type': 'text', 'fields': {
				'keyword': {'type': 'keyword', 'ignore_above': 256},
				'keyword_lc': {'type': 'keyword', 'normalizer': 'use_lowercase', 'ignore_above': 256}
			}
		},
		'MatchedParentTaxaURIs': {'type': 'keyword'},
		'MatchedTaxaTree': {
			'type': 'nested',
			'properties': {
				'TaxonURI': {'type': 'keyword'},
				'TaxonURL': {'type': 'keyword'},
				'Taxon': {'type': 'keyword', 'fields': {'keyword_lc': {'type': 'keyword', 'normalizer': 'use_lowercase', 'ignore_above': 256}}},
				'Rank': {'type': 'keyword', 'fields': {'keyword_lc': {'type': 'keyword', 'normalizer': 'use_lowercase', 'ignore_above': 256}}},
				'TreeLevel': {'type': 'integer'},
				'ParentTaxonURI': {'type': 'keyword'},
			}
		},
		
		'MatchedSynonyms': {
			'properties': {
				'Synonym': {'type': 'text', 'fields': {
						'keyword': {'type': 'keyword', 'ignore_above': 256},
						'keyword_lc': {'type': 'keyword', 'normalizer': 'use_lowercase', 'ignore_above': 256}
					}
				},
				'SynonymTaxonURI': {'type': 'keyword'}
			}
		},
		
		'CollectionID': {'type': 'integer'},
		'CollectionName': {
			'type': 'text', 'fields': {
				'keyword': {'type': 'keyword', 'ignore_above': 256},
				'keyword_lc': {'type': 'keyword', 'normalizer': 'use_lowercase', 'ignore_above': 256}
			}
		},
		'CollectionAcronym': {'type': 'keyword', 'fields': {'keyword_lc': {'type': 'keyword', 'normalizer': 'use_lowercase', 'ignore_above': 256}}},
		'ParentCollections': {'type': 'keyword', 'fields': {'keyword_lc': {'type': 'keyword', 'normalizer': 'use_lowercase', 'ignore_above': 256}}},
		'CollectionsTree': {
			'type': 'nested',
			'properties': {
				'CollectionID': {'type': 'integer'},
				'CollectionName': {'type': 'keyword', 'fields': {'keyword_lc': {'type': 'keyword', 'normalizer': 'use_lowercase', 'ignore_above': 256}}},
				'TreeLevel': {'type': 'integer'},
				'ParentCollectionID': {'type': 'integer'}
			}
		},
		
		# keep it as is because it controls the access rights
		'Projects': {
			'properties': {
				'DB_ProjectID': {'type': 'keyword'}, # key combined of database key taken from config.in and ProjectID
				'ProjectID': {'type': 'integer'},
				'Project': {
					'type': 'text', 'fields': {
						'keyword': {'type': 'keyword', 'ignore_above': 256},
						'keyword_lc': {'type': 'keyword', 'normalizer': 'use_lowercase', 'ignore_above': 256}
					}
				},
				'ProjectURI': {'type': 'keyword'},
			}
		},
		
		# not available, because project structure is stored in DiversityProjects not in ProjectProxy
		#'ProjectsTree': {
		#	'type': 'nested',
		#	'properties': {
		#		'DB_ProjectID': {'type': 'keyword'},
		#		'Project': {'type': 'keyword', 'fields': {'keyword_lc': {'type': 'keyword', 'normalizer': 'use_lowercase', 'ignore_above': 256}}},
		#		'ProjectURI': {'type': 'keyword'},
		#		'TreeLevel': {'type': 'integer'},
		#	}
		#},
		
		'Images': {
			# must be nested because of the withhold
			'type': 'nested',
			'properties': {
				'URI': {'type': 'keyword'},
				'ResourceURI': {'type': 'keyword'},
				'ImageType': {'type': 'keyword', 'fields': {'keyword_lc': {'type': 'keyword', 'normalizer': 'use_lowercase', 'ignore_above': 256}}},
				'Title': {'type': 'text', 'fields': {
						'keyword': {'type': 'keyword', 'ignore_above': 256},
						'keyword_lc': {'type': 'keyword', 'normalizer': 'use_lowercase', 'ignore_above': 256}
					}
				},
				'Description': {'type': 'text', 'fields': {
						'keyword': {'type': 'keyword', 'ignore_above': 256},
						'keyword_lc': {'type': 'keyword', 'normalizer': 'use_lowercase', 'ignore_above': 256}
					}
				},
				'ImageCreator': {'type': 'keyword', 'fields': {'keyword_lc': {'type': 'keyword', 'normalizer': 'use_lowercase', 'ignore_above': 256}}},
				'CopyRightStatement': {'type': 'text', 'fields': {
						'keyword': {'type': 'keyword', 'ignore_above': 256},
						'keyword_lc': {'type': 'keyword', 'normalizer': 'use_lowercase', 'ignore_above': 256}
					}
				},
				'LicenseType': {'type': 'keyword', 'fields': {'keyword_lc': {'type': 'keyword', 'normalizer': 'use_lowercase', 'ignore_above': 256}}},
				'LicenseURI': {'type': 'keyword'},
				'LicenseHolder': {'type': 'keyword', 'fields': {'keyword_lc': {'type': 'keyword', 'normalizer': 'use_lowercase', 'ignore_above': 256}}},
				'LicenseHolderAgentURI': {'type': 'keyword'},
				'LicenseYear': {
					'type': 'date',
					"format": "yyyy-MM-dd||yyyy/MM/dd||yyyy||yy",
					'ignore_malformed': True
				},
				'ImageDisplayOrder': {'type': 'integer'},
				'ImageWithholdingReason': {'type': 'keyword'},
				'ImageWithhold': {'type': 'boolean'}
			}
		},
		
		'Barcodes': {
			'properties': {
				# from IdentificationUnitAnalysis
				'AnalysisNumber': {'type': 'keyword'},
				'AnalysisInstanceNotes': {'type': 'text', 'fields': {'keyword': {'type': 'keyword', 'ignore_above': 256}}},
				'ExternalAnalysisURI': {'type': 'keyword'},
				'ResponsibleName': {'type': 'keyword'},
				'AnalysisDate': {
					"type": "date",
					"format": "yyyy-MM-dd HH:mm:ss.SSS||yyyy-MM-dd HH:mm:ss||yyyy-MM-dd||dd.MM.yyyy||dd.MM.yy||d.MM.yyyy||d.M.yyyy||dd.M.yyyy||d.MM.yy||d.M.yy||dd.M.yy||yyyy",
					'ignore_malformed': True
				},
				'AnalysisResult': {'type': 'text', 'fields': {
						'keyword': {'type': 'keyword', 'ignore_above': 256},
						'keyword_lc': {'type': 'keyword', 'normalizer': 'use_lowercase', 'ignore_above': 256}
					}
				},
				
				# from Analysis
				'AnalysisID': {'type': 'long'},
				'AnalysisDisplay': {'type': 'keyword', 'fields': {'keyword_lc': {'type': 'keyword', 'normalizer': 'use_lowercase', 'ignore_above': 256}}},
				'AnalysisDescription': {'type': 'text', 'fields': {
						'keyword': {'type': 'keyword', 'ignore_above': 256},
						'keyword_lc': {'type': 'keyword', 'normalizer': 'use_lowercase', 'ignore_above': 256}
					}
				},
				'MeasurementUnit': {'type': 'keyword', 'fields': {'keyword_lc': {'type': 'keyword', 'normalizer': 'use_lowercase', 'ignore_above': 256}}},
				'AnalysisTypeNotes': {'type': 'keyword'},
				
				# from IdentificationUnitAnalysisMethod
				'Methods': {
					'properties': {
						'MethodMarker': {'type': 'keyword'},
						'MethodID': {'type': 'long'},
						'MethodDisplay': {'type': 'keyword', 'fields': {'keyword_lc': {'type': 'keyword', 'normalizer': 'use_lowercase', 'ignore_above': 256}}},
						'MethodDescription': {'type': 'text', 'fields': {
								'keyword': {'type': 'keyword', 'ignore_above': 256},
								'keyword_lc': {'type': 'keyword', 'normalizer': 'use_lowercase', 'ignore_above': 256}
							}
						},
						'MethodTypeNotes': {'type': 'text', 'fields': {'keyword': {'type': 'keyword', 'ignore_above': 256}}},
					}
				},
				
			}
		},
		
		'FOGS': {
			'properties': {
				# from IdentificationUnitAnalysis
				'AnalysisNumber': {'type': 'keyword'},
				'AnalysisInstanceNotes': {'type': 'text', 'fields': {'keyword': {'type': 'keyword', 'ignore_above': 256}}},
				'ExternalAnalysisURI': {'type': 'keyword'},
				'ResponsibleName': {'type': 'keyword'},
				'AnalysisDate': {
					"type": "date",
					"format": "yyyy-MM-dd HH:mm:ss.SSS||yyyy-MM-dd HH:mm:ss||yyyy-MM-dd||dd.MM.yyyy||dd.MM.yy||d.MM.yyyy||d.M.yyyy||dd.M.yyyy||d.MM.yy||d.M.yy||dd.M.yy||yyyy",
					'ignore_malformed': True
				},
				'AnalysisResult': {'type': 'text', 'fields': {
						'keyword': {'type': 'keyword', 'ignore_above': 256},
						'keyword_lc': {'type': 'keyword', 'normalizer': 'use_lowercase', 'ignore_above': 256}
					}
				},
				
				# from Analysis
				'AnalysisID': {'type': 'long'},
				'AnalysisDisplay': {'type': 'keyword', 'fields': {'keyword_lc': {'type': 'keyword', 'normalizer': 'use_lowercase', 'ignore_above': 256}}},
				'AnalysisDescription': {'type': 'text', 'fields': {
					'keyword': {'type': 'keyword', 'ignore_above': 256},
					'keyword_lc': {'type': 'keyword', 'normalizer': 'use_lowercase', 'ignore_above': 256}
				}},
				'MeasurementUnit': {'type': 'keyword'},
				'AnalysisTypeNotes': {'type': 'keyword'},
				
				# from IdentificationUnitAnalysisMethod
				'Methods': {
					'properties': {
						'MethodMarker': {'type': 'keyword'},
						'MethodID': {'type': 'long'},
						'MethodDisplay': {'type': 'keyword', 'fields': {'keyword_lc': {'type': 'keyword', 'normalizer': 'use_lowercase', 'ignore_above': 256}}},
						'MethodDescription': {'type': 'text', 'fields': {'keyword': {'type': 'keyword', 'ignore_above': 256}}},
						'MethodTypeNotes': {'type': 'text', 'fields': {'keyword': {'type': 'keyword', 'ignore_above': 256}}},
					}
				}
			}
		},
		
		'MAM_Measurements': {
			'properties': {
				# from IdentificationUnitAnalysis
				'AnalysisNumber': {'type': 'keyword'},
				'AnalysisInstanceNotes': {'type': 'text', 'fields': {'keyword': {'type': 'keyword', 'ignore_above': 256}}},
				'ExternalAnalysisURI': {'type': 'keyword'},
				'ResponsibleName': {'type': 'keyword'},
				'AnalysisDate': {
					"type": "date",
					"format": "yyyy-MM-dd HH:mm:ss.SSS||yyyy-MM-dd HH:mm:ss||yyyy-MM-dd||dd.MM.yyyy||dd.MM.yy||d.MM.yyyy||d.M.yyyy||dd.M.yyyy||d.MM.yy||d.M.yy||dd.M.yy||yyyy",
					'ignore_malformed': True
				},
				'AnalysisResult': {'type': 'text', 'fields': {
						'keyword': {'type': 'keyword', 'ignore_above': 256},
						'keyword_lc': {'type': 'keyword', 'normalizer': 'use_lowercase', 'ignore_above': 256}
					}
				},
				
				# from Analysis
				'AnalysisID': {'type': 'long'},
				'AnalysisDisplay': {'type': 'keyword', 'fields': {'keyword_lc': {'type': 'keyword', 'normalizer': 'use_lowercase', 'ignore_above': 256}}},
				'AnalysisDescription': {'type': 'text', 'fields': {
						'keyword': {'type': 'keyword', 'ignore_above': 256},
						'keyword_lc': {'type': 'keyword', 'normalizer': 'use_lowercase', 'ignore_above': 256}
					}
				},
				'MeasurementUnit': {'type': 'keyword'},
				'AnalysisTypeNotes': {'type': 'keyword'},
			}
		},
		# flat mappings of existing nested structures
		
		# Identifications
		'VernacularTerms': {
			'type': 'text', 'fields': {
				'keyword': {'type': 'keyword', 'ignore_above': 256},
				'keyword_lc': {'type': 'keyword', 'normalizer': 'use_lowercase', 'ignore_above': 256}
			}
		},
		'TypeStatus': {
			'type': 'text', 'fields': {
				'keyword': {'type': 'keyword', 'ignore_above': 256},
				'keyword_lc': {'type': 'keyword', 'normalizer': 'use_lowercase', 'ignore_above': 256}
			}
		},
		# Images
		'NumberOfSpecimenImages': {'type': 'integer', 'null_value': 0},
		
		'ImagesAvailable': {'type': 'keyword', 'ignore_above': 256},
		'ImagesWithhold': {'type': 'keyword', 'ignore_above': 256},
		
	}
}


'''
# better use the data in the iuparts index? otherwise 5m taxa have to be indexed where only about 100000 are used
# and the index have to be synced whenever the iuparts index is updated
MappingsDict['taxonomy'] = {
	'propperties': {
		'taxon_id': {'type': 'keyword'}, # is the same as _id in the index
		'parent_taxon_id': {'type': 'keyword'}, # important for tree generation in ui: find all childs in a tree that have that parent
		'Taxon': {'type': 'keyword', 'fields': {'keyword_lc': {'type': 'keyword', 'normalizer': 'use_lowercase', 'ignore_above': 256}}},
		'TaxonAuthor': {'type': 'keyword'},
		'TaxonRank': {'type': 'keyword'},
		'TaxonURI': {'type': 'keyword'},
		'TaxonURL': {'type': 'keyword'},
		'ParentTaxa': {'type': 'keyword', 'fields': {'keyword_lc': {'type': 'keyword', 'normalizer': 'use_lowercase', 'ignore_above': 256}}},
		'RankedParentTaxa': {
			'type': 'nested',
			'properties': {
				'TaxonURI': {'type': 'keyword'},
				'TaxonURL': {'type': 'keyword'},
				'Taxon': {'type': 'keyword'},
				'Rank': {'type': 'keyword'},
				'TreeLevel': {'type': 'integer'}
			}
		}
	}
}
'''
