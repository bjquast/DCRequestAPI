from pyramid.response import Response
from pyramid.renderers import render_to_response
from pyramid.view import (view_config, view_defaults)
from pyramid.httpexceptions import HTTPFound, HTTPNotFound, HTTPSeeOther

from DCRequestAPI.lib.UserLogin.UserLogin import UserLogin
from dwb_authentication.DWB_Servers import DWB_Servers

from ElasticSearch.ES_Searcher import ES_Searcher

from DCRequestAPI.views.RequestParams import RequestParams
from DCRequestAPI.lib.SearchResults.HierarchyAggregations import HierarchyAggregations
from ElasticSearch.FieldDefinitions import FieldDefinitions


import pudb
import json


class HierarchiesView():
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
		
		fielddefs = FieldDefinitions()
		self.fielddefinitions = fielddefs.fielddefinitions
		self.hierarchy_query_fields = fielddefs.hierarchy_query_fields
		self.hierarchy_filter_names = fielddefs.getHierarchyFilterNames()
		


	'''
	@view_config(route_name='hierarchy_aggregation', accept='application/json', renderer="json")
	def viewHierarchyAggregationJSON(self):
		
		if 'hierarchies' not in self.search_params or len(self.search_params['hierarchies']) <= 0:
			return {
				'message': 'parameter hierarchies=hierarchy_name:path is missing',
				'buckets': {}
			}
		
		hierarchy_name = self.request.matchdict['hierarchy_name']
		
		if hierarchy_name not in self.search_params['hierarchies']:
			return {
				'message': 'hierarchy name {0} can not be found in parameters'.format(hierarchy_name),
				'buckets': {}
			}
		
		if not (isinstance(self.search_params['hierarchies'][hierarchy_name], tuple) or isinstance(self.search_params['hierarchies'][hierarchy_name], list)):
				return {
					'message': '{0} parameter contains no hierarchy:path parameter'.format(hierarchy_name),
					'buckets': {}
				}
		
		es_searcher = ES_Searcher(search_params = self.search_params, user_id = self.uid, users_project_ids = self.users_project_ids)
		buckets = es_searcher.singleHierarchyAggregationSearch(hierarchy_name, self.search_params['hierarchies'])
		
		buckets_dict = {
			'aggregation': hierarchy_name,
			'aggregation_names': self.fielddefinitions[hierarchy_name].get('names', {'en', None}),
			'buckets': buckets
		}
		
		return buckets_dict
	'''


	@view_config(route_name='hierarchies', accept='text/html', renderer="DCRequestAPI:templates/hierarchy_filters_macro.pt")
	def viewHierarchiesHTML(self):
		
		hierarchy_pathes_dict = self.search_params['hierarchies']
		
		open_hierarchy_selectors = self.search_params['open_hierarchy_selectors']
		for hierarchy_field in self.search_params['hierarchies']:
			if hierarchy_field not in open_hierarchy_selectors:
				open_hierarchy_selectors.append(hierarchy_field)
		
		for term_filter_field in self.search_params['term_filters']:
			if term_filter_field in self.hierarchy_query_fields:
				if term_filter_field not in open_hierarchy_selectors:
					open_hierarchy_selectors.append(term_filter_field)
				if term_filter_field not in hierarchy_pathes_dict:
					hierarchy_pathes_dict[term_filter_field] = []
				for path in self.search_params['term_filters'][term_filter_field]:
					if path not in hierarchy_pathes_dict[term_filter_field]:
						hierarchy_pathes_dict[term_filter_field].append(path)
		
		
		es_searcher = ES_Searcher(search_params = self.search_params, user_id = self.uid, users_project_ids = self.users_project_ids)
		buckets = es_searcher.searchHierarchyAggregations(hierarchy_pathes_dict, source_fields = open_hierarchy_selectors)
		
		hierarchies_dict = HierarchyAggregations(buckets).calcHierarchiesDict()
		
		for key in hierarchies_dict:
			if key not in open_hierarchy_selectors:
				open_hierarchy_selectors.append(key)
		
		response_dict = {
			'hierarchy_pathes_dict': hierarchy_pathes_dict,
			'hierarchy_filter_fields': self.hierarchy_query_fields,
			'hierarchies_dict': hierarchies_dict,
			'open_hierarchy_selectors': open_hierarchy_selectors,
			'hierarchy_filter_names': self.hierarchy_filter_names
		}
		
		return response_dict


	@view_config(route_name='hierarchy_remove_path', accept='text/html', renderer="DCRequestAPI:templates/hierarchy_filters_macro.pt")
	def viewRemovePathFromHierarchyHTML(self):
		
		hierarchy_name = self.request.matchdict['hierarchy_name']
		
		path_to_remove = self.search_params['path_to_remove']
		hierarchy_pathes_dict = self.search_params['hierarchies']
		
		if hierarchy_name in hierarchy_pathes_dict:
			new_pathes_list = []
			for path in hierarchy_pathes_dict[hierarchy_name]:
				if path.startswith(path_to_remove):
					pass
				else:
					new_pathes_list.append(path)
			hierarchy_pathes_dict[hierarchy_name] = new_pathes_list
			
		
		open_hierarchy_selectors = self.search_params['open_hierarchy_selectors']
		for hierarchy_field in self.search_params['hierarchies']:
			if hierarchy_field not in open_hierarchy_selectors:
				open_hierarchy_selectors.append(hierarchy_field)
		
		for term_filter_field in self.search_params['term_filters']:
			if term_filter_field in self.hierarchy_query_fields:
				if term_filter_field not in open_hierarchy_selectors:
					open_hierarchy_selectors.append(term_filter_field)
				if term_filter_field not in hierarchy_pathes_dict:
					hierarchy_pathes_dict[term_filter_field] = []
				for path in self.search_params['term_filters'][term_filter_field]:
					if path not in hierarchy_pathes_dict[term_filter_field]:
						hierarchy_pathes_dict[term_filter_field].append(path)
		
		
		es_searcher = ES_Searcher(search_params = self.search_params, user_id = self.uid, users_project_ids = self.users_project_ids)
		buckets = es_searcher.searchHierarchyAggregations(hierarchy_pathes_dict, source_fields = open_hierarchy_selectors)
		
		hierarchies_dict = HierarchyAggregations(buckets).calcHierarchiesDict()
		
		for key in hierarchies_dict:
			if key not in open_hierarchy_selectors:
				open_hierarchy_selectors.append(key)
		
		response_dict = {
			'hierarchy_pathes_dict': hierarchy_pathes_dict,
			'hierarchy_filter_fields': self.hierarchy_query_fields,
			'hierarchies_dict': hierarchies_dict,
			'open_hierarchy_selectors': open_hierarchy_selectors,
			'hierarchy_filter_names': self.hierarchy_filter_names
		}
		
		return response_dict


