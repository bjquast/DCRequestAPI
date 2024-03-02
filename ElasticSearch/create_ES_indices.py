import argparse
import pudb

import threading
import queue

#from ElasticSearch.ES_Indexer import ES_Indexer

import logging, logging.config

logging.config.fileConfig('logging.conf')
logger = logging.getLogger('elastic_indexer')

from ElasticSearch.ES_Indexer import ES_Indexer

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


es_queue = queue.Queue()


def es_worker():
	es_indexer = ES_Indexer()
	while True:
		data_page = es_queue.get()
		
		if len(data_page.iuparts_dict) > 0:
			es_indexer.bulkIndex(data_page.iuparts_dict, data_page.page)
		if len(data_page.collections_dict) > 0:
			es_indexer.bulkUpdateDocs(data_page.collections_dict, 'Collections', data_page.page)
		if len(data_page.projects_dict) > 0:
			es_indexer.bulkUpdateDocs(data_page.projects_dict, 'Projects', data_page.page)
		if len(data_page.identifications_dict) > 0:
			es_indexer.bulkUpdateDocs(data_page.identifications_dict, 'Identifications', data_page.page)
		if len(data_page.collectors_dict) > 0:
			es_indexer.bulkUpdateDocs(data_page.collectors_dict, 'CollectionAgents', data_page.page)
		if len(data_page.images_dict) > 0:
		
			es_indexer.bulkUpdateDocs(data_page.images_dict, 'Images', data_page.page)
		if len(data_page.barcode_analyses_dict) > 0:
			es_indexer.bulkUpdateDocs(data_page.barcode_analyses_dict, 'Barcodes', data_page.page)
		if len(data_page.fogs_analyses_dict) > 0:
			es_indexer.bulkUpdateDocs(data_page.fogs_analyses_dict, 'FOGS', data_page.page)
		if len(data_page.mam_analyses_dict) > 0:
			es_indexer.bulkUpdateDocs(data_page.mam_analyses_dict, 'MAM_Measurements', data_page.page)
		if len(data_page.matchedtaxa_dict) > 0:
			es_indexer.bulkUpdateDocs(data_page.matchedtaxa_dict, 'MatchedTaxa', data_page.page)
		
		es_queue.task_done()
		
	return


threading.Thread(target=es_worker, daemon=True).start()

class DataPage():
	""" a class that holds the data of each page requested from the database """ 
	def __init__(self):
		pass



class IUPartsIndexer():
	def __init__(self, es_indexer, dc_params, last_updated = None):
		self.es_indexer = es_indexer
		self.dc_params = dc_params
		self.last_updated = last_updated
		
		self.data_getter = DataGetter(self.dc_params, last_updated)
		self.data_getter.create_ids_temptable()
		self.data_getter.fill_ids_temptable()
		
		self.setDataGetters()
		self.submitDataPages()
		
		logger.info('No more remaining data pages')
		# add None to queue to signal all items have been send
		es_queue.join()


	def setDataGetters(self):
		
		self.iuparts = IdentificationUnitParts(self.data_getter)
		self.collections = Collections(self.data_getter)
		self.projects = Projects(self.data_getter)
		self.identifications = Identifications(self.data_getter)
		self.collectors = CollectionAgents(self.data_getter)
		self.images = CollectionSpecimenImages(self.data_getter)
		
		self.setBarcodeAMPFilterIDS()
		self.barcode_analyses = IdentificationUnitAnalyses(self.data_getter, self.barcode_amp_filter_ids, 'Barcodes')
		
		self.setFOGSAMPFilterIDS()
		self.fogs_analyses = IdentificationUnitAnalyses(self.data_getter, self.fogs_amp_filter_ids, 'FOGS')
		
		self.setMamAMPFilterIDS()
		self.mam_analyses = IdentificationUnitAnalyses(self.data_getter, self.mam_measurements_amp_filter_ids, 'MAM_Measurements')
		
		self.taxamatcher = TaxaMatcher()


	def submitDataPages(self):
		for i in range(1, self.data_getter.max_page + 1):
			
			data_page = DataPage()
			data_page.iuparts_dict = self.iuparts.get_data_page(i)
			data_page.collections_dict = self.collections.get_data_page(i)
			data_page.projects_dict = self.projects.get_data_page(i)
			data_page.identifications_dict = self.identifications.get_data_page(i)
			data_page.collectors_dict = self.collectors.get_data_page(i)
			data_page.images_dict = self.images.get_data_page(i)
			data_page.barcode_analyses_dict = self.barcode_analyses.get_data_page(i)
			data_page.fogs_analyses_dict = self.fogs_analyses.get_data_page(i)
			data_page.mam_analyses_dict = self.mam_analyses.get_data_page(i)
			data_page.matchedtaxa_dict = self.getMatchedTaxa(data_page.iuparts_dict, i)
			
			data_page.page = i
			
			es_queue.put(data_page)
		
		return


	def setBarcodeAMPFilterIDS(self):
		self.barcode_amp_filter_ids = {
		'161': {
				'12': ['62', '86', '87'],
				'16': ['73', '63', '64', '65', '66', '71', '72', '74', '75', '84', '91', '92']
			}
		}


	def setFOGSAMPFilterIDS(self):
		self.fogs_amp_filter_ids = {
		'327': {
				'23': ['140', '141', '150', '164', '165', '166', '167'],
				'25': ['144', '145', '146', '148']
			}
		}


	def setMamAMPFilterIDS(self):
		self.mam_measurements_amp_filter_ids = {
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


	def getMatchedTaxa(self, iuparts_dict, i):
		self.taxamatcher.createSpecimenTempTable()
		valuelists = []
		for idshash in iuparts_dict:
			valuelists.append([
				iuparts_dict[idshash]['_id'],
				iuparts_dict[idshash]['LastIdentificationCache'],
				iuparts_dict[idshash]['FamilyCache'],
				iuparts_dict[idshash]['OrderCache'],
				iuparts_dict[idshash]['TaxonomicGroup'],
				iuparts_dict[idshash]['TaxonNameURI'],
				iuparts_dict[idshash]['TaxonNameURI_sha'],
				iuparts_dict[idshash]['PartAccessionNumber'],
			])
		self.taxamatcher.fillSpecimenTempTable(valuelists)
		self.taxamatcher.matchTaxa()
		
		matchedtaxa_dict = self.taxamatcher.getMatchedTaxaDict()
		return matchedtaxa_dict



if __name__ == "__main__":
	#pudb.set_trace()
	
	es_indexer = ES_Indexer()
	es_indexer.deleteIndex()
	es_indexer.createIndex()
	
	dc_databases = DC_Connections()
	dc_databases.read_connectionparams()
	
	for dc_params in dc_databases.databases:
		iuparts_indexer = IUPartsIndexer(es_indexer, dc_params)
	
	logger.info('indexing completed')
	exit(0)



