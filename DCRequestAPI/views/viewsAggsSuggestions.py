from pyramid.response import Response
from pyramid.renderers import render_to_response
from pyramid.view import (view_config, view_defaults)
from pyramid.httpexceptions import HTTPFound, HTTPNotFound, HTTPSeeOther

from ElasticSearch.ES_Searcher import ES_Searcher

from DCRequestAPI.lib.UserLogin.UserLogin import UserLogin
from dwb_authentication.DWB_Servers import DWB_Servers

from DCRequestAPI.views.RequestParams import RequestParams

from ElasticSearch.FieldConfig import FieldConfig

import pudb
import json


class AggsSuggestionsView():
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
		
		self.fielddefinitions = FieldConfig().fielddefinitions


	@view_config(route_name='aggs_suggestions', accept='application/json', renderer="json")
	def viewSuggestionsJSON(self):
		
		#pudb.set_trace()
		
		buckets = {}
		
		if 'buckets_search_term' in self.search_params:
			buckets_search_term = self.search_params['buckets_search_term']
			
			if 'buckets_sort_alphanum' in self.search_params:
				buckets_sort_alphanum = self.search_params['buckets_sort_alphanum']
			else:
				buckets_sort_alphanum = False
			
			if 'buckets_sort_dir' in self.search_params:
				buckets_sort_dir = self.search_params['buckets_sort_dir']
			else:
				buckets_sort_dir = 'asc'
			
			es_searcher = ES_Searcher(search_params = self.search_params, user_id = self.uid, users_project_ids = self.users_project_ids)
			buckets = es_searcher.suggestionsSearch(buckets_search_term, buckets_sort_alphanum = buckets_sort_alphanum, buckets_sort_dir = buckets_sort_dir)
			
			extended_buckets = {}
			for key in buckets:
				extended_buckets[key] = {}
				extended_buckets[key]['names'] = self.fielddefinitions[key]['names']
				extended_buckets[key]['buckets'] = buckets[key]
			
			buckets = extended_buckets
		
		suggestions_dict = {
			'buckets': buckets
		}
		
		return suggestions_dict

