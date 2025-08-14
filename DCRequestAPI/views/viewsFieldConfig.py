from pyramid.response import Response
from pyramid.renderers import render_to_response
from pyramid.view import (view_config, view_defaults)
from pyramid.httpexceptions import HTTPFound, HTTPNotFound, HTTPBadRequest

from DCRequestAPI.lib.UserLogin.UserLogin import UserLogin
from ElasticSearch.FieldConfig import FieldConfig

from DCRequestAPI.views.RequestParams import RequestParams

import pudb
import json
from datetime import datetime


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


	@view_config(route_name='get_field_type', accept='application/json', renderer='json')
	def get_field_type(self):
		if 'fieldname' in self.request.matchdict:
			fieldname = self.request.matchdict['fieldname']
		else:
			return HTTPBadRequest(detail = 'Field name missing in request. Add field name to the end of the url: {0}/get_field_type/{fieldname}'.format(self.request.application_url))
		
		response = {
			'field_type': None
		}
		
		if fieldname in self.fieldconfig.date_fields:
			response['field_type'] = 'date'
		else:
			response['field_type'] = 'term'
		
		return response



