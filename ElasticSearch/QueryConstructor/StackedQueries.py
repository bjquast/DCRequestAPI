import logging
import logging.config
logging.config.fileConfig('logging.conf')
logger = logging.getLogger('elastic_queries')

import pudb

from ElasticSearch.QueryConstructor.QueryConstructor import QueryConstructor
from ElasticSearch.QueryConstructor.StringQueries import StringQueries


class StackedQueries():
	def __init__(self, search_params, users_project_ids):
		self.search_params = search_params
		self.users_project_ids = users_project_ids
		
		self.query_stack = {
			'bool': {
				'must': []
			}
		}
		self.create_query_stack()


	def create_query_stack(self):
		"""
		iterate over the stack_queries list wich contains dicts with:
		{
			['string']: list,
			['date_from']: list,
			['date_to']: list,
			['field']: list,
			['query_type']: list,
			['outer_connector']: string 'AND'/'OR',
			['inner_connector']: string 'AND'/'OR'
		}
		
		the elements lists define a sub query each, so if there are 2 strings and 2 fields etc. these are 2 sub queries with:
		query[0] = {'string' = search_params['stack_queries'][0]['string'][0], 'field': search_params['stack_queries'][0]['field'][0], ...}
		query[1] = {'string' = search_params['stack_queries'][0]['string'][1], 'field': search_params['stack_queries'][0]['field'][1], ...}
		
		the queries are separated by StackedInnerQuery.readQueryDict()
		
		inner queries are appended to a list of queries connected to each other according to the inner_connector
		these inner queries are then appended to a list of outer queries according to the outer_connector
		
		TODO: this has to be adopted for separate requests on strings and date ranges and other query types
		"""
		#pudb.set_trace()
		outer_query = StackedOuterQuery()
		
		if 'stack_queries' in self.search_params:
			# set outer connector to AND for the first query, otherwise it might result in all documents matched when it starts with an OR query and it is the only query
			if len(self.search_params['stack_queries']) > 0:
				self.search_params['stack_queries'][0]['outer_connector'] = 'AND'
			
			# iterate over the outer queries,
			# the StackedInnerQuery class then iterates over the inner queries
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
				self.query_stack = outer_query.query_stack
		return


class StackedInnerQuery(QueryConstructor):
	def __init__(self, query_dict, users_project_ids = []):
		QueryConstructor.__init__(self)
		
		self.request_dict = query_dict
		self.users_project_ids = users_project_ids
		
		self.source_fields = self.request_dict['field']
		
		self.string_type = 'simple_query_string'
		
		self.readQueryDict()


	def readQueryDict(self):
		"""
		# iterate over the inner queries and put them together into a list of dicts
		TODO: needs to be reworked together with RequestParams where the stacked queries are set
		"""
		
		#pudb.set_trace()
		if not len(self.request_dict['query_type']) > 0 and len(self.request_dict['string']) == len(self.request_dict['field']):
			raise ValueError('count of terms and fields must be the same')
		
		self.query_list = []
		
		# check if 'all fields' are selected
		for i in range(len(self.request_dict['query_type'])):
			if self.request_dict['query_type'][i] == 'term' and self.request_dict['string'][i]:
				
				# TODO: it is not useful to give a dictionary as parameter when fields and connector are set in the constructor of StringQueries()
				# it comes from the idea that multiple queries can be send to StringQueries() and the class is in charge to put them together
				# see TODO in StringQueries.setQueryList()
				
				if self.request_dict['field'][i] == 'all fields':
					query_dict = {
						'term': self.request_dict['string'][i],
						'fields': self.fieldconf.stacked_term_fields,
						'inner_connector': self.request_dict['inner_connector']
					}
					self.query_list.append(query_dict)
				else:
					query_dict = {
						'term': self.request_dict['string'][i],
						'fields': [self.request_dict['field'][i]],
						'inner_connector': self.request_dict['inner_connector']
					}
					self.query_list.append(query_dict)
			
			elif self.request_dict['query_type'][i] == 'date' and (self.request_dict['date_from'][i] or self.request_dict['date_from'][i]):
				query_dict = {
					'date_from': self.request_dict.get(['date_from'][i], ''),
					'date_to': self.request_dict.get(['date_to'][i], ''),
					'fields': [self.request_dict['field'][i]],
					'inner_connector': self.request_dict['inner_connector']
				}
				self.query_list.append(query_dict)
		
		return 



	def getInnerStackQuery(self):
		inner_queries = []
		inner_query = {
			'bool': {
				'should': [],
				'must': []
			}
		}
		
		for query_dict in self.query_list:
			if 'term' in query_dict:
				string_query = StringQueries(self.users_project_ids, query_dict['fields'], query_dict['inner_connector'])
				q = string_query.getQueries([query_dict])
				
				if query_dict['inner_connector'].upper() == 'OR':
					inner_query['bool']['should'].extend(q)
				elif query_dict['inner_connector'].upper() == 'AND':
					inner_query['bool']['must'].extend(q)
				
			elif 'date_from' in self.query_list or 'date_to' in self.query_list:
				#date_range_query = DateRangeQueries(self.users_project_ids, query_dict['fields'], query_dict['inner_connector'])
				#q = string_query.getQueries([query_dict])
				
				#if query_dict['inner_connector'].upper() == 'OR':
				#	inner_query['bool']['should'].extend(q)
				#elif query_dict['inner_connector'].upper() == 'AND':
				#	inner_query['bool']['must'].extend(q)
				pass
		
		if len(inner_query['bool']['must']) < 1 and len(inner_query['bool']['should']) < 1:
			inner_query = None
		
		return inner_query



class StackedOuterQuery():
	def __init__(self):
		
		self.should = []
		self.must = [] 
		
		self.query_stack = {
			'bool': {
				'must': [],
				'should': [],
				'minimum_should_match': 1
			}
		}


	def deleteEmptyElements(self):
		if 'should' in self.query_stack['bool'] and len(self.query_stack['bool']['should']) < 1:
			del self.query_stack['bool']['should']
			if 'minimum_should_match' in self.query_stack['bool']:
				del self.query_stack['bool']['minimum_should_match']
		if 'must' in self.query_stack['bool'] and len(self.query_stack['bool']['must']) < 1:
			del self.query_stack['bool']['must']


	def addShouldQuery(self, inner_query):
		self.deleteEmptyElements()
		
		if len(inner_query) > 0:
			new_outer_query = {
				'bool': {
					'should': [
						inner_query
					],
					'minimum_should_match': 1
				}
			}
			
			if len(self.query_stack) > 0:
				new_outer_query['bool']['should'].append(self.query_stack)
			
			self.query_stack = new_outer_query
		
		return


	def addMustQuery(self, inner_query):
		self.deleteEmptyElements()
		
		if len(inner_query) > 0:
			new_outer_query = {
				'bool': {
					'must': [
						inner_query
					]
				}
			}
			
			if len(self.query_stack) > 0:
				new_outer_query['bool']['must'].append(self.query_stack)
			
			self.query_stack = new_outer_query
		
		return
