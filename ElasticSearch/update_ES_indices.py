import pudb

from configparser import ConfigParser
from ElasticSearch.ES_Indexer import ES_Indexer
from ElasticSearch.ES_Searcher import ES_Searcher

from DC2ElasticSearch.DCDataGetters.DC_Connections import DC_Connections
from DC2ElasticSearch.DCDataGetters.DataGetter import DataGetter
from ElasticSearch.create_ES_indices import IUPartsIndexer

import logging, logging.config
logging.config.fileConfig('logging.conf')
logger = logging.getLogger('elastic_indexer')



class UpdateES_Index:
	def __init__(self):
		self.config = ConfigParser(allow_no_value=True)
		self.config.read('./config.ini')
		
		self.es_indexer = ES_Indexer()
		self.dc_databases = DC_Connections()
		self.dc_databases.read_connectionparams()
		
		self.es_searcher = ES_Searcher()
		self.last_updated = self.es_searcher.getLastUpdated()
		# for testing
		#self.last_updated = '2024-03-11 17:44:46'
		
		self.skip_taxa_db = self.config.getboolean('taxamergerdb', 'skip_taxa_db', fallback = False)
		self.multi_threaded_getter = config.getboolean('default', 'multi_threaded_getter', fallback = False)
		
		if self.last_updated is None:
			raise ValueError('Last update time could not be determined, check if index has been filled before')


	def update_from_database(self, dc_params:dict, table_name:str|None = None):
		#pudb.set_trace()
		data_getter = DataGetter(dc_params, self.last_updated)
		
		data_getter.create_deleted_temptable()
		for i in range(1, data_getter.max_page_to_delete + 1):
			deleted_ids = data_getter.get_deleted_ids_page(i)
			if len(deleted_ids) > 0:
				self.es_indexer.bulkDelete(deleted_ids, i)
		
		iuparts_indexer = IUPartsIndexer(self.es_indexer, dc_params, last_updated = self.last_updated, skip_taxa_db = self.skip_taxa_db, multi_threaded_getter = self.multi_threaded_getter)
		
		logger.info('update completed')


	def update_es_index(self):
		for dc_params in self.dc_databases.databases:
			self.update_from_database(dc_params)



if __name__ == "__main__":
	config = ConfigParser(allow_no_value=True)
	config.read('./config.ini')
	skip_taxa_db = config.getboolean('taxamergerdb', 'skip_taxa_db', fallback = False)
	multi_threaded_getter = config.getboolean('default', 'multi_threaded_getter', fallback = False)
	
	
	updater = UpdateES_Index()
	updater.update_es_index()
	
	
	



