from pyramid.response import Response
from pyramid.renderers import render_to_response
from pyramid.view import (view_config, view_defaults)
from pyramid.httpexceptions import HTTPFound, HTTPNotFound, HTTPSeeOther

from ElasticSearch.ES_Searcher import ES_Searcher

from DCRequestAPI.lib.SearchResults.IUPartsTable import IUPartsTable
from DCRequestAPI.lib.UserLogin.UserLogin import UserLogin

from DCRequestAPI.views.RequestParams import RequestParams


import pudb
import json



class IUPartsListView():
	def __init__(self, request):
		self.request = request
		self.uid = self.request.authenticated_userid
		
		self.roles = self.request.identity['dwb_roles']
		self.users_projects = self.request.identity['projects']
		self.users_project_ids = [project[0] for project in self.users_projects]
		
		self.userlogin = UserLogin(self.request)
		self.messages = []
		
		request_params = RequestParams(self.request)
		self.search_params = request_params.search_params
		self.requeststring = request_params.requeststring
		self.credentials = request_params.credentials
		
		# check if there are any authentication data given in request
		# and if so: authenticate the user
		if 'logout' in self.credentials and self.credentials['logout'] == 'logout':
			self.userlogin.log_out_user()
			self.uid, self.roles, self.users_projects, self.users_project_ids = self.userlogin.get_identity()
		
		if 'username' in self.credentials and 'password' in self.credentials:
			self.token = self.userlogin.authenticate_user(self.credentials['username'], self.credentials['password'])
			self.uid, self.roles, self.users_projects, self.users_project_ids = self.userlogin.get_identity()
		
		elif 'token' in self.credentials:
			self.userlogin.authenticate_by_token(self.credentials['token'])
			self.uid, self.roles, self.users_projects, self.users_project_ids = self.userlogin.get_identity()
		
		self.messages.extend(self.userlogin.get_messages())


	@view_config(route_name='iupartslist', accept='application/json', renderer="json")
	def IUPartsListJSON(self):
		
		#pudb.set_trace()
		
		iupartstable = IUPartsTable()
		if len(self.search_params['result_table_columns']) > 0:
			iupartstable.setSelectedSourceFields(self.search_params['result_table_columns'])
		
		restrict_to_users_projects = False
		if 'restrict_to_users_projects' in self.search_params and self.uid is not None:
			restrict_to_users_projects = True
		
		selected_sourcefields = iupartstable.selected_sourcefields
		#default_sourcefields = iupartstable.default_sourcefields
		selected_bucketfields = iupartstable.selected_bucketfields
		#default_bucketfields = iupartstable.default_bucketfields
		
		coldefs = iupartstable.coldefs
		bucketdefs = iupartstable.bucketdefs
		
		es_searcher = ES_Searcher(search_params = self.search_params, user_id = self.uid, users_project_ids = self.users_project_ids, restrict_to_users_projects = restrict_to_users_projects)
		es_searcher.setSourceFields(selected_sourcefields)
		es_searcher.setBucketFields(selected_bucketfields)
		docs, maxpage, resultnum = es_searcher.paginatedSearch()
		#aggregations = es_searcher.getParsedAggregations()
		#iupartslist = iupartstable.getRowContent(doc_sources = [doc['_source'] for doc in docs])
		
		# set the coldefs for each iupart as keys for the json dicts 
		iuparts = []
		for doc in docs:
			iupartdict = {
				'_id': doc['_id']
			}
			
			for key in ['_score', '_ignored']:
				if key in doc:
					iupartdict[key] = doc[key]
			
			for colkey in selected_sourcefields:
				if colkey in doc['_source']:
					iupartdict[colkey] = doc['_source'][colkey]
			
			iuparts.append(iupartdict)
		
		jsoncontent = {
			'title': 'API for requests on DiversityCollection database',
			'maxpage': maxpage,
			'resultnum': resultnum,
			'page': int(self.search_params.get('page', 1)),
			'pagesize': int(self.search_params.get('pagesize', 1000)),
			'search_params': self.search_params,
			'iuparts': iuparts,
			#'aggregations': aggregations,
			'messages': self.messages
		}
		
		return jsoncontent


	@view_config(route_name='iupartslist', accept='text/html', renderer="DCRequestAPI:templates/iupartslist.pt")
	def IUPartsListHTML(self):
		
		iupartstable = IUPartsTable()
		if len(self.search_params['result_table_columns']) > 0:
			iupartstable.setSelectedSourceFields(self.search_params['result_table_columns'])
		
		restrict_to_users_projects = False
		if 'restrict_to_users_projects' in self.search_params and self.uid is not None:
			restrict_to_users_projects = True
		
		selected_sourcefields = iupartstable.selected_sourcefields
		default_sourcefields = iupartstable.default_sourcefields
		selected_bucketfields = iupartstable.selected_bucketfields
		default_bucketfields = iupartstable.default_bucketfields
		
		coldefs = iupartstable.coldefs
		bucketdefs = iupartstable.bucketdefs
		
		
		es_searcher = ES_Searcher(search_params = self.search_params, user_id = self.uid, users_project_ids = self.users_project_ids, restrict_to_users_projects = restrict_to_users_projects)
		es_searcher.setSourceFields(selected_sourcefields)
		es_searcher.setBucketFields(selected_bucketfields)
		docs, maxpage, resultnum = es_searcher.paginatedSearch()
		aggregations = es_searcher.getParsedAggregations()
		iupartslist = iupartstable.getRowContent(doc_sources = [doc['_source'] for doc in docs])
		
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
			'bucketdefs': bucketdefs,
			'default_sourcefields': default_sourcefields,
			'selected_sourcefields': selected_sourcefields, 
			'default_bucketfields': default_bucketfields,
			'selected_bucketfields': selected_bucketfields, 
			'open_filter_selectors': self.search_params['open_filter_selectors'],
			'authenticated_user': self.uid,
			'messages': self.messages
		}
		return pagecontent





