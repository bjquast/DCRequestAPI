import logging
import logging.config
logging.config.fileConfig('logging.conf')
logger = logging.getLogger('elastic_queries')

import json
import math

import pudb

from ElasticSearch.ES_Connector import ES_Connector
from ElasticSearch.ES_Mappings import MappingsDict

from ElasticSearch.WithholdFilters import WithholdFilters
from ElasticSearch.QueryConstructor.BucketAggregations import BucketAggregations
from ElasticSearch.QueryConstructor.TermFilterQueries import TermFilterQueries
from ElasticSearch.QueryConstructor.MatchQuery import MatchQuery

class ES_Searcher():
	def __init__(self, search_params = {}, user_id = None, users_project_ids = []):
		es_connector = ES_Connector()
		self.client = es_connector.client
		
		self.search_params = search_params
		self.user_id = user_id
		self.users_project_ids = users_project_ids
		
		self.index = 'iuparts'
		self.source_fields = []
		
		self.pagesize = 1000
		self.start = 0
		
		self.withholdfilters = WithholdFilters()
		self.withhold_fields = self.withholdfilters.getWithholdFields()
		


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
			if int(self.search_params['page']) < 1:
				self.search_params['page'] = 1
			self.start = self.pagesize * (int(self.search_params['page'])-1)
		else:
			self.start = 0
		return


	def setSorting(self):
		#pudb.set_trace()
		self.sort = [{"_score":{"order":"desc"}}, {"PartAccessionNumber.keyword_lc":{"order":"asc"}}]
		
		if 'sorting_col' in self.search_params and 'sorting_dir' not in self.search_params:
			self.search_params['sorting_dir'] = 'asc'
		if 'sorting_col' in self.search_params and 'sorting_dir' in self.search_params:
			if self.search_params['sorting_col'] is not None and self.search_params['sorting_dir'] is not None:
				self.sort = []
				# check which type is needed for sorting
				if self.search_params['sorting_col'] in self.mapping:
					if self.mapping[self.search_params['sorting_col']]['type'].lower() in ['long', 'integer']:
						self.sort.append({"{0}".format(self.search_params['sorting_col']): {'order': self.search_params['sorting_dir'].lower()}})
					elif self.mapping[self.search_params['sorting_col']]['type'].lower() in ['date']:
						self.sort.append({"{0}".format(self.search_params['sorting_col']): {'order': self.search_params['sorting_dir'].lower(), 'format': 'date_optional_time'}})
					elif self.mapping[self.search_params['sorting_col']]['type'].lower() in ['keyword'] and 'fields' in self.mapping[self.search_params['sorting_col']] and 'keyword_lc' in self.mapping[self.search_params['sorting_col']]['fields']:
						self.sort.append({"{0}.keyword_lc".format(self.search_params['sorting_col']): {'order': self.search_params['sorting_dir'].lower()}})
					elif self.mapping[self.search_params['sorting_col']]['type'].lower() in ['text'] and 'fields' in self.mapping[self.search_params['sorting_col']] and 'keyword_lc' in self.mapping[self.search_params['sorting_col']]['fields']:
						self.sort.append({"{0}.keyword_lc".format(self.search_params['sorting_col']): {'order': self.search_params['sorting_dir'].lower()}})
		
		return


	def setSourceFields(self, source_fields=[]):
		self.source_fields = source_fields
		
		if 'Projects.ProjectID' not in self.source_fields:
			source_fields.append('Projects.ProjectID')
		source_fields.extend(self.withhold_fields)


	def addUserLimitation(self):
		#if self.user_id is not None:
		#	projectmanager = ProjectManagement(self.uid)
		#	available_projects = [project[0] for project in projectmanager.fetch_affiliated_projects()]
		#else:
		
		# prepare the query as a subquery to the must-queries, so that it is guarantied that it is AND connected. 
		# this is in contrast to should filters where the addition of other should filters might disable the AND connection
		self.user_limitation = {"bool": {"should": [{"terms": {"Projects.ProjectID": self.users_project_ids}}, {"bool": {"must": [{"term": {"IUWithhold": "false"}}, {"term": {"SpecimenWithhold": "false"}}]}}], "minimum_should_match": 1}}
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
				filter_queries = TermFilterQueries(users_project_ids = self.users_project_ids).getTermFilterQueries(self.search_params['term_filters'])
				self.query['bool']["filter"].extend(filter_queries)
			
			if param == 'match_query':
				match_query = MatchQuery(users_project_ids = self.users_project_ids).getMatchQuery(self.search_params['match_query'])
				if match_query is not None:
					self.query['bool']['must'].append(match_query)
		
		
		self.addUserLimitation()
		self.deleteEmptySubqueries()


	def updateMaxResultWindow(self, max_result_window):
		#adjust max number of results that can be fetched
		logger.debug(self.client.indices.get_settings(index=self.index))
		
		body = {'index': {'max_result_window': max_result_window}}
		self.client.indices.put_settings(index=self.index, body=body)


	def paginatedSearch(self):
		
		self.updateMaxResultWindow(max_result_window=2000000)
		self.readIndexMapping()
		
		self.setPageSize()
		self.setStartRow()
		self.setSorting()
		
		#self.queryConstructor is set in the derived classes
		self.setQuery()
		
		buckets_query = BucketAggregations(users_project_ids = self.users_project_ids)
		aggs = buckets_query.getAggregationsQuery()
		
		logger.debug(self.sort)
		logger.debug(json.dumps(aggs))
		logger.debug(json.dumps(self.query))
		#logger.debug(json.dumps(self.sort))
		
		if len(self.source_fields) == 0:
			source_fields = True
		elif len(self.source_fields) > 0:
			source_fields = self.source_fields
		else:
			pass
		
		response = self.client.search(index=self.index, size=self.pagesize, sort=self.sort, query=self.query, from_=self.start, source=source_fields, track_total_hits=True, aggs=aggs)
		
		resultnum = response['hits']['total']['value']
		maxpage = self.getMaxPage(resultnum)
		
		if self.start > resultnum:
			self.search_params['page'] = maxpage
			self.setStartRow()
			response = self.client.search(index=self.index, size=self.pagesize, sort=self.sort, query=self.query, from_=self.start, source=source_fields, track_total_hits=True, aggs=aggs)
			
		self.raw_aggregations = response['aggregations']
		
		docs = [doc for doc in response['hits']['hits']]
		docs = self.withholdfilters.applyFiltersToSources(docs, self.users_project_ids)
		
		return docs, maxpage, resultnum


	def parseRawAggregations(self):
		self.aggregations = {}
		for colname in self.raw_aggregations:
			self.parseRawAggregation(self.raw_aggregations[colname], colname)
		return


	def parseRawAggregation(self, raw_aggregation, colname):
		if 'buckets' in raw_aggregation:
			if isinstance(raw_aggregation['buckets'], list) or isinstance(raw_aggregation['buckets'], tuple):
				if colname not in self.aggregations:
					self.aggregations[colname] = []
				for bucket in raw_aggregation['buckets']:
					self.aggregations[colname].append(bucket)
			elif isinstance(raw_aggregation['buckets'], dict) and 'buckets' in raw_aggregation['buckets']:
				self.parseRawAggregation(raw_aggregation['buckets'], colname)
		return


	def getParsedAggregations(self):
		self.parseRawAggregations()
		return self.aggregations



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
	es_search = ES_Searcher(search_params = search_params, user_id = 'bquast', users_project_ids = [634, 30000])
	es_search.paginatedSearch()
	facets = es_search.raw_aggregations
	
	
	



