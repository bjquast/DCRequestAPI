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


class AggregationView():
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


	@view_config(route_name='aggregation', accept='application/json', renderer="json")
	def viewAggregationJSON(self):
		if 'buckets_search_term' in self.search_params:
			buckets_search_term = self.search_params['buckets_search_term']
		else:
			buckets_search_term = None
		
		if 'aggregation' in self.search_params:
			agg_key = self.search_params['aggregation']
		else:
			agg_key = None
		
		if 'buckets_sort_alphanum' in self.search_params:
			buckets_sort_alphanum = self.search_params['buckets_sort_alphanum']
		else:
			buckets_sort_alphanum = False
		
		if 'buckets_sort_dir' in self.search_params:
			buckets_sort_dir = self.search_params['buckets_sort_dir']
		else:
			buckets_sort_dir = None
		
		if 'buckets_size' in self.search_params:
			buckets_size = self.search_params['buckets_size']
		else:
			buckets_size = 5000
		
		if agg_key not in self.fielddefinitions:
			return {
				'message': '{0} is not available as bucket aggregation'.format(agg_key),
				'buckets': {}
			}
		
		es_searcher = ES_Searcher(search_params = self.search_params, user_id = self.uid, users_project_ids = self.users_project_ids)
		buckets = es_searcher.singleAggregationSearch(agg_key, buckets_search_term = buckets_search_term, buckets_sort_alphanum = buckets_sort_alphanum, buckets_sort_dir = buckets_sort_dir, size = buckets_size)
		
		
		
		buckets_dict = {
			'aggregation': agg_key,
			'aggregation_names': self.fielddefinitions[agg_key].get('names', {'en', None}),
			'buckets': buckets
		}
		
		return buckets_dict

