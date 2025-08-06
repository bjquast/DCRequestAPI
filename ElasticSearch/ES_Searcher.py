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
from ElasticSearch.QueryConstructor.DateAggregations import DateAggregations
from ElasticSearch.QueryConstructor.TermFilterQueries import TermFilterQueries
from ElasticSearch.QueryConstructor.HierarchyQueries import HierarchyQueries
from ElasticSearch.QueryConstructor.StackedQueries import StackedInnerQuery, StackedOuterQuery
#from ElasticSearch.QueryConstructor.RangeQueries import RangeQueries
from ElasticSearch.FieldConfig import FieldConfig


class ES_Searcher():
	def __init__(self, search_params = {}, user_id = None, users_project_ids = []):
		es_connector = ES_Connector()
		self.client = es_connector.client
		
		self.search_params = search_params
		self.user_id = user_id
		self.users_project_ids = users_project_ids
		self.restrict_to_users_projects = False
		if 'restrict_to_users_projects' in self.search_params and self.search_params['restrict_to_users_projects'] and self.user_id:
			self.restrict_to_users_projects = True
		
		self.index = 'iuparts'
		self.source_fields = []
		self.term_filters = []
		self.date_filters = []
		self.hierarchy_filters = []
		self.hierarchy_pathes_dict = {}
		
		self.pagesize = 1000
		self.start = 0
		
		self.withholdfilters = WithholdFilters()
		self.withhold_fields = self.withholdfilters.getWithholdFields()
		
		self.fieldconfig = FieldConfig()


	def __getMaxPage(self, hits):
		maxpage = math.ceil(hits/self.pagesize)
		return maxpage


	def __readIndexMapping(self):
		try:
			self.mapping = MappingsDict[self.index]['properties']
		except:
			self.mapping = {}


	def __setPageSize(self):
		if 'pagesize' in self.search_params:
			self.pagesize = int(self.search_params['pagesize'])
		else:
			pass
		return


	def __setStartRow(self, page = None):
		if page is not None:
			if int(page) < 1:
				page = 1
			self.start = self.pagesize * int(page)-1
		elif 'page' in self.search_params:
			if int(self.search_params['page']) < 1:
				self.search_params['page'] = 1
			self.start = self.pagesize * (int(self.search_params['page'])-1)
		else:
			self.start = 0
		return


	def __setSorting(self):
		#pudb.set_trace()
		self.__readIndexMapping()
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


	def __addUserLimitation(self):
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



	def setFilterFields(self, filter_fields = []):
		# set the specific fields for aggs from terms, date, hierarchy fields 
		
		self.filter_fields = list(filter_fields)
		self.term_filters = []
		self.date_filters = []
		for field in self.filter_fields:
			if field in self.fieldconfig.term_fields:
				self.term_filters.append(field)
			elif field in self.fieldconfig.date_fields:
				self.date_filters.append(field)
			elif field in self.fieldconfig.hierarchy_fields:
				self.hierarchy_filters.append(field)
		return


	def setHierarchyPathesDict(self, hierarchy_pathes_dict = {}):
		self.hierarchy_pathes_dict = hierarchy_pathes_dict
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
		pudb.set_trace()
		
		
		if 'term_filters' in self.search_params:
			connector = 'AND'
			if 'term_filters_connector' in self.search_params:
				connector = self.search_params['term_filters_connector']
			
			
			# append source fields from term_filters not yet in self.term_filters
			# this is due to the term_filters comming from hierarchy aggregations
			hierarchy_bucket_fields = list(self.term_filters)
			for key in self.search_params['term_filters']:
				if key not in hierarchy_bucket_fields:
					hierarchy_bucket_fields.append(key)
			
			filter_queries = TermFilterQueries(users_project_ids = self.users_project_ids, source_fields = hierarchy_bucket_fields, connector = connector).getTermFilterQueries(self.search_params['term_filters'])
			self.query['bool']["filter"].extend(filter_queries)
		
		#pudb.set_trace()
		'''
		if 'range_queries' in self.search_params:
			connector = 'AND'
			if 'term_filters_connector' in self.search_params:
				connector = self.search_params['term_filters_connector']
			
			range_queries = RangeQueries(users_project_ids = self.users_project_ids, source_fields = source_fields, connector = connector).setRangeQueries(self.search_params['range_queries'])
			self.query['bool']["filter"].extend(filter_queries)
			
			
			pass
		'''
		
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
		
		
		self.__addUserLimitation()
		self.deleteEmptySubqueries()


	def updateMaxResultWindow(self, max_result_window):
		#adjust max number of results that can be fetched
		#logger.debug(self.client.indices.get_settings(index=self.index))
		
		body = {'index': {'max_result_window': max_result_window}}
		self.client.indices.put_settings(index=self.index, body=body)


	'''
	def singleHierarchyAggregationSearch(self, hierarchy_name, hierarchy_pathes_dict = {}):
		
		self.setQuery()
		buckets_query = HierarchyQueries(hierarchy_pathes_dict = hierarchy_pathes_dict, users_project_ids = self.users_project_ids, source_fields = [hierarchy_name]) #, buckets_sort_alphanum = True)
		aggs = buckets_query.getHierarchiesQuery()
		
		logger.debug(json.dumps(aggs))
		logger.debug(json.dumps(self.query))
		
		source_fields = False
		
		response = self.client.search(index=self.index, query=self.query, source=source_fields, aggs=aggs, size = 0)
		pudb.set_trace()
		buckets = []
		if 'aggregations' in response:
			self.raw_aggregations = response['aggregations']
			buckets = self.__getBucketListFromAggregation(self.raw_aggregations[hierarchy_name])
		
		return buckets
	'''


	def searchHierarchyAggregations(self, hierarchy_pathes_dict = None, source_fields = None):
		if hierarchy_pathes_dict is None:
			hierarchy_pathes_dict = {}
		if source_fields is None:
			source_fields = []
		
		self.setQuery()
		buckets_query = HierarchyQueries(hierarchy_pathes_dict = hierarchy_pathes_dict, users_project_ids = self.users_project_ids, source_fields = source_fields) #, buckets_sort_alphanum = True)
		aggs = buckets_query.getHierarchiesQuery()
		
		logger.debug(json.dumps(aggs))
		logger.debug(json.dumps(self.query))
		
		source_fields = False
		
		response = self.client.search(index=self.index, query=self.query, source=source_fields, aggs=aggs, size = 0)
		
		self.raw_aggregations = response['aggregations']
		aggregations = self.getParsedAggregations()
		
		'''
		if 'aggregations' in response:
			self.raw_aggregations = response['aggregations']
			buckets = self.__getBucketListFromCompositeAggregation(self.raw_aggregations[aggregation_name])
		'''
		return aggregations


	def singleAggregationSearch(self, aggregation_name, buckets_search_term = None, size = 5000, buckets_sort_alphanum = True, buckets_sort_dir = 'asc'):
		self.setQuery()
		pudb.set_trace()
		
		if aggregation_name in self.fieldconfig.date_fields:
			buckets_query = DateAggregations(users_project_ids = self.users_project_ids, source_fields = [aggregation_name], size = size, 
				buckets_sort_alphanum = buckets_sort_alphanum, buckets_sort_dir = buckets_sort_dir)
			aggs = buckets_query.getAggregationsQuery()
		
		elif aggregation_name in self.fieldconfig.term_fields:
			buckets_query = BucketAggregations(users_project_ids = self.users_project_ids, source_fields = [aggregation_name], size = size, 
				buckets_search_term = buckets_search_term, buckets_sort_alphanum = buckets_sort_alphanum, buckets_sort_dir = buckets_sort_dir)
			aggs = buckets_query.getAggregationsQuery()
		
		else:
			aggs = None
		
		logger.debug(json.dumps(aggs))
		logger.debug(json.dumps(self.query))
		
		source_fields = False
		
		response = self.client.search(index=self.index, query=self.query, source=source_fields, aggs=aggs, size = 0)
		
		buckets = []
		if 'aggregations' in response:
			self.raw_aggregations = response['aggregations']
			buckets = self.__getBucketListFromAggregation(self.raw_aggregations[aggregation_name])
		
		return buckets


	def suggestionsSearch(self, buckets_search_term, size = 10, buckets_sort_alphanum = True, buckets_sort_dir = 'asc'):
		# do suggestion search only for term filters, makes no sence for dates and hierarchies?!
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


	def countResultDocsSearch(self):
		self.updateMaxResultWindow(max_result_window=2000000)
		self.__setPageSize()
		self.setQuery()
		aggs = None
		logger.debug(json.dumps(self.query))
		
		response = self.client.search(index=self.index, size=self.pagesize, query=self.query, from_=self.start, source=False, track_total_hits=True)
		
		resultnum = response['hits']['total']['value']
		maxpage = self.__getMaxPage(resultnum)
		return maxpage, resultnum


	def searchDocsByPage(self, page):
		"""
		Search method for csv export
		no aggregations requested
		return docs for the specified result page
		csv export code iterates over the existing pages
		"""
		self.__setPageSize()
		self.__setStartRow(page)
		self.__setSorting()
		
		self.setQuery()
		
		logger.debug(json.dumps(self.query))
		
		if len(self.source_fields) <= 0:
			source_fields = True
		else:
			self.__addRequiredSourceFields()
			source_fields = self.source_fields
		
		response = self.client.search(index=self.index, size=self.pagesize, sort=self.sort, query=self.query, from_=self.start, source=source_fields, track_total_hits=True)
		
		resultnum = response['hits']['total']['value']
		maxpage = self.__getMaxPage(resultnum)
		
		if self.start > resultnum:
			self.search_params['page'] = maxpage
			self.__setStartRow()
			response = self.client.search(index=self.index, size=self.pagesize, sort=self.sort, query=self.query, from_=self.start, source=source_fields, track_total_hits=True)
		
		docs = [doc for doc in response['hits']['hits']]
		docs = self.withholdfilters.applyFiltersToSources(docs, self.users_project_ids)
		
		return docs, maxpage, resultnum



	def paginatedSearch(self):
		pudb.set_trace()
		self.updateMaxResultWindow(max_result_window=2000000)
		self.__setPageSize()
		self.__setStartRow()
		self.__setSorting()
		
		#self.queryConstructor is set in the derived classes
		self.setQuery()
		
		aggs = None
		if len(self.term_filters) > 0:
			buckets_query = BucketAggregations(users_project_ids = self.users_project_ids, source_fields = self.term_filters)
			aggs = buckets_query.getAggregationsQuery()
		
		if len(self.date_filters) > 0:
			date_aggregator = DateAggregations(users_project_ids = self.users_project_ids, source_fields = self.date_filters)
			if aggs is not None:
				aggs.update(date_aggregator.getAggregationsQuery())
			else:
				aggs = date_aggregator.getAggregationsQuery()
		
		if len(self.hierarchy_filters) > 0:
			hierarchies_query = HierarchyQueries(hierarchy_pathes_dict = self.hierarchy_pathes_dict, users_project_ids = self.users_project_ids, source_fields = self.hierarchy_filters)
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
			self.__addRequiredSourceFields()
			source_fields = self.source_fields
		
		response = self.client.search(index=self.index, size=self.pagesize, sort=self.sort, query=self.query, from_=self.start, source=source_fields, track_total_hits=True, aggs=aggs)
		
		resultnum = response['hits']['total']['value']
		maxpage = self.__getMaxPage(resultnum)
		
		if self.start > resultnum:
			self.search_params['page'] = maxpage
			self.__setStartRow()
			response = self.client.search(index=self.index, size=self.pagesize, sort=self.sort, query=self.query, from_=self.start, source=source_fields, track_total_hits=True, aggs=aggs)
		
		if 'aggregations' in response:
			self.raw_aggregations = response['aggregations']
		else:
			self.raw_aggregations = {}
		
		docs = [doc for doc in response['hits']['hits']]
		docs = self.withholdfilters.applyFiltersToSources(docs, self.users_project_ids)
		
		return docs, maxpage, resultnum


	def __addRequiredSourceFields(self):
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
		return


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


	def __getBucketListFromAggregation(self, raw_aggregation):
		pudb.set_trace()
		buckets = []
		if 'buckets' in raw_aggregation:
			if isinstance(raw_aggregation['buckets'], list) or isinstance(raw_aggregation['buckets'], tuple):
				for bucket in raw_aggregation['buckets']:
					buckets.append([bucket['key'], bucket['doc_count']])
			elif isinstance(raw_aggregation['buckets'], dict) and 'buckets' in raw_aggregation['buckets']:
				buckets = self.__getBucketListFromAggregation(raw_aggregation['buckets'])
			else:
				buckets = []
		return buckets


	def __getBucketListFromCompositeAggregation(self, raw_aggregation):
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
	
	
	



