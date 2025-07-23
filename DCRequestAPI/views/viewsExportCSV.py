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
from datetime import datetime


class ExportCSVView():
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


	@view_config(route_name='export_csv', accept='application/json')
	def export_csv(self):
		pudb.set_trace()
		
		restrict_to_users_projects = False
		if 'restrict_to_users_projects' in self.search_params and self.uid is not None:
			restrict_to_users_projects = True
		
		csv_generator = CSVGenerator(self.search_params, self.uid, self.users_project_ids, restrict_to_users_projects)
		csv_generator.set_es_searcher()
		
		now = datetime.now().strftime("%d.%m.%Y-%H:%M:%S")
		filename = 'ZFMK_Catalog_Search_Results' + str(now) + ".csv"
		
		response = Response(content_type='application/csv')
		response.app_iter = csv_generator.yield_CSV_pages()
		response.headers['Content-Disposition'] = ("attachment; filename={0}".format(filename))
		return response
		
		
		





class CSVGenerator():
	def __init__(self, search_params, uid, users_project_ids, restrict_to_users_projects):
		self.search_params = search_params
		self.uid = uid
		self.users_project_ids = users_project_ids
		self.restrict_to_users_projects = restrict_to_users_projects
		
		self.maxpage = 0
		self.resultnum = 0
		self.pagesize = 1000
		self.page = 1
		
		self.iupartstable = IUPartsTable()
		if len(self.search_params['result_table_columns']) > 0:
			self.iupartstable.setSelectedSourceFields(self.search_params['result_table_columns'])
		self.selected_sourcefields = self.iupartstable.selected_sourcefields
		
	
	def set_es_searcher(self):
		self.es_searcher = ES_Searcher(search_params = self.search_params, user_id = self.uid, users_project_ids = self.users_project_ids, restrict_to_users_projects = self.restrict_to_users_projects)
		self.es_searcher.setSourceFields(self.selected_sourcefields)
		self.maxpage, self.resultnum = self.es_searcher.countResultDocsSearch()
		return
	
	def yield_CSV_pages(self):
		self.page = 1
		pudb.set_trace()
		while self.page <= self.maxpage:
			docs, maxpage, resultnum = self.es_searcher.searchDocsByPage(self.page)
			iupartslist = self.iupartstable.getRowContent(doc_sources = [doc['_source'] for doc in docs])
			
			self.page = self.page + 1
			csv_page = ''
			
			for iupart in iupartslist:
				csv_list = []
				for source_field in self.selected_sourcefields:
					if source_field in iupart:
						if isinstance(iupart[source_field], tuple) or isinstance(iupart[source_field], list):
							csv_list.append("'" + '; '.join([str(element) for element in iupart[source_field]]) + "'")
						elif iupart[source_field] is None:
							csv_list.append('')
						else:
							csv_list.append("'" + str(iupart[source_field]) + "'")
					else:
						csv_list.append('')
				csv_page += '\n' + ', '.join(csv_list)
			print (self.page, self.maxpage)
			yield bytes(csv_page, 'utf8')
		
		return 


