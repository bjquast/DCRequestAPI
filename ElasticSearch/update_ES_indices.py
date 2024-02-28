import argparse
import pudb

#from ElasticSearch.ES_Indexer import ES_Indexer

import logging, logging.config

logging.config.fileConfig('logging.conf')
logger = logging.getLogger('elastic_indexer')

from ElasticSearch.ES_Indexer import ES_Indexer
from ElasticSearch.ES_Searcher import ES_Searcher

from DC2ElasticSearch.DCDataGetters.DC_Connections import DC_Connections
from DC2ElasticSearch.DCDataGetters.DataGetterForUpdate import DataGetterForUpdate


from DC2ElasticSearch.DCDataGetters.IdentificationUnitParts import IdentificationUnitParts
from DC2ElasticSearch.DCDataGetters.Collections import Collections
from DC2ElasticSearch.DCDataGetters.Projects import Projects
from DC2ElasticSearch.DCDataGetters.Identifications import Identifications
from DC2ElasticSearch.DCDataGetters.CollectionAgents import CollectionAgents
from DC2ElasticSearch.DCDataGetters.CollectionSpecimenImages import CollectionSpecimenImages
from DC2ElasticSearch.DCDataGetters.IdentificationUnitAnalyses import IdentificationUnitAnalyses

from DC2ElasticSearch.TaxaMatcher.TaxaMatcher import TaxaMatcher


if __name__ == "__main__":
	#pudb.set_trace()
	
	es_indexer = ES_Indexer()
	es_searcher = ES_Searcher()
	
	dc_databases = DC_Connections()
	dc_databases.read_connectionparams()
	
	
	last_updated = es_searcher.getLastUpdated()
	last_updated = '2024-02-20 17:44:46'
	
	if last_updated is None:
		raise ValueError('Last update time could not be determined, check if index has been filled before')
	
	for dc_params in dc_databases.databases:
		update_getter = DataGetterForUpdate(dc_params, last_updated)
		
		update_getter.create_deleted_temptable()
		for i in range(1, update_getter.max_page_to_delete + 1):
			deleted_ids = update_getter.get_deleted_ids_page(i)
			if len(deleted_ids) > 0:
				es_indexer.bulkDelete(deleted_ids, i)
		
		#pudb.set_trace()
		
		update_getter.create_ids_temptable()
		update_getter.fill_ids_temptable()
	
		collections = None
		
		for i in range(1, update_getter.max_page + 1):
			iu_parts = IdentificationUnitParts(update_getter)
			iu_parts_dict = iu_parts.get_data_page(i)
			if len(iu_parts_dict) > 0:
				es_indexer.bulkIndex(iu_parts_dict, i)
			
			if collections is None:
				# initiate only once as it creates temp tables for Collection hierarchy
				collections = Collections(update_getter)
			collections_dict = collections.get_data_page(i)
			if len(collections_dict) > 0:
				es_indexer.bulkUpdateDocs(collections_dict, 'Collections', i)
			
			projects = Projects(update_getter)
			projects_dict = projects.get_data_page(i)
			if len(projects_dict) > 0:
				es_indexer.bulkUpdateDocs(projects_dict, 'Projects', i)
			
			identifications = Identifications(update_getter)
			identifications_dict = identifications.get_data_page(i)
			if len(identifications_dict) > 0:
				es_indexer.bulkUpdateDocs(identifications_dict, 'Identifications', i)
			
			collectors = CollectionAgents(update_getter)
			collectors_dict = collectors.get_data_page(i)
			if len(collectors_dict) > 0:
				es_indexer.bulkUpdateDocs(collectors_dict, 'CollectionAgents', i)
			
			images = CollectionSpecimenImages(update_getter)
			images_dict = images.get_data_page(i)
			if len(images_dict) > 0:
				es_indexer.bulkUpdateDocs(images_dict, 'Images', i)
			
			barcode_amp_filter_ids = {
			'161': {
					'12': ['62', '86', '87'],
					'16': ['73', '63', '64', '65', '66', '71', '72', '74', '75', '84', '91', '92']
				}
			}
			analyses = IdentificationUnitAnalyses(update_getter, barcode_amp_filter_ids, 'Barcodes')
			analyses_dict = analyses.get_data_page(i)
			if len(analyses_dict) > 0:
				es_indexer.bulkUpdateDocs(analyses_dict, 'Barcodes', i)
			
			fogs_amp_filter_ids = {
			'327': {
					'23': ['140', '141', '150', '164', '165', '166', '167'],
					'25': ['144', '145', '146', '148']
				}
			}
			analyses = IdentificationUnitAnalyses(update_getter, fogs_amp_filter_ids, 'FOGS')
			analyses_dict = analyses.get_data_page(i)
			if len(analyses_dict) > 0:
				es_indexer.bulkUpdateDocs(analyses_dict, 'FOGS', i)
			
			mam_measurements_amp_filter_ids = {
			'210': {},
			'220': {},
			'230': {},
			'240': {},
			'250': {},
			'260': {},
			'270': {},
			'280': {},
			'290': {},
			'293': {},
			'294': {},
			'295': {},
			'296': {},
			'299': {},
			'301': {},
			'302': {},
			'303': {}
			}
			analyses = IdentificationUnitAnalyses(update_getter, mam_measurements_amp_filter_ids, 'MAM_Measurements')
			analyses_dict = analyses.get_data_page(i)
			if len(analyses_dict) > 0:
				es_indexer.bulkUpdateDocs(analyses_dict, 'MAM_Measurements', i)
			
			taxamatcher = TaxaMatcher()
			taxamatcher.createSpecimenTempTable()
			valuelists = []
			for idshash in iu_parts_dict:
				valuelists.append([
					iu_parts_dict[idshash]['_id'],
					iu_parts_dict[idshash]['LastIdentificationCache'],
					iu_parts_dict[idshash]['FamilyCache'],
					iu_parts_dict[idshash]['OrderCache'],
					iu_parts_dict[idshash]['TaxonomicGroup'],
					iu_parts_dict[idshash]['TaxonNameURI'],
					iu_parts_dict[idshash]['TaxonNameURI_sha'],
					iu_parts_dict[idshash]['PartAccessionNumber'],
				])
			taxamatcher.fillSpecimenTempTable(valuelists)
			taxamatcher.matchTaxa()
			
			matched_taxa_dict = taxamatcher.getMatchedTaxaDict()
			if len(matched_taxa_dict) > 0:
				es_indexer.bulkUpdateDocs(matched_taxa_dict, 'MatchedTaxa', i)
			
			
			
		
		#pudb.set_trace()
	
