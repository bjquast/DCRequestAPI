import logging
log = logging.getLogger(__name__)

from pyramid.response import Response
from pyramid.renderers import render_to_response
from pyramid.view import (view_config, view_defaults)
from pyramid.httpexceptions import HTTPFound, HTTPNotFound, HTTPSeeOther

from ElasticSearch.ES_Searcher import ES_Searcher

from DCRequestAPI.lib.UserLogin.UserLogin import UserLogin

from dwb_authentication.security import SecurityPolicy
from dwb_authentication.DWB_Servers import DWB_Servers

import pudb
import json


class AggregationsView():
	def __init__(self, request):
		self.request = request
		self.uid = self.request.authenticated_userid
		
		self.roles = self.request.identity['dwb_roles']
		self.users_projects = self.request.identity['projects']
		self.users_project_ids = [project[0] for project in self.users_projects]
		
		self.userlogin = UserLogin(self.request)
		
		self.dwb_servers = DWB_Servers()
		self.available_dwb_cons = self.dwb_servers.get_available_dwb_cons()
		
		self.messages = []


	@view_config(route_name='aggregations', accept='application/json', renderer="json")
	def viewAggregationsJSON(self):
		
		#pudb.set_trace()
		
		if 'username' in self.request.params:
			self.userlogin.authenticate_user()
			self.uid, self.roles, self.users_projects, self.users_project_ids = self.userlogin.get_identity()
		
		elif 'token' in self.request.params:
			security = SecurityPolicy()
			identity = security.get_identity_by_token(self.request)
			self.uid = identity['username']
			self.roles = identity['dwb_roles']
			self.users_projects = identity['projects']
			self.users_project_ids = [project[0] for project in self.users_projects]
		
		self.messages.extend(self.userlogin.get_messages())
		
		self.set_search_params()
		
		# remove aggregation from term filters to get all buckets in this aggregation
		# but keep all other search params?
		
		if 'aggregation' in self.search_params:
			agg_name = self.search_params['aggregation']
			if agg_name in self.search_params['term_filters']:
				del self.search_params['term_filters'][agg_name]
		
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
			'messages': self.messages
		}
		
		return pagecontent

