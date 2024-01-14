import pudb

from dwb_authentication.mysql_connect import mysql_connect


class DWB_Servers():
	def __init__(self):
		
		self.con, self.cur = mysql_connect()
		self.set_available_servers()
	
	
	def set_available_servers(self):
		self.servers = []
		
		query = """
		SELECT `accronym`, `server`, `port`, `database`, `driver`
		FROM `mssql_connectors`
		;"""
		
		self.cur.execute(query)
		rows = self.cur.fetchall()
		for row in rows:
			server = {}
			server['accronym'] = row[0]
			server['server'] = row[1]
			server['port'] = row[2]
			server['database'] = row[3]
			server['driver'] = row[4]
			self.servers.append(server)
		return
	
	
	def get_available_dwb_cons(self):
		return self.servers
	
	
	def get_dwb_con_by_accronym(self, accronym):
		dwb_con = None
		for server in self.servers:
			if accronym == server['accronym']:
				dwb_con = server
		
		return dwb_con

