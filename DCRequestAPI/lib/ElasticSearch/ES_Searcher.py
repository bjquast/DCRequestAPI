import logging
import logging.config
logging.config.fileConfig('logging.conf')
logger = logging.getLogger('elastic')

import json
import math

from DCRequestAPI.lib.ElasticSearch.ES_Connector import ES_Connector
from DCRequestAPI.lib.ElasticSearch.ES_Mappings import MappingsDict

from DCRequestAPI.lib.ElasticSearch.QueryConstructor.BucketAggregations import BucketAggregations
from DCRequestAPI.lib.ElasticSearch.QueryConstructor.TermFilterQueries import TermFilterQueries
from DCRequestAPI.lib.ElasticSearch.QueryConstructor.MatchQuery import MatchQuery

import pudb

class ES_Searcher():
	def __init__(self, search_params = {}, user_id = None, users_projects = []):
		es_connector = ES_Connector()
		self.client = es_connector.client
		
		self.search_params = search_params
		self.user_id = user_id
		self.users_projects = users_projects
		
		self.index = 'iuparts'
		
		self.pagesize = 1000
		self.start = 0
		
		# standard sorting
		self.sort = {'PartAccessionNumber.keyword': {'order': 'asc'}}
		
		self.sorting_cols = [
			'CollectionSpecimenID',
			'IdentificationUnitID',
			'SpecimenPartID',
			'PartAccessionNumber.keyword',
			'AccessionDate',
			'PreparationMethod.keyword',
			'MaterialCategory',
			'CollectorsEventNumber.keyword',
			'CountryCache.keyword',
			'CollectingMethod.keyword',
			'LastIdentificationCache',
			'FamilyCache',
			'Projects.Project',
			'Projects.ProjectID',
			'CollectionName',
			'NumberOfUnits',
		]
		


	def getMaxPage(self, hits):
		maxpage = math.ceil(hits/self.pagesize)
		return maxpage


	def readIndexMapping(self):
		try:
			self.mapping = MappingsDict[self.index]['properties']
		except:
			self.mapping = {}


	def setPageSize(self):
		if 'pagesize' in self.search_params:
			self.pagesize = int(self.search_params['pagesize'])
		else:
			pass
		return


	def setStartRow(self):
		if 'page' in self.search_params:
			self.start = self.pagesize * (int(self.search_params['page'])-1)
		else:
			self.start = 0
		return


	def setSorting(self):
		
		if self.search_params['sorting_col'] is not None and self.search_params['sorting_dir'] is not None:
			# check which type is needed for sorting
			if self.search_params['sorting_col'] in self.mapping:
				if self.mapping[self.search_params['sorting_col']]['type'].lower() in ['long', 'integer']:
					self.sort = {"{0}".format(self.search_params['sorting_col']): {'order': self.search_params['sorting_dir'].lower()}}
				elif self.mapping[self.search_params['sorting_col']]['type'].lower() in ['date']:
					self.sort = {"{0}".format(self.search_params['sorting_col']): {'order': self.search_params['sorting_dir'].lower(), 'format': 'date_optional_time'}}
				else:
					self.sort = {"{0}.keyword".format(self.search_params['sorting_col']): {'order': self.search_params['sorting_dir'].lower()}}
			else:
				pass
		return


	def addUserLimitation(self):
		#if self.user_id is not None:
		#	projectmanager = ProjectManagement(self.uid)
		#	available_projects = [project[0] for project in projectmanager.fetch_affiliated_projects()]
		#else:
		
		# prepare the query as a subquery to the must-queries, so that it is guarantied that it is AND connected. 
		# this is in contrast to should filters where the addition of other should filters might disable the AND connection
		self.user_limitation = {"bool": {"should": [{"terms": {"Projects.ProjectID": self.users_projects}}, {"bool": {"must": [{"term": {"IUWithhold": "false"}}, {"term": {"SpecimenWithhold": "false"}}]}}], "minimum_should_match": 1}}
		self.query["bool"]["must"].append(self.user_limitation)
		return


	def deleteEmptySubqueries(self):
		if len(self.query['bool']['must']) <= 0:
			del self.query['bool']['must']
		
		if len(self.query['bool']['should']) <= 0:
			del self.query['bool']['should']
		
		if len(self.query['bool']['filter']) <= 0:
			del self.query['bool']['filter']
		
		if len(self.query['bool']) <= 0:
			del self.query['bool']
		return


	def setQuery(self):
		self.query = {"bool": {"must": [], "should": [], "filter": []}}
		
		for param in self.search_params:
			
			if param == 'term_filters':
				filter_queries = TermFilterQueries(self.mapping).getTermFilterQueries(self.search_params['term_filters'])
				self.query['bool']["filter"].extend(filter_queries)
			
			if param == 'match_query':
				match_query = MatchQuery(users_projects = self.users_projects).getMatchQuery(self.search_params['match_query'])
				self.query['bool']['must'].append(match_query)
		
		
		self.addUserLimitation()
		self.deleteEmptySubqueries()


	def updateMaxResultWindow(self, max_result_window):
		#adjust max number of results that can be fetched
		logger.info(self.client.indices.get_settings(index=self.index))
		
		body = {'index': {'max_result_window': max_result_window}}
		self.client.indices.put_settings(index=self.index, body=body)


	def paginatedSearch(self, source_fields=[]):
		
		self.updateMaxResultWindow(max_result_window=2000000)
		self.readIndexMapping()
		
		self.setPageSize()
		self.setStartRow()
		
		if 'sorting_col' in self.search_params and 'sorting_dir' in self.search_params:
			self.setSorting()
		
		#self.queryConstructor is set in the derived classes
		self.setQuery()
		
		buckets_query = BucketAggregations(users_projects = self.users_projects)
		aggs = buckets_query.getAggregationsQuery()
		
		logger.info(json.dumps(aggs))
		logger.info(json.dumps(self.query))
		#logger.info(json.dumps(self.sort))
		
		if (isinstance(source_fields, list) or isinstance(source_fields, tuple)) and len(source_fields) == 0:
			source_fields = True
		else:
			pass
		
		response = self.client.search(index=self.index, size=self.pagesize, sort=self.sort, query=self.query, from_=self.start, source=source_fields, track_total_hits=True, aggs=aggs)
		self.raw_aggregations = response['aggregations']
		
		resultnum = hits=response['hits']['total']['value']
		maxpage = self.getMaxPage(hits=response['hits']['total']['value'])
		docs = [doc for doc in response['hits']['hits']]
		
		return docs, maxpage, resultnum






if __name__ == "__main__":
	# main program for testing
	
	#search_params = {}
	
	
	search_params = {
		'pagesize': 1000,
		'page': 1,
		'sorting_col': 'AccessionDate',
		'sorting_dir': 'DESC',
		'term_filters': {
			'Projects.Project': ['Section Mammalia ZFMK'],
			'CountryCache': ['Germany', ]
		},
		'match_query': 'Rulik',
	}
	
	
	pudb.set_trace()
	es_search = ES_Searcher(search_params = search_params, user_id = 'bquast', users_projects = [634, 30000])
	es_search.paginatedSearch()
	facets = es_search.raw_aggregations
	
	
	



