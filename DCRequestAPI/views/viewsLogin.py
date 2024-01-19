from pyramid.response import Response
from pyramid.view import view_config, forbidden_view_config
from pyramid.renderers import render
from pyramid.httpexceptions import HTTPFound, HTTPNotFound, HTTPSeeOther

from dwb_authentication.security import SecurityPolicy
from dwb_authentication.DWB_Servers import DWB_Servers

from DCRequestAPI.lib.UserLogin.UserLogin import UserLogin

#from pyramid.security import remember, forget

import pudb
import re


class LoginViews(object):
	'''
	copied from https://docs.pylonsproject.org/projects/pyramid/en/latest/quick_tutorial/authentication.html
	'''

	def __init__(self, request):
		self.request = request
		
		self.uid = self.request.authenticated_userid
		
		self.userlogin = UserLogin(self.request)
		
		self.dwb_servers = DWB_Servers()
		self.available_dwb_cons = self.dwb_servers.get_available_dwb_cons()
		
		self.messages = []


	@view_config(route_name='login', accept='text/html')
	@forbidden_view_config(accept='text/html')
	def login_view(self):
		
		#pudb.set_trace()
		
		login_url = self.request.route_url('login')
		referrer = self.request.url
		if referrer == login_url:
			referrer = self.request.route_url('iupartslist') # never use login form itself as came_from
		came_from = self.request.params.get('came_from', referrer)
		
		self.token = None
		
		if 'form.submitted' in self.request.params:
			
			self.loginparams = self.userlogin.get_login_params()
			if len(self.loginparams) > 0:
				self.token = self.userlogin.authenticate_user(self.loginparams)
				#self.uid, self.roles, self.users_projects, self.users_project_ids = self.userlogin.get_identity()
			
			if self.token is not None:
				return HTTPFound(location=came_from)
			
			else:
				self.messages.insert(0, 'Login failed, please check your credentials')
		
		responsedict = dict(
			name='Login',
			messages = self.messages,
			url = self.request.application_url + '/login',
			came_from = came_from,
			username = self.loginparams.get('username', None),
			#password= self.password,
			request = self.request,
			available_dwb_cons = self.available_dwb_cons,
			current_dwb_con = self.loginparams.get('db_accronym', None)
		)
		
		result = render('DCRequestAPI:templates/login.pt', responsedict)
		response = Response(result)
		return response
	
	
	@view_config(route_name='logout')
	def logout_view(self):
		#pudb.set_trace()
		logout_url = self.request.route_url('logout')
		referrer = self.request.url
		if referrer == logout_url:
			referrer = self.request.route_url('iupartslist') # never use login form itself as came_from
		came_from = self.request.params.get('came_from', referrer)
		
		#headers = forget(self.request)
		self.request.session['token'] = None
		return HTTPFound(location = came_from)


	'''
	@view_config(route_name='authenticated_user', renderer='json')
	def authenticated_user_view(self):
		if self.request.params.get('token', ''):
			security = SecurityPolicy()
			identity = security.get_identity_by_token(self.request)
			if identity is not None:
				return identity
			else:
				return {}
		else:
			return {}
	'''
	








