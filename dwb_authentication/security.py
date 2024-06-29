import pudb


from dwb_authentication.dbsession import DBSession


class SecurityPolicy:
	def __init__(self):
		self.messages = []
		pass


	def validate_credentials(self, username = None, password = None):
		'''
		# this is for the first login, when no token is available
		# try to connect with credentials, if successful create new session
		# return username as authenticated_userid
		'''
		
		dbsession = DBSession()
		
		# dbsession.set_session() checks if connection params are valid and returns None if they are not valid
		token = dbsession.set_session(username, password)
		return token


	def de_authenticate(self, request):
		dbsession = DBSession()
		
		session_id = None
		
		token = self.get_token_from_request(request)
		if token is not None:
			session_id = dbsession.get_session_id_by_token(token)
			if session_id is not None:
				dbsession.delete_session_by_token(token)
		
		# even if the session token has not been found de-authenticate
		# because it might be called from html form and the user expects to be logged of now
		self.reset_authenticated_identity()
		return session_id


	def get_identity_by_token(self, request):
		
		dbsession = DBSession()
		
		token = self.get_token_from_request(request)
		if token is not None:
			identity = dbsession.get_identity_by_token(token)
			if identity is not None:
				hashed_token = dbsession.encryptor.hash_token(token)
				dbsession.update_expiration_time(hashed_token)
				return identity
		
		return 


	def authenticated_userid(self, request):
		# reset the authenticated_identity to ensure that it is checked whenever authenticated_userid is called
		# because the identity method takes a shortcut when it was set once
		# to prevent the repeated requests against session db
		self.reset_authenticated_identity()
		
		self.authenticated_identity = self.identity(request)
		return self.authenticated_identity['username']


	def identity(self, request):
		# when the user was authenticated via authenticated_userid method, take the shortcut to get roles and projects
		# prevent repeated requests against sessiondb to get these data via the token
		if self.authenticated_identity['username'] is not None:
			return self.authenticated_identity
		
		self.authenticated_identity = self.get_identity_by_token(request)
		if self.authenticated_identity is not None:
			return self.authenticated_identity
		else:
			self.reset_authenticated_identity()
		return self.authenticated_identity


	def reset_authenticated_identity(self):
		self.authenticated_identity = {
			'username': None,
			'dwb_roles': {},
			'projects': [],
		}


	def get_token_from_request(self, request):
		token = None
		if 'token' in request.session:
			token = request.session['token']
		elif 'token' in request.params:
			try:
				token = request.params.getone('token')
			except:
				token = None
		else:
			try:
				json_params = request.json_body
				if 'token' in json_params:
					if (isinstance (json_params['token'], str)):
						token = json_params['token']
			except:
				token = None
				
		return token




	'''
	def get_username_by_token(self, request):
		"""
		# return an authenticated_userid when there is a valid token
		"""
		
		dbsession = DBSession()
		
		token = self.get_token_from_request(request)
		if token is not None:
			identity = dbsession.get_identity_from_session(token)
			identity = dbsession.get_identity_from_session(token)
			if identity is not None:
				hashed_token = dbsession.encryptor.hash_token(token)
				dbsession.update_expiration_time(hashed_token)
				return identity['username']
		
		return None
	'''





