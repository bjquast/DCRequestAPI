import pudb

from configparser import ConfigParser

from DBConnectors.MSSQLConnector import MSSQLConnectionParams

'''
Keep this class within DCDataGetters as it reads user and password from config.ini and should only be used for indexing with credentials that allow to read all data
'''


class DC_Connections():
	def __init__(self):
		self.config = ConfigParser(allow_no_value=True)
		self.config.read('./config.ini')
		
		self.databases = []


	def read_connectionparams(self):
		sections = self.config.sections()
		for section in sections:
			if section[:12]=='data_source_' and section!='data_source_test' and len(section[12:]) > 0:
				database_id = section[12:]
				accronym = self.config.get(section, 'accronym', fallback = section[12:])
				server = self.config.get(section, 'server', fallback = None)
				port = self.config.get(section, 'port', fallback = None)
				database_name = self.config.get(section, 'database', fallback = None)
				uid = self.config.get(section, 'uid', fallback = None)
				password = self.config.get(section, 'password', fallback = None)
				driver = self.config.get(section, 'driver', fallback = None)
				trust_certificate = self.config.get(section, 'trust_certificate', fallback = None)
				trusted_connection = self.config.get(section, 'trusted_connection', fallback = None)
				encrypt = self.config.get(section, 'encrypt', fallback = None)
				project_section = self.config.get(section, 'project_db_connector', fallback = None)
				
				if project_section is not None:
					self.read_projects_connectionparams(project_section)
				else:
					self.projects_connectionstring = None
				
				mssql_params = MSSQLConnectionParams(server = server, port = port, database = database_name, uid = uid, pwd = password, driver = driver, trust_certificate = trust_certificate, trusted_connection = trusted_connection, encrypt = encrypt)
				connectionstring = mssql_params.getConnectionString()
				
				database_params = {
					'connectionstring': connectionstring,
					'server_url': server,
					'database_name': database_name,
					'accronym': accronym,
					'database_id': database_id,
					'projects_connectionstring': self.projects_connectionstring
				}
				
				self.databases.append(database_params)
		return


	def read_projects_connectionparams(self, project_section):
		"""
		DiversityProjects Database connection for Embargo setting. This is a LIB specific idea? Would it be usefull over the time?
		"""
		sections = self.config.sections()
		for section in sections:
			if section == project_section:
				server = self.config.get(section, 'server', fallback = None)
				port = self.config.get(section, 'port', fallback = None)
				database_name = self.config.get(section, 'database', fallback = None)
				uid = self.config.get(section, 'uid', fallback = None)
				password = self.config.get(section, 'password', fallback = None)
				driver = self.config.get(section, 'driver', fallback = None)
				trust_certificate = self.config.get(section, 'trust_certificate', fallback = None)
				trusted_connection = self.config.get(section, 'trusted_connection', fallback = None)
				encrypt = self.config.get(section, 'encrypt', fallback = None)
				
				try:
					projects_db_params = MSSQLConnectionParams(server = server, port = port, database = database_name, uid = uid, pwd = password, driver = driver, trust_certificate = trust_certificate, trusted_connection = trusted_connection, encrypt = encrypt)
					self.projects_connectionstring = projects_db_params.getConnectionString()
				except ValueError:
					self.projects_connectionstring = None
		
		
