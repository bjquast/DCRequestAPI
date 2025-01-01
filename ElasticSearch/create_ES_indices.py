import argparse
import pudb

from configparser import ConfigParser

import threading
import queue

import logging, logging.config

logging.config.fileConfig('logging.conf')
logger = logging.getLogger('elastic_indexer')

from ElasticSearch.ES_Indexer import ES_Indexer

from DC2ElasticSearch.DCDataGetters.DC_Connections import DC_Connections
from DC2ElasticSearch.DCDataGetters.DataGetter import DataGetter
from DC2ElasticSearch.DCDataGetters.IdentificationUnitParts import IdentificationUnitParts
from DC2ElasticSearch.DCDataGetters.Collections import Collections, CollectionRelationsTempTable
from DC2ElasticSearch.DCDataGetters.Projects import Projects
from DC2ElasticSearch.DCDataGetters.Identifications import Identifications
from DC2ElasticSearch.DCDataGetters.CollectionAgents import CollectionAgents
from DC2ElasticSearch.DCDataGetters.CollectionSpecimenImages import CollectionSpecimenImages
from DC2ElasticSearch.DCDataGetters.IdentificationUnitAnalyses import IdentificationUnitAnalyses

from DC2ElasticSearch.TaxaMatcher.TaxaMatcher import TaxaMatcher


class DataPage():
	""" a class that holds the data of each page requested from the database """ 
	def __init__(self, data_getter, skip_taxa_db = False):
		self.data_getter = data_getter
		self.skip_taxa_db = skip_taxa_db
		
		self.setDataGetters()


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
		
		if not self.skip_taxa_db:
			self.taxamatcher = TaxaMatcher()


	def setDataPage(self, page):
		self.page = page
		self.data_getter.create_iupart_ids_temptable()
		self.data_getter.fill_iupart_ids_temptable(self.page)
		
		self.iuparts_dict = self.iuparts.get_data_page()
		self.collections_dict = self.collections.get_data_page()
		self.projects_dict = self.projects.get_data_page()
		self.identifications_dict = self.identifications.get_data_page()
		# the common names set in Identifications table, here accessed separately so that they can be updated later with 
		# common names from the matched taxa
		self.vernaculars_dict = self.identifications.vernaculars_dict
		self.collectors_dict = self.collectors.get_data_page()
		self.images_dict = self.images.get_data_page()
		self.barcode_analyses_dict = self.barcode_analyses.get_data_page()
		self.fogs_analyses_dict = self.fogs_analyses.get_data_page()
		self.mam_analyses_dict = self.mam_analyses.get_data_page()
		
		if not self.skip_taxa_db:
			logger.info('Match taxa of page {0}'.format(self.page))
			self.setMatchedTaxa(self.iuparts_dict)
		else:
			self.matchedtaxa_dict = {}
			self.synonyms_dict = {}
		return


	def setMatchedTaxa(self, iuparts_dict):
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
		
		self.matchedtaxa_dict = self.taxamatcher.getMatchedTaxaDict()
		self.matchedsynonyms_dict = self.taxamatcher.getMatchedSynonymsDict()
		self.vernaculars_dict = self.taxamatcher.appendMatchedVernaculars(self.vernaculars_dict)
		
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


class IUPartsIndexer():
	def __init__(self, es_indexer, dc_params, last_updated = None, skip_taxa_db = False, multi_threaded_getter = False):
		self.es_indexer = es_indexer
		self.dc_params = dc_params
		self.last_updated = last_updated
		self.skip_taxa_db = skip_taxa_db
		self.multi_threaded_getter = multi_threaded_getter
		
		if self.multi_threaded_getter is True:
			self.runSubmissionThreads()
			
		else:
			self.submitDataPages()
		
		logger.info('No more remaining data pages')
		


	def es_submission(self, data_page):
		if len(data_page.iuparts_dict) > 0:
			self.es_indexer.bulkIndex(data_page.iuparts_dict, data_page.page)
		if len(data_page.collections_dict) > 0:
			self.es_indexer.bulkUpdateDocs(data_page.collections_dict, 'Collections', data_page.page)
		if len(data_page.projects_dict) > 0:
			self.es_indexer.bulkUpdateDocs(data_page.projects_dict, 'Projects', data_page.page)
		if len(data_page.identifications_dict) > 0:
			self.es_indexer.bulkUpdateDocs(data_page.identifications_dict, 'Identifications', data_page.page)
		if len(data_page.collectors_dict) > 0:
			self.es_indexer.bulkUpdateDocs(data_page.collectors_dict, 'CollectionAgents', data_page.page)
		if len(data_page.images_dict) > 0:
		
			self.es_indexer.bulkUpdateDocs(data_page.images_dict, 'Images', data_page.page)
		if len(data_page.barcode_analyses_dict) > 0:
			self.es_indexer.bulkUpdateDocs(data_page.barcode_analyses_dict, 'Barcodes', data_page.page)
		if len(data_page.fogs_analyses_dict) > 0:
			self.es_indexer.bulkUpdateDocs(data_page.fogs_analyses_dict, 'FOGS', data_page.page)
		if len(data_page.mam_analyses_dict) > 0:
			self.es_indexer.bulkUpdateDocs(data_page.mam_analyses_dict, 'MAM_Measurements', data_page.page)
		if len(data_page.matchedtaxa_dict) > 0:
			self.es_indexer.bulkUpdateDocs(data_page.matchedtaxa_dict, 'MatchedTaxa', data_page.page)
		if len(data_page.matchedsynonyms_dict) > 0:
			self.es_indexer.bulkUpdateDocs(data_page.matchedsynonyms_dict, 'MatchedSynonyms', data_page.page)
		
		if len(data_page.vernaculars_dict) > 0:
			self.es_indexer.bulkUpdateDocs(data_page.vernaculars_dict, 'VernacularTerms', data_page.page)
		
		return


	def es_worker(self, es_queue):
		while True:
			data_page = es_queue.get()
			self.es_submission(data_page)
			del data_page
			es_queue.task_done()
			
		return


	def submitDataPages(self):
		es_queue = queue.Queue()
		threading.Thread(target=self.es_worker, daemon=True, args = [es_queue]).start()
		
		#pudb.set_trace()
		data_getter = DataGetter(self.dc_params, self.last_updated)
		data_getter.create_cs_ids_temptable()
		data_getter.fill_cs_ids_temptable(self.last_updated)
		
		# create the CollectionRelationsTempTable that is used to add hierarchy levels to the collections
		CollectionRelationsTempTable(data_getter)
		
		for i in range(1, data_getter.max_page + 1):
			logger.info('################# getting data from page number {0}'.format(i))
			data_page = DataPage(data_getter, skip_taxa_db = self.skip_taxa_db)
			data_page.setDataPage(i)
			es_queue.put(data_page)
		
		es_queue.join()
		
		return


	def runSubmissionThreads(self, thread_num = 4):
		self.lock = threading.Lock()
		self.exc_info = None
		self.exc_log_info = None
		threadpool = []
		
		for i in range(int(thread_num)):
			skip_taxa_db = bool(self.skip_taxa_db)
			threadpool.append(threading.Thread(target = self.threadedPageSubmission, args = [i, skip_taxa_db]))
		
		for thread in threadpool:
			# set thread as daemon to guarantee that it is terminated when the program exits i. e. to prevent zombies
			thread.daemon = True
			thread.start()
		
		for thread in threadpool:
			thread.join()
			if self.exc_info:
				logger.info(self.exc_log_info)
				raise self.exc_info[1].with_traceback(self.exc_info[2])
				
		
		return


	def threadedPageSubmission(self, thread_num, skip_taxa_db):
		self.page_num = 1
		
		es_queue = queue.Queue()
		threading.Thread(target=self.es_worker, daemon=True, args = [es_queue]).start()
		
		data_getter = DataGetter(self.dc_params, self.last_updated)
		data_getter.create_cs_ids_temptable()
		data_getter.fill_cs_ids_temptable(self.last_updated)
		
		# create the CollectionRelationsTempTable that is used to add hierarchy levels to the collections
		CollectionRelationsTempTable(data_getter)
		
		while True:
			self.lock.acquire()
			if self.page_num <= data_getter.max_page:
				current_page = self.page_num
				self.page_num = self.page_num +1
				# log here to prevent concurrent writing into the log file 
				logger.info('################# thread number {0}'.format(thread_num))
				logger.info('################# page number {0}'.format(current_page))
				self.lock.release()
			else:
				self.lock.release()
				break
			
			try:
				
				data_page = DataPage(data_getter, skip_taxa_db = skip_taxa_db)
				data_page.setDataPage(current_page)
				
				#self.es_submission(data_page)
				es_queue.put(data_page)
			except Exception as e:
				self.lock.acquire()
				import sys
				self.exc_info = sys.exc_info()
				self.page_num = data_getter.max_page +1
				self.exc_log_info = '######### Exception occured in thread number {0}, page {1}'.format(thread_num, current_page)
				
				logger.info('######### Exception occured in thread number {0}, page {1}'.format(thread_num, current_page))
				self.lock.release()
				break
		
		es_queue.join()
		
		return


if __name__ == "__main__":
	#pudb.set_trace()
	
	config = ConfigParser(allow_no_value=True)
	config.read('./config.ini')
	skip_taxa_db = config.getboolean('taxamergerdb', 'skip_taxa_db', fallback = False)
	multi_threaded_getter = config.getboolean('default', 'multi_threaded_getter', fallback = False)
	
	logger.info('indexing started')
	
	es_indexer = ES_Indexer()
	es_indexer.deleteIndex()
	es_indexer.createIndex()
	
	dc_databases = DC_Connections()
	dc_databases.read_connectionparams()
	
	for dc_params in dc_databases.databases:
		iuparts_indexer = IUPartsIndexer(es_indexer, dc_params, last_updated = None, skip_taxa_db = skip_taxa_db, multi_threaded_getter = multi_threaded_getter)
	
	logger.info('indexing completed')
	exit(0)



