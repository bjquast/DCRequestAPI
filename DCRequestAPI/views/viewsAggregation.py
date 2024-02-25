import logging
log = logging.getLogger(__name__)

from pyramid.response import Response
from pyramid.renderers import render_to_response
from pyramid.view import (view_config, view_defaults)
from pyramid.httpexceptions import HTTPFound, HTTPNotFound, HTTPSeeOther

from ElasticSearch.ES_Searcher import ES_Searcher

from DCRequestAPI.lib.UserLogin.UserLogin import UserLogin
from dwb_authentication.DWB_Servers import DWB_Servers

from DCRequestAPI.views.RequestParams import RequestParams

from ElasticSearch.FieldDefinitions import FieldDefinitions

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
		
		self.fielddefinitions = FieldDefinitions().fielddefinitions


	@view_config(route_name='aggregation', accept='application/json', renderer="json")
	def viewAggregationJSON(self):
		
		#pudb.set_trace()
		
		# remove aggregation from term filters to get all buckets in this aggregation
		# but keep all other search params?
		# that might be confusing for users
		
		if 'aggregation' in self.search_params:
			agg_key = self.search_params['aggregation']
			#if agg_key in self.search_params['term_filters']:
			#	del self.search_params['term_filters'][agg_key]
		
		if agg_key not in self.fielddefinitions:
			return {
				'message': '{0} can is not available as bucket aggregation'.format(agg_key),
				'buckets': {}
			}
		
		es_searcher = ES_Searcher(search_params = self.search_params, user_id = self.uid, users_project_ids = self.users_project_ids)
		buckets = es_searcher.singleAggregationSearch(agg_key)
		
		
		
		buckets_dict = {
			'aggregation': agg_key,
			'aggregation_names': self.fielddefinitions[agg_key].get('names', {'en', None}),
			'buckets': buckets
		}
		
		return buckets_dict

