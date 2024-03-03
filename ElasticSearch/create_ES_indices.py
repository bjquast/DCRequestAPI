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


from DC2ElasticSearch.DCDataGetters.IdentificationUnitParts import IdentificationUnitPartsPage
from DC2ElasticSearch.DCDataGetters.Collections import CollectionsPage, CollectionRelationsTable
from DC2ElasticSearch.DCDataGetters.Projects import ProjectsPage
from DC2ElasticSearch.DCDataGetters.Identifications import IdentificationsPage
from DC2ElasticSearch.DCDataGetters.CollectionAgents import CollectionAgentsPage
from DC2ElasticSearch.DCDataGetters.CollectionSpecimenImages import CollectionSpecimenImagesPage
from DC2ElasticSearch.DCDataGetters.IdentificationUnitAnalyses import IdentificationUnitAnalysesPage, IUAnalysesAMPFilterTable

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
	def __init__(self, data_getter, page):
		self.data_getter = data_getter
		self.page = page
		
		self.iuparts_dict = IdentificationUnitPartsPage(self.data_getter, self.page).get_data_page()
		self.collections_dict = CollectionsPage(self.data_getter, self.page).get_data_page()
		self.projects_dict = ProjectsPage(self.data_getter, self.page).get_data_page()
		self.identifications_dict = IdentificationsPage(self.data_getter, self.page).get_data_page()
		self.collectors_dict = CollectionAgentsPage(self.data_getter, self.page).get_data_page()
		self.images_dict = CollectionSpecimenImagesPage(self.data_getter, self.page).get_data_page()
		self.barcode_analyses_dict = IdentificationUnitAnalysesPage(self.data_getter, 'Barcodes', self.page).get_data_page()
		self.fogs_analyses_dict = IdentificationUnitAnalysesPage(self.data_getter, 'FOGS', self.page).get_data_page()
		self.mam_analyses_dict = IdentificationUnitAnalysesPage(self.data_getter, 'MAM_Measurements', self.page).get_data_page()
		
		self.taxamatcher = TaxaMatcher()
		self.matchedtaxa_dict = self.getMatchedTaxa(self.iuparts_dict)
		


	def getMatchedTaxa(self, iuparts_dict):
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



class IUPartsIndexer():
	def __init__(self, es_indexer, dc_params, last_updated = None):
		self.es_indexer = es_indexer
		self.dc_params = dc_params
		self.last_updated = last_updated
		
		self.data_getter = DataGetter(self.dc_params, last_updated)
		self.data_getter.create_ids_temptable()
		self.data_getter.fill_ids_temptable()
		
		self.prepareGlobalTempTables()
		
		self.threaded_iu_getters = ThreadedIUPartGetters(self.data_getter, self.data_getter.max_page)
		self.threaded_iu_getters.runGetterThreads()
		
		logger.info('No more remaining data pages')
		# add None to queue to signal all items have been send
		es_queue.join()


	def prepareGlobalTempTables(self):
		self.setBarcodeAMPFilterIDS()
		barcode_amp_temptable = IUAnalysesAMPFilterTable(self.data_getter, self.barcode_amp_filter_ids, 'Barcodes')
		
		self.setFOGSAMPFilterIDS()
		fogs_amp_temptable = IUAnalysesAMPFilterTable(self.data_getter, self.fogs_amp_filter_ids, 'FOGS')
		
		self.setMamAMPFilterIDS()
		mam_amp_temptable = IUAnalysesAMPFilterTable(self.data_getter, self.mam_measurements_amp_filter_ids, 'MAM_Measurements')


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


class ThreadedIUPartGetters():
	def __init__(self, data_getter, max_page):
		self.data_getter = data_getter
		self.max_page = max_page
		self.page = 0
		
		self.lock = threading.Lock()
		pass


	def runGetterThreads(self, thread_num = 4):
		threadpool = []
		for num in range(int(thread_num)):
			threadpool.append(threading.Thread(target = self.getterThread, args = [num]))
		
		for thread in threadpool:
			# set thread as daemon to guarantee that it is terminated when the program exits i. e. to prevent zombies
			thread.setDaemon(True)
			thread.start()
		
		for thread in threadpool:
			thread.join()
		
		return


	def getterThread(self, num = 0):
		while True:
			self.lock.acquire()
			self.page = self.page + 1
			if self.page > self.max_page:
				self.lock.release()
				break
			else:
				self.lock.release()
			
			data_page = DataPage(self.data_getter, self.page)
			
			self.lock.acquire()
			es_queue.put(data_page)
			self.lock.release()
		return






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







