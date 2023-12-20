import pudb

from dwb_authentication.mysql_connect import mysql_connect


class DWB_Server():
	def __init__(self):
		
		self.con, self.cur = mysql_connect()
	
	
	def get_available_servers(self):
		servers = []
		
		query = """
		SELECT `server`, `port`, `database`
		FROM `mssql_connectors`
		;"""
		
		self.cur.execute(query)
		rows = self.cur.fetchall()
		for row in rows:
			params = {}
			params['server'] = row[0]
			params['port'] = row[1]
			params['database'] = row[2]
			servers.append(params)
		return servers
	
	
	def get_available_dwb_cons(self):
		servers = self.get_available_servers()
		
		dwbcons = []
		for params in servers:
			dwbcons.append("{0}:{1}:{2}".format(params['server'], params['port'], params['database']))
		
		return dwbcons
		
	
