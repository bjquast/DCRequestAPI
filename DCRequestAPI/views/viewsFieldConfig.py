from pyramid.view import (view_config, view_defaults)
from pyramid.httpexceptions import HTTPFound, HTTPNotFound, HTTPBadRequest

from DCRequestAPI.lib.UserLogin.UserLogin import UserLogin
from ElasticSearch.FieldConfig import FieldConfig

from DCRequestAPI.views.RequestParams import RequestParams

import pudb

class FieldConfigView():
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
		
		self.fieldconfig = FieldConfig()
		self.messages.extend(self.userlogin.get_messages())


	@view_config(route_name='get_stacked_field_type', accept='application/json', renderer='json')
	def get_stacked_field_type(self):
		"""
		get the type of a field
		called by  DCRequestAPI/static/js/StackedSearch.js because
		the stacked search has to differentiate between date and term types
		"""
		
		fieldname = self.request.matchdict['fieldname']
		
		response = {
			'field_type': None
		}
		if fieldname in self.fieldconfig.stacked_query_fields and fieldname in self.fieldconfig.date_fields:
			response['field_type'] = 'date'
		elif fieldname in self.fieldconfig.stacked_query_fields and fieldname in self.fieldconfig.term_fields:
			response['field_type'] = 'term'
		else:
			return HTTPBadRequest(detail = 'Field {1} in {0}/get_stacked_field_type/{1} is not a valid field name\n Must be one of: {2}'.format(self.request.application_url, fieldname, ', '.join(self.fieldconfig.stacked_query_fields)))
		
		return response



