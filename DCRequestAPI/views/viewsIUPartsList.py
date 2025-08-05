from pyramid.response import Response
from pyramid.renderers import render_to_response
from pyramid.view import (view_config, view_defaults)
from pyramid.httpexceptions import HTTPFound, HTTPNotFound, HTTPSeeOther


from ElasticSearch.FieldConfig import FieldConfig
from ElasticSearch.ES_Searcher import ES_Searcher

from DCRequestAPI.lib.SearchResults.IUPartsTable import IUPartsTable
from DCRequestAPI.lib.SearchResults.HierarchyAggregations import HierarchyAggregations
from DCRequestAPI.lib.UserLogin.UserLogin import UserLogin

from DCRequestAPI.views.RequestParams import RequestParams
from DCRequestAPI.lib.SearchResults.FieldParameterSetter import FieldParameterSetter


import pudb
import json



class IUPartsListView():
	def __init__(self, request):
		pudb.set_trace()
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
		
		self.fieldconfig = FieldConfig()
		
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
		iupartstable.setSelectedSourceFields(self.search_params['result_table_columns'])
		
		# makes no sense here
		#if len(self.search_params['open_filter_selectors']) > 0:
		#	iupartstable.setSelectedBucketFields(self.search_params['open_filter_selectors'])
				
		selected_sourcefields = iupartstable.selected_sourcefields
		selected_bucketfields = iupartstable.selected_bucketfields
		
		coldefs = iupartstable.coldefs
		bucketdefs = iupartstable.bucketdefs
		
		es_searcher = ES_Searcher(search_params = self.search_params, user_id = self.uid, users_project_ids = self.users_project_ids)
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
		pudb.set_trace()
		
		field_lists = FieldParameterSetter()
		
		# -> columns in table = field_lists.selected_sourcefields, field_lists.fallback result_fields
		field_lists.setSelectedSourceFields(self.search_params['result_table_columns'])
		# -> filters opened in filter box
		field_lists.setSelectedFilterFields(self.search_params['open_filter_selectors'])
		# -> add all fields from self.search_params['open_filter_selectors']
		field_lists.appendSelectedFilterFields(self.search_params['term_filters'])
		# -> filters shown in filter box, can be selected by user, fallback default_filter_sections, must be extended by selected_filter_fields
		field_lists.setSelectedFilterSections(self.search_params['selected_filter_sections'])
		
		
		# -> fields for the hierarchy filter
		hierarchy_filter_fields = field_lists.hierarchy_filter_fields
		
		column_names = self.fieldconfig.getColNames()
		term_filter_names = self.fieldconfig.getTermFilterNames()
		hierarchy_filter_names = self.fieldconfig.getHierarchyFilterNames()
		
		
		########################
		
		open_hierarchy_selectors = self.search_params['open_hierarchy_selectors']
		hierarchy_pathes_dict = self.search_params['hierarchies']
		
		
		#bucketdefs = iupartstable.bucketdefs
		#hierarchy_filter_names = iupartstable.hierarchy_filter_names
		
		
		es_searcher = ES_Searcher(search_params = self.search_params, user_id = self.uid, users_project_ids = self.users_project_ids)
		es_searcher.setSourceFields(field_lists.selected_sourcefields)
		es_searcher.setBucketFields(field_lists.selected_term_fields)
		es_searcher.setDateFields(field_lists.selected_date_fields)
		es_searcher.setHierarchyFields(open_hierarchy_selectors)
		
		es_searcher.setHierarchyPathesDict(hierarchy_pathes_dict)
		
		docs, maxpage, resultnum = es_searcher.paginatedSearch()
		aggregations = es_searcher.getParsedAggregations()
		
		hierarchies_dict = HierarchyAggregations(aggregations).calcHierarchiesDict()
		pudb.set_trace()
		doc_sources = [doc['_source'] for doc in docs]
		
		iupartstable = IUPartsTable(field_lists.selected_sourcefields)
		iupartslist = iupartstable.getRowContent(doc_sources = doc_sources)
		
		pagecontent = {
			'pagetitle': 'LIB collections cataloque',
			# parameters from the request
			'request': self.request,
			'maxpage': maxpage,
			'resultnum': resultnum,
			'page': int(self.search_params.get('page', 1)),
			'pagesize': int(self.search_params.get('pagesize', 1000)),
			'requestparamsstring': self.requeststring,
			'search_params': self.search_params,
			# the ES request ressults
			'iupartslist': iupartslist,
			'aggregations': aggregations,
			'hierarchies_dict': hierarchies_dict,
			# dicts for the names of the fields shown in interface
			'coldefs': column_names,
			'bucketdefs': term_filter_names,
			'hierarchy_filter_names': hierarchy_filter_names,
			# the fields for the user interface
			'default_sourcefields': field_lists.result_fields,
			'selected_sourcefields': field_lists.selected_sourcefields,
			'available_filter_fields': field_lists.available_filter_fields,
			'selected_filter_fields': field_lists.selected_filter_fields,
			'open_filter_selectors': field_lists.selected_filter_fields,
			'selected_filter_sections': field_lists.selected_filter_sections,
			'stacked_query_fields': field_lists.stacked_query_fields,
			'hierarchy_filter_fields': hierarchy_filter_fields,
			'open_hierarchy_selectors': open_hierarchy_selectors,
			'hierarchy_pathes_dict': hierarchy_pathes_dict,
			# authentication
			'authenticated_user': self.uid,
			'messages': self.messages
		}
		pudb.set_trace()
		return pagecontent


	def reduce_hierarchical_term_filters(self, term_filters, hierarchy_filter_fields):
		# when term_filters are used with hierarchies
		# filter out the term_filters that are parents of other term_filters
		# to have a specific search
		new_term_filters = {}
		for key in term_filters:
			if key in hierarchy_filter_fields:
				
				filter_dict = {}
				
				for filter_entry in term_filters[key]:
					element_list = [element.strip() for element in filter_entry.split('>')]
					self.set_reduced_hierarchy_dict(filter_dict, element_list)
				
				self.reduced_hierarchy_pathes = []
				self.set_reduced_hierarchy_pathes(filter_dict)
				
				if len(self.reduced_hierarchy_pathes) > 0:
					new_term_filters[key] = []
					for hierarchy_path in self.reduced_hierarchy_pathes:
						new_term_filters[key].append('>'.join(hierarchy_path))
				
			else:
				new_term_filters[key] = term_filters[key]
		
		return new_term_filters


	def set_reduced_hierarchy_dict(self, subdict, element_list):
		if len(element_list) <= 0:
			return
		element = element_list.pop(0)
		if element in subdict.keys():
			self.set_reduced_hierarchy_dict(subdict[element], element_list)
		else:
			subdict[element] = {}
			self.set_reduced_hierarchy_dict(subdict[element], element_list)
		return


	def set_reduced_hierarchy_pathes(self, sub_dict, path = None):
		if path is None:
			path = []
		for key in sub_dict:
			if isinstance(sub_dict[key], dict) and len(sub_dict[key]) > 0:
				path.append(key)
				self.set_reduced_hierarchy_pathes(sub_dict[key], path)
			elif isinstance(sub_dict[key], dict) and len(sub_dict[key]) <= 0:
				path.append(key)
				self.reduced_hierarchy_pathes.append(path)
				return
		return
	
	
