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

import pudb
import json


class AggregationView():
	def __init__(self, request):
		self.request = request
		self.uid = self.request.authenticated_userid
		
		self.roles = self.request.identity['dwb_roles']
		self.users_projects = self.request.identity['projects']
		self.users_project_ids = [project[0] for project in self.users_projects]
		pudb.set_trace()
		self.userlogin = UserLogin(self.request)
		
		self.messages = []
		
		if 'username' in self.request.params:
			self.userlogin.authenticate_user()
			self.uid, self.roles, self.users_projects, self.users_project_ids = self.userlogin.get_identity()
		
		elif 'token' in self.request.params:
			self.userlogin.authenticate_by_token(self.request.params['token'])
			self.uid, self.roles, self.users_projects, self.users_project_ids = self.userlogin.get_identity()
		
		self.messages.extend(self.userlogin.get_messages())


	@view_config(route_name='aggregation', accept='application/json', renderer="json")
	def viewAggregationJSON(self):
		
		#pudb.set_trace()
		
		self.search_params = RequestParams().get_search_params(self.request)
		
		# remove aggregation from term filters to get all buckets in this aggregation
		# but keep all other search params?
		# that might be confusing for users
		
		if 'aggregation' in self.search_params:
			agg_name = self.search_params['aggregation']
			if agg_name in self.search_params['term_filters']:
				del self.search_params['term_filters'][agg_name]
		
		es_searcher = ES_Searcher(search_params = self.search_params, user_id = self.uid, users_project_ids = self.users_project_ids)
		buckets = es_searcher.singleAggregationSearch(agg_name)
		
		pagecontent = {
			agg_name: buckets,
		}
		
		return pagecontent

