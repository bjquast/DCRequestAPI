import pymysql
import warnings
import re

import pudb
import logging, logging.config

logger = logging.getLogger('error')
log_query = logging.getLogger('query')

#from pymysql.constants.CLIENT import MULTI_STATEMENTS

class MySQLConnector():
	def __init__(self, config = None, host = None, user = None, password = None, database = None, charset = None, port = None):
		'''
		Class to read and represent the database structure
		'''
		if config is None:
			self.config = {
			'host': 'localhost',
			'password': None,
			'charset': 'utf8',
			'port': '3306',
			'user': None,
			'database': None
			}
		else: 
			#copy the data, do not change the original dict
			self.config = dict(config)
		
		# check if there is something in the other parameters
		if host is not None:
			self.config['host'] = host
		if user is not None:
			self.config['user'] = user
		if password is not None:
			self.config['password'] = password
		if database is not None:
			self.config['database'] = database
		if charset is not None:
			self.config['charset'] = charset
		if port is not None:
			self.config['port'] = port
		
		
		if (self.config['database'] is None) or (self.config['user'] is None):
			raise Exception ('Not enough data base connection parameters given')
		self.con = None
		self.cur = None
		self.open_connection()
		self.MysqlError = pymysql.err

		self.databasename = self.config['database']

		

	def open_connection(self):
		self.con = self.__mysql_connect()
		self.cur = self.con.cursor()


	def __mysql_connect(self):
		try:
			con = pymysql.connect(host=self.config['host'], user=self.config['user'], password=self.config['password'], database=self.config['database'], port=int(self.config['port']), charset=self.config['charset'])
		except pymysql.Error as e:
			logger.critical("Error {0}: {1}".format(*e.args))
			raise
		return con


	def closeConnection(self):
		if self.con:
			self.con.close()



	'''
	expose the connection and cursor
	'''
	
	def getCursor(self):
		return self.cur
	
	def getConnection(self):
		return self.con
	






