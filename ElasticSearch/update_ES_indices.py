import argparse
import pudb

#from ElasticSearch.ES_Indexer import ES_Indexer

import logging, logging.config

logging.config.fileConfig('logging.conf')
logger = logging.getLogger('elastic_indexer')

from ElasticSearch.ES_Indexer import ES_Indexer
from ElasticSearch.ES_Searcher import ES_Searcher

from DC2ElasticSearch.DCDataGetters.DC_Connections import DC_Connections
from DC2ElasticSearch.DCDataGetters.DataGetter import DataGetter


from DC2ElasticSearch.DCDataGetters.IdentificationUnitParts import IdentificationUnitParts
from DC2ElasticSearch.DCDataGetters.Collections import Collections
from DC2ElasticSearch.DCDataGetters.Projects import Projects
from DC2ElasticSearch.DCDataGetters.Identifications import Identifications
from DC2ElasticSearch.DCDataGetters.CollectionAgents import CollectionAgents
from DC2ElasticSearch.DCDataGetters.CollectionSpecimenImages import CollectionSpecimenImages
from DC2ElasticSearch.DCDataGetters.IdentificationUnitAnalyses import IdentificationUnitAnalyses

from DC2ElasticSearch.TaxaMatcher.TaxaMatcher import TaxaMatcher

from ElasticSearch.create_ES_indices import IUPartsIndexer


if __name__ == "__main__":
	
	es_indexer = ES_Indexer()
	es_searcher = ES_Searcher()
	
	dc_databases = DC_Connections()
	dc_databases.read_connectionparams()
	
	last_updated = es_searcher.getLastUpdated()
	#last_updated = '2024-02-20 17:44:46'
	
	if last_updated is None:
		raise ValueError('Last update time could not be determined, check if index has been filled before')
	
	for dc_params in dc_databases.databases:
		data_getter = DataGetter(dc_params, last_updated)
		
		data_getter.create_deleted_temptable()
		for i in range(1, data_getter.max_page_to_delete + 1):
			deleted_ids = data_getter.get_deleted_ids_page(i)
			if len(deleted_ids) > 0:
				es_indexer.bulkDelete(deleted_ids, i)
		
		iuparts_indexer = IUPartsIndexer(es_indexer, dc_params, last_updated)
		


