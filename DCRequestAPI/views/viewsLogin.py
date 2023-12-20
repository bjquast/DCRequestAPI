from pyramid.response import Response
from pyramid.view import view_config, forbidden_view_config
from pyramid.renderers import render
from pyramid.httpexceptions import HTTPFound, HTTPNotFound, HTTPSeeOther

from dwb_authentication.security import SecurityPolicy
from dwb_authentication.dwb_server.DWB_Server import DWB_Server

#from pyramid.security import remember, forget

import pudb
import re


class LoginViews(object):
	'''
	copied from https://docs.pylonsproject.org/projects/pyramid/en/latest/quick_tutorial/authentication.html
	'''

	def __init__(self, request):
		self.request = request
		
		self.lang = 'en'
		self.uid = self.request.authenticated_userid
		
		self.message = None
		
		self.available_dwb_cons = DWB_Server().get_available_dwb_cons()
		self.dwb_connector = ''
		
		self.server = ''
		self.port = ''
		self.database = ''
		self.login = ''
		self.password = ''
	
	
	@view_config(route_name='login', accept='text/html')
	@forbidden_view_config(accept='text/html')
	def login_view(self):
		login_url = self.request.route_url('login')
		referrer = self.request.url
		if referrer == login_url:
			referrer = self.request.route_url('iupartslist') # never use login form itself as came_from
		came_from = self.request.params.get('came_from', referrer)
		self.message = None
		
		pudb.set_trace()
		
		if 'form.submitted' in self.request.params:
			self.read_form_input()
			
			if self.password == '' or self.password is None:
				messages = {
					'en': 'Please provide a password',
					'de': 'Bitte geben Sie ein Passwort ein'
				}
			
			elif self.password_not_pawned(self.password) is False:
				messages = {
					'en': 'Your password is not secure, please contact the administrator',
					'de': 'Ihr Passwort ist nicht sicher, bitte kontaktieren Sie den Administrator'
				}
				self.message = messages[self.lang]
			
			else:
				security = SecurityPolicy()
				token = security.validate_credentials(server = self.server, port = self.port, database = self.database, username = self.login, password = self.password)
				
				if token is not None:
					self.request.session['token'] = token
					#headers = remember(self.request, login)
					return HTTPFound(location=came_from)
				
				else:
					messages = {
						'en': 'Login failed, please check your credentials',
						'de': 'Login gescheitert, bitte überprüfen Sie Nutzername und Passwort'
					}
					self.message = messages[self.lang]
					
					#pass
		
		responsedict = dict(
			name='Login',
			message = self.message,
			url = self.request.application_url + '/login',
			came_from = came_from,
			login = self.login,
			password= self.password,
			server = self.server,
			port = self.port,
			database = self.database,
			request = self.request,
			available_dwb_cons = self.available_dwb_cons,
			current_dwb_con = self.dwb_connector
		)
		
		result = render('DCRequestAPI:templates/login.pt', responsedict)
		response = Response(result)
		return response
	
	
	@view_config(route_name='logout')
	def logout_view(self):
		
		#headers = forget(self.request)
		self.request.session['token'] = None
		url = self.request.route_url('select_table')
		return HTTPFound(location=url)


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
	


	'''
	check against https://haveibeenpwned.com disallow pawned passwords
	code from:
	https://pwcheck.gwdg.de/api.html
	with usage of haveibeenpwned.com API
	https://haveibeenpwned.com/API/v2#SearchingPwnedPasswordsByRange
	'''
	def password_not_pawned(self, password):
		
		import hashlib, urllib.request
		
		pwhash = hashlib.sha1(password.encode('utf8')).hexdigest().upper()
		prefix = pwhash[:5]
		suffix = pwhash[5:]
		
		unknown_password = False
		
		url = "https://api.pwnedpasswords.com/range/" + prefix
		with urllib.request.urlopen(url) as response:
			unknown_password = True
			for line in response.read().splitlines():
				line = line.decode('ASCII')
				if line.startswith(suffix):
					return False
					#print("Bad password!", "Score:", line.split(':')[-1])
		return unknown_password


	def read_form_input(self):
		self.serverpattern = re.compile(r'(^[^\:]+)\:')
		self.portpattern = re.compile(r'\:(\d{2,5})\:')
		self.dbpattern = re.compile(r'\:([^\:]+)$')
		
		self.login = self.request.params.get('login', '')
		self.password = self.request.params.get('password', '')
			
		self.server = self.request.params.get('server', '')
		self.port = self.request.params.get('port', '')
		self.database = self.request.params.get('database', '')
		
		self.dwb_connector = self.request.params.get('dwb_connector', '')
		
		if self.server == '':
			if self.dwb_connector != '':
				m = self.serverpattern.search(self.dwb_connector)
				if m is not None:
					self.server = m.group(1)
		
		if self.port == '':
			if self.dwb_connector != '':
				m = self.portpattern.search(self.dwb_connector)
				if m is not None:
					self.port = m.group(1)
		
		if self.database == '':
			if self.dwb_connector != '':
				m = self.dbpattern.search(self.dwb_connector)
				if m is not None:
					self.database = m.group(1)
		
		# a little prevention against sql injection
		if ';' in self.server:
			self.server = None
		
		if ';' in self.database:
			self.database = None
		
		try:
			self.port = int(self.port)
		except ValueError:
			self.port = None
		
		



