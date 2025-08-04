from pyramid.response import Response
from pyramid.renderers import render_to_response
from pyramid.view import (view_config, view_defaults)
from pyramid.httpexceptions import HTTPFound, HTTPNotFound, HTTPSeeOther

from ElasticSearch.ES_Searcher import ES_Searcher

from DCRequestAPI.lib.SearchResults.IUPartsTable import IUPartsTable
from DCRequestAPI.lib.SearchResults.HierarchyAggregations import HierarchyAggregations
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
		iupartstable = IUPartsTable()
		if len(self.search_params['result_table_columns']) > 0:
			iupartstable.setSelectedSourceFields(self.search_params['result_table_columns'])
		
		#if len(self.search_params['open_filter_selectors']) > 0:
		iupartstable.setSelectedBucketFields(self.search_params['open_filter_selectors'])
		iupartstable.setSelectedFilterSections(self.search_params['selected_filter_sections'])
		
		selected_sourcefields = iupartstable.selected_sourcefields
		default_sourcefields = iupartstable.default_sourcefields
		selected_bucketfields = iupartstable.selected_bucketfields
		all_bucketfields = iupartstable.bucketfields
		selected_filter_sections = iupartstable.selected_filter_sections
		stacked_query_fields = iupartstable.stacked_query_fields
		hierarchy_filter_fields = iupartstable.hierarchy_query_fields
		datefields = iupartstable.date_fields
		selected_datefields = []
		
		open_filter_selectors = self.search_params['open_filter_selectors']
		open_hierarchy_selectors = self.search_params['open_hierarchy_selectors']
		
		hierarchy_pathes_dict = self.search_params['hierarchies']
		
		#for hierarchy_field in self.search_params['hierarchies']:
		#	if hierarchy_field not in open_hierarchy_selectors:
		#		open_hierarchy_selectors.append(hierarchy_field)
		
		self.search_params['term_filters'] = self.reduce_hierarchical_term_filters(self.search_params['term_filters'], hierarchy_filter_fields)
		
		# the selected_bucketfields contain only the fields found in self.search_params['open_filter_selectors']
		# the fields from self.search_params['term_filters'] must be added, otherwise their results are not mentioned when their filter selector is not opened
		
		for term_filter_field in self.search_params['term_filters']:
			if term_filter_field in all_bucketfields and term_filter_field not in datefields and term_filter_field not in selected_bucketfields:
				selected_bucketfields.append(term_filter_field)
			if term_filter_field in all_bucketfields and term_filter_field in datefields and term_filter_field not in selected_datefields:
				selected_datefields.append(term_filter_field)
			if term_filter_field in hierarchy_filter_fields:
				if term_filter_field not in open_hierarchy_selectors:
					open_hierarchy_selectors.append(term_filter_field)
				if term_filter_field not in hierarchy_pathes_dict:
					hierarchy_pathes_dict[term_filter_field] = []
				for path in self.search_params['term_filters'][term_filter_field]:
					if path not in hierarchy_pathes_dict[term_filter_field]:
						hierarchy_pathes_dict[term_filter_field].append(path)
		
		# add the opened_filter_selectors to the selected filtersections
		# which here also includes the fields from the applied filters in self.search_params['term_filters']
		# because they are in selected_bucketfields
		# order the fields by all_bucketfields
		sorted_filter_sections = []
		
		for bucketfield in all_bucketfields:
			if bucketfield in selected_bucketfields or bucketfield in selected_datefields or bucketfield in selected_filter_sections:
				sorted_filter_sections.append(bucketfield)
			if (bucketfield in selected_bucketfields or bucketfield in selected_datefields) and bucketfield not in open_filter_selectors:
				open_filter_selectors.append(bucketfield)
		selected_filter_sections = sorted_filter_sections
		
		coldefs = iupartstable.coldefs
		bucketdefs = iupartstable.bucketdefs
		hierarchy_filter_names = iupartstable.hierarchy_filter_names
		
		es_searcher = ES_Searcher(search_params = self.search_params, user_id = self.uid, users_project_ids = self.users_project_ids)
		es_searcher.setSourceFields(selected_sourcefields)
		es_searcher.setBucketFields(selected_bucketfields)
		es_searcher.setDateFields(selected_datefields)
		es_searcher.setHierarchyFields(open_hierarchy_selectors)
		
		es_searcher.setHierarchyPathesDict(hierarchy_pathes_dict)
		
		docs, maxpage, resultnum = es_searcher.paginatedSearch()
		aggregations = es_searcher.getParsedAggregations()
		
		hierarchies_dict = HierarchyAggregations(aggregations).calcHierarchiesDict()
		
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
			'hierarchies_dict': hierarchies_dict,
			'coldefs': coldefs,
			'bucketdefs': bucketdefs,
			'hierarchy_filter_names': hierarchy_filter_names,
			'default_sourcefields': default_sourcefields,
			'selected_sourcefields': selected_sourcefields,
			'all_bucketfields': all_bucketfields,
			'selected_bucketfields': selected_bucketfields,
			'open_filter_selectors': open_filter_selectors,
			'selected_filter_sections': selected_filter_sections,
			'stacked_query_fields': stacked_query_fields,
			'hierarchy_filter_fields': hierarchy_filter_fields,
			'open_hierarchy_selectors': open_hierarchy_selectors,
			'hierarchy_pathes_dict': hierarchy_pathes_dict,
			'authenticated_user': self.uid,
			'messages': self.messages
		}
		return pagecontent


	def reduce_hierarchical_term_filters(self, term_filters, hierarchy_filter_fields):
		# when term_filters that are used with hierarchies filter out the term_filters that are parents of other term_filters
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
	
	
