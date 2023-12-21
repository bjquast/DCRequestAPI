import logging
log = logging.getLogger(__name__)

from pyramid.response import Response
from pyramid.renderers import render_to_response
from pyramid.view import (view_config, view_defaults)
from pyramid.httpexceptions import HTTPFound, HTTPNotFound, HTTPSeeOther

from DCRequestAPI.lib.ElasticSearch.ES_Searcher import ES_Searcher

import pudb
import json



class IUPartsListView():
	def __init__(self, request):
		self.request = request
		self.uid = self.request.authenticated_userid
		
		self.roles = self.request.identity['dwb_roles']
		self.users_projects = self.request.identity['projects']
		


	@view_config(route_name='iupartslist', accept='application/json', renderer="DCRequestAPI:templates/help.pt")
	def IUPartsList(self):
		pudb.set_trace()
		
		json_dict = self.request.json_body
		self.search_params = json_dict.get('search_params', {})
		
		es_searcher = ES_Searcher(search_params = {}, user_id = self.uid, users_projects = self.users_projects)
		docs, maxpage = es_searcher.paginatedSearch()
		
		
		pagecontent = {
			'request': self.request,
			'pagetitle': 'API for requests on DiversityCollection database',
			'maxpage': maxpage,
			'currentpage': self.search_params.get('current_page', 1)
			
		}
		return pagecontent


	@view_config(route_name='iupartslist', accept='text/html', renderer="DCRequestAPI:templates/help.pt")
	def IUPartsList(self):
		pudb.set_trace()
		
		self.set_search_params()
		
		es_searcher = ES_Searcher(search_params = {}, user_id = self.uid, users_projects = self.users_projects)
		docs, maxpage = es_searcher.paginatedSearch()
		
		
		pagecontent = {
			'request': self.request,
			'pagetitle': 'API for requests on DiversityCollection database',
			'maxpage': maxpage,
			'currentpage': self.search_params.get('page', 1)
			
		}
		return pagecontent



	def set_search_params(self):
		self.search_params = {}
		
		simple_params = ['pagesize', 'page', 'sorting_col', 'sorting_dir', 'match_query']
		complex_params = ['term_filters',]
		
		request_params = self.request.params.dict_of_lists()
		for request_param in request_params:
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
