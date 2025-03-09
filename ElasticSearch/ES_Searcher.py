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
from ElasticSearch.QueryConstructor.HierarchyQueries import HierarchyQueries
from ElasticSearch.QueryConstructor.StackedQueries import StackedInnerQuery, StackedOuterQuery

class ES_Searcher():
	def __init__(self, search_params = {}, user_id = None, users_project_ids = [], restrict_to_users_projects = False):
		es_connector = ES_Connector()
		self.client = es_connector.client
		
		self.search_params = search_params
		self.user_id = user_id
		self.users_project_ids = users_project_ids
		self.restrict_to_users_projects = restrict_to_users_projects
		
		self.index = 'iuparts'
		self.source_fields = []
		self.bucket_fields = []
		self.hierarchy_fields = []
		self.hierarchy_pathes_dict = {}
		
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
		self.sort = [{"PartAccessionNumber.keyword_lc":{"order":"asc"}}]
		
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


	def setSourceFields(self, source_fields = []):
		# copy the source_fields, otherwise the change here changes the source_fields variable in the caller 
		self.source_fields = list(source_fields)
		
		# moved to paginated_search
		'''
		# add the fields that are needed for filtering the results in WithholdFilters.applyFiltersToSources()
		if 'Projects.DB_ProjectID' not in self.source_fields:
			self.source_fields.append('Projects.DB_ProjectID')
		self.source_fields.extend(self.withhold_fields)
		'''


	def setBucketFields(self, bucket_fields = []):
		self.bucket_fields = list(bucket_fields)
		return


	def setHierarchyFields(self, hierarchy_fields = []):
		self.hierarchy_fields = list(hierarchy_fields)
		return


	def setHierarchyPathesDict(self, hierarchy_pathes_dict = {}):
		self.hierarchy_pathes_dict = hierarchy_pathes_dict
		return


	def addUserLimitation(self):
		# prepare the query as a subquery to the must-queries, so that it is guarantied that it is AND connected. 
		# this is in contrast to should filters where the addition of other should filters might disable the AND connection
		if self.restrict_to_users_projects is False:
			# when open data without withhold should be shown
			self.user_limitation = {"bool": {"should": [{"terms": {"Projects.DB_ProjectID": self.users_project_ids}}, {"bool": {"must": [{"term": {"IUWithhold": "false"}}, {"term": {"SpecimenWithhold": "false"}}]}}], "minimum_should_match": 1}}
		else:
			# when only the data from the users projects should be shown
			self.user_limitation = {"terms": {"Projects.DB_ProjectID": self.users_project_ids}}
		
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
		#pudb.set_trace()
		if 'term_filters' in self.search_params:
			connector = 'AND'
			if 'term_filters_connector' in self.search_params:
				connector = self.search_params['term_filters_connector']
			
			filter_queries = TermFilterQueries(users_project_ids = self.users_project_ids, source_fields = self.bucket_fields, connector = connector).getTermFilterQueries(self.search_params['term_filters'])
			self.query['bool']["filter"].extend(filter_queries)
		
		#pudb.set_trace()
		outer_query = StackedOuterQuery()
		
		if 'stack_queries' in self.search_params:
			# set outer connector to AND for the first query, otherwise it might result in all documents matched when it starts with an OR query and it is the only query
			if len(self.search_params['stack_queries']) > 0:
				self.search_params['stack_queries'][0]['outer_connector'] = 'AND'
			for stack_query in self.search_params['stack_queries']:
				inner_query = StackedInnerQuery(stack_query, users_project_ids = self.users_project_ids)
				inner_string_query = inner_query.getInnerStackQuery()
				
				if inner_string_query is not None:
					if stack_query['outer_connector'] == 'AND':
						outer_query.addMustQuery(inner_string_query)
					else:
						outer_query.addShouldQuery(inner_string_query)
				
			
			if len(outer_query.query_stack) > 0:
				# add them all to must to ensure that the stacked query results must be fullfilled when connected with other query types
				self.query['bool']['must'].append(outer_query.query_stack)
				logger.debug(self.query)
		
		
		self.addUserLimitation()
		self.deleteEmptySubqueries()


	def updateMaxResultWindow(self, max_result_window):
		#adjust max number of results that can be fetched
		#logger.debug(self.client.indices.get_settings(index=self.index))
		
		body = {'index': {'max_result_window': max_result_window}}
		self.client.indices.put_settings(index=self.index, body=body)


	def singleHierarchyAggregationSearch(self, hierarchy_name, hierarchy_pathes_dict = {}):
		
		self.setQuery()
		buckets_query = HierarchyQueries(hierarchy_pathes_dict = hierarchy_pathes_dict, users_project_ids = self.users_project_ids, source_fields = [hierarchy_name]) #, buckets_sort_alphanum = True)
		aggs = buckets_query.getHierarchiesQuery()
		
		logger.debug(json.dumps(aggs))
		logger.debug(json.dumps(self.query))
		
		source_fields = False
		
		response = self.client.search(index=self.index, query=self.query, source=source_fields, aggs=aggs, size = 0)
		
		buckets = []
		if 'aggregations' in response:
			self.raw_aggregations = response['aggregations']
			buckets = self.getBucketListFromAggregation(self.raw_aggregations[hierarchy_name])
		
		'''
		if 'aggregations' in response:
			self.raw_aggregations = response['aggregations']
			buckets = self.getBucketListFromCompositeAggregation(self.raw_aggregations[aggregation_name])
		'''
		return buckets


	def singleAggregationSearch(self, aggregation_name, buckets_search_term = None, size = 5000, buckets_sort_alphanum = True, buckets_sort_dir = 'asc'):
		self.setQuery()
		buckets_query = BucketAggregations(users_project_ids = self.users_project_ids, source_fields = [aggregation_name], size = size, 
			buckets_search_term = buckets_search_term, buckets_sort_alphanum = buckets_sort_alphanum, buckets_sort_dir = buckets_sort_dir)
		aggs = buckets_query.getAggregationsQuery()
		
		logger.debug(json.dumps(aggs))
		logger.debug(json.dumps(self.query))
		
		source_fields = False
		
		response = self.client.search(index=self.index, query=self.query, source=source_fields, aggs=aggs, size = 0)
		
		buckets = []
		if 'aggregations' in response:
			self.raw_aggregations = response['aggregations']
			buckets = self.getBucketListFromAggregation(self.raw_aggregations[aggregation_name])
		
		return buckets


	def suggestionsSearch(self, buckets_search_term, size = 10, buckets_sort_alphanum = True, buckets_sort_dir = 'asc'):
		
		self.setQuery()
		buckets_query = BucketAggregations(users_project_ids = self.users_project_ids, source_fields = [], size = size, 
			buckets_search_term = buckets_search_term, buckets_sort_alphanum = buckets_sort_alphanum, buckets_sort_dir = buckets_sort_dir, add_include_filter = True)
		aggs = buckets_query.getAggregationsQuery()
		
		#logger.debug(json.dumps(aggs))
		#logger.debug(json.dumps(self.query))
		
		source_fields = False
		
		response = self.client.search(index=self.index, query=self.query, source=source_fields, aggs=aggs, size = 0)
		
		buckets = []
		if 'aggregations' in response:
			self.raw_aggregations = response['aggregations']
			buckets = self.getParsedAggregations()
		
		return buckets



	def paginatedSearch(self):
		
		self.updateMaxResultWindow(max_result_window=2000000)
		self.readIndexMapping()
		
		self.setPageSize()
		self.setStartRow()
		self.setSorting()
		
		#self.queryConstructor is set in the derived classes
		self.setQuery()
		
		aggs = None
		if len(self.bucket_fields) > 0:
			buckets_query = BucketAggregations(users_project_ids = self.users_project_ids, source_fields = self.bucket_fields)
			aggs = buckets_query.getAggregationsQuery()
		
		if len(self.hierarchy_fields) > 0:
			hierarchies_query = HierarchyQueries(hierarchy_pathes_dict = self.hierarchy_pathes_dict, users_project_ids = self.users_project_ids, source_fields = self.hierarchy_fields)
			if aggs is not None:
				aggs.update(hierarchies_query.getHierarchiesQuery())
			else:
				aggs = hierarchies_query.getHierarchiesQuery()
		
		#logger.debug(self.sort)
		logger.debug(json.dumps(aggs))
		logger.debug(json.dumps(self.query))
		#logger.debug(json.dumps(self.sort))
		
		if len(self.source_fields) <= 0:
			source_fields = True
		else:
			# add the fields that are needed for filtering the results in WithholdFilters.applyFiltersToSources()
			if 'Projects.DB_ProjectID' not in self.source_fields:
				self.source_fields.append('Projects.DB_ProjectID')
			self.source_fields.extend(self.withhold_fields)
			source_fields = self.source_fields
			
			# add the fields that are necessary for linking out from the retrieved data
			if 'PartAccessionNumber' not in self.source_fields:
				self.source_fields.append('PartAccessionNumber')
			if 'StableIdentifierURL' not in self.source_fields:
				self.source_fields.append('StableIdentifierURL')
		
		response = self.client.search(index=self.index, size=self.pagesize, sort=self.sort, query=self.query, from_=self.start, source=source_fields, track_total_hits=True, aggs=aggs)
		
		resultnum = response['hits']['total']['value']
		maxpage = self.getMaxPage(resultnum)
		
		if self.start > resultnum:
			self.search_params['page'] = maxpage
			self.setStartRow()
			response = self.client.search(index=self.index, size=self.pagesize, sort=self.sort, query=self.query, from_=self.start, source=source_fields, track_total_hits=True, aggs=aggs)
		
		if 'aggregations' in response:
			self.raw_aggregations = response['aggregations']
		else:
			self.raw_aggregations = {}
		
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


	def getBucketListFromAggregation(self, raw_aggregation):
		#pudb.set_trace()
		buckets = []
		if 'buckets' in raw_aggregation:
			if isinstance(raw_aggregation['buckets'], list) or isinstance(raw_aggregation['buckets'], tuple):
				for bucket in raw_aggregation['buckets']:
					buckets.append([bucket['key'], bucket['doc_count']])
			elif isinstance(raw_aggregation['buckets'], dict) and 'buckets' in raw_aggregation['buckets']:
				buckets = self.getBucketListFromAggregation(raw_aggregation['buckets'])
			else:
				buckets = []
		return buckets


	def getBucketListFromCompositeAggregation(self, raw_aggregation):
		#pudb.set_trace()
		buckets = []
		
		try:
			bucket_dicts = [bucket_dict for bucket_dict in raw_aggregation['buckets']['composite_buckets']['buckets']]
		except:
			return []
		
		for bucket_dict in bucket_dicts:
			buckets.append([bucket_dict['key']['Value'], bucket_dict['key']['ItemID'], bucket_dict['key']['ParentID'], bucket_dict['key']['TreeLevel'], bucket_dict['doc_count']])
		return buckets


	def getParsedAggregations(self):
		self.parseRawAggregations()
		return self.aggregations


	def getLastUpdated(self):
		sort = [{"LastUpdated":{"order":"desc"}}]
		source_fields = ["LastUpdated", "_id", "PartAccessionNumber"]
		response = self.client.search(index=self.index, size=1, sort=sort, source=source_fields)
		
		docs = [doc for doc in response['hits']['hits']]
		
		if len(docs) != 1:
			return None
		else: 
			lastupdated = docs[0]['_source']['LastUpdated']
		
		return lastupdated


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
		'stack_queries': 'Rulik',
	}
	
	
	pudb.set_trace()
	es_search = ES_Searcher(search_params = search_params, user_id = 'bquast', users_project_ids = [634, 30000])
	es_search.paginatedSearch()
	facets = es_search.raw_aggregations
	
	
	



