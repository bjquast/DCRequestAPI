import logging
log = logging.getLogger(__name__)

from pyramid.response import Response
from pyramid.renderers import render_to_response
from pyramid.view import (view_config, view_defaults)
from pyramid.httpexceptions import HTTPFound, HTTPNotFound, HTTPSeeOther

from ElasticSearch.ES_Searcher import ES_Searcher
from DCRequestAPI.lib.SearchResults.IUPartsListTable import IUPartsListTable

import pudb
import json



class IUPartsListView():
	def __init__(self, request):
		self.request = request
		self.uid = self.request.authenticated_userid
		
		
		
		self.roles = self.request.identity['dwb_roles']
		self.users_projects = self.request.identity['projects']
		self.users_project_ids = [project[0] for project in self.users_projects]
		


	@view_config(route_name='iupartslist', accept='application/json', renderer="json")
	def IUPartsListJSON(self):
		
		#pudb.set_trace()
		
		self.set_search_params()
		
		iupartstable = IUPartsListTable()
		sourcefields = iupartstable.iupartstable.getDefaultSourceFields()
		coldefs = iupartstable.coldefs
		
		es_searcher = ES_Searcher(search_params = self.search_params, user_id = self.uid, users_project_ids = self.users_project_ids)
		es_searcher.setSourceFields(source_fields = sourcefields)
		docs, maxpage, resultnum = es_searcher.paginatedSearch()
		aggregations = es_searcher.getParsedAggregations()
		iupartslist = iupartstable.getRowContent(doc_sources = [doc['_source'] for doc in docs], users_project_ids = self.users_project_ids)
		
		# set the coldefs for each iupart as keys for the json dicts 
		iuparts = []
		for doc in docs:
			iupartdict = {
				'_id': doc['_id']
			}
			
			for key in ['_score', '_ignored']:
				if key in doc:
					iupartdict[key] = doc[key]
			
			for colkey in default_coldefkeys:
				if colkey in doc['_source']:
					iupartdict[colkey] = doc['_source'][colkey]
			
			iuparts.append(iupartdict)
		
		pagecontent = {
			'title': 'API for requests on DiversityCollection database',
			'maxpage': maxpage,
			'resultnum': resultnum,
			'page': int(self.search_params.get('page', 1)),
			'pagesize': int(self.search_params.get('pagesize', 1000)),
			'search_params': self.search_params,
			'iuparts': iuparts,
			'aggregations': aggregations,
		}
		
		return pagecontent


	@view_config(route_name='iupartslist', accept='text/html', renderer="DCRequestAPI:templates/iupartslist.pt")
	def IUPartsListHTML(self):
		
		#pudb.set_trace()
		
		self.set_search_params()
		self.set_requeststring()
		
		iupartstable = IUPartsListTable()
		if len(self.search_params['result_table_columns']) > 0:
			iupartstable.setSelectedSourceFields(self.search_params['result_table_columns'])
		
		selected_sourcefields = iupartstable.getSelectedSourceFields()
		default_sourcefields = iupartstable.getDefaultSourceFields()
		coldefs = iupartstable.coldefs
		
		
		es_searcher = ES_Searcher(search_params = self.search_params, user_id = self.uid, users_project_ids = self.users_project_ids)
		es_searcher.setSourceFields(selected_sourcefields)
		docs, maxpage, resultnum = es_searcher.paginatedSearch()
		aggregations = es_searcher.getParsedAggregations()
		iupartslist = iupartstable.getRowContent(doc_sources = [doc['_source'] for doc in docs], users_project_ids = self.users_project_ids)
		
		pagecontent = {
			'request': self.request,
			'pagetitle': 'API for requests on DiversityCollection database',
			'maxpage': maxpage,
			'resultnum': resultnum,
			'page': int(self.search_params.get('page', 1)),
			'pagesize': int(self.search_params.get('pagesize', 1000)),
			'requestparamsstring': self.requeststring,
			'search_params': self.search_params,
			'iupartslist': iupartslist,
			'aggregations': aggregations,
			'coldefs': coldefs,
			'default_sourcefields': default_sourcefields,
			'selected_sourcefields': selected_sourcefields, 
			'open_filter_selectors': self.search_params['open_filter_selectors'],
			'authenticated_user': self.uid
		}
		return pagecontent



	def set_search_params(self):
		
		# check if there is a json body in the request
		try:
			json_params = self.request.json_body
			# prepare the params as dict of lists so it can be used in self.set_search_params()
			request_params = {}
			for key in json_params:
				request_params[key] = []
				if isinstance(json_params[key], list) or isinstance(json_params[key], tuple):
					request_params[key].extend(json_params[key])
				else:
					request_params[key].append(json_params[key])
		except:
			request_params = self.request.params.dict_of_lists()
		
		self.search_params = {}
		
		simple_params = ['pagesize', 'page', 'sorting_col', 'sorting_dir', 'match_query']
		complex_params = ['term_filters',]
		list_params = ['open_filter_selectors', 'result_table_columns']
		
		for param_name in simple_params: 
			if param_name in request_params and len(request_params[param_name]) > 0:
				self.search_params[param_name] = request_params[param_name][-1]
		
		for param_name in complex_params: 
			if param_name in request_params and len(request_params[param_name]) > 0:
				for searchquery in request_params[param_name]:
					query = searchquery.split(':')
					if len(query) == 2:
						if param_name not in self.search_params:
							self.search_params[param_name] = {}
						if query[0] not in self.search_params[param_name]:
							self.search_params[param_name][query[0]] = []
						self.search_params[param_name][query[0]].append(query[1])
			else:
				self.search_params[param_name] = []
		
		for param_name in list_params:
			if param_name in request_params:
				self.search_params[param_name] = request_params[param_name]
			else:
				self.search_params[param_name] = []
		
		return


	def set_requeststring(self):
		self.requeststring = ''
		paramslist = []
		request_params = self.request.params.dict_of_lists()
		for param in request_params:
			# if param not in ['pagesize', 'page']:
			for value in request_params[param]:
				paramslist.append('{0}={1}'.format(param, value))
		
		self.requeststring = '&'.join(paramslist)
		return
	
		
	'''
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
	'''
