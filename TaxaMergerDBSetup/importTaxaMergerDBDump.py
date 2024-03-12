import pudb
import subprocess
import argparse

from configparser import ConfigParser
config = ConfigParser(allow_no_value=True)
config.read('./config.ini')

from DBConnectors.MySQLConnector import MySQLConnector

class TaxaMergerDBImport():
	def __init__(self, dump_file):
		self.dump_file = dump_file
		
		self.dbconfig = {
			'host': config.get('authentication_db', 'host'),
			'port': int(config.get('authentication_db', 'port')),
			'user': 'root',
			'password': config.get('authentication_db', 'root_password'),
			'database': config.get('authentication_db', 'database'),
			'charset': config.get('authentication_db', 'charset', fallback = 'utf8mb4')
		}
		
		self.dbcon = MySQLConnector(self.dbconfig)
		self.cur = self.dbcon.getCursor()
		self.con = self.dbcon.getConnection()
		
		self.taxadbconfig = {
			'host': config.get('taxamergerdb', 'host'),
			'port': int(config.get('taxamergerdb', 'port')),
			'user': config.get('taxamergerdb', 'user'),
			'password': config.get('taxamergerdb', 'password'),
			'database': config.get('taxamergerdb', 'database'),
			'charset': config.get('taxamergerdb', 'charset', fallback = 'utf8mb4')
		}
		
		self.create_database()
		self.import_database()

	def create_database(self):
		query = """
		DROP DATABASE IF EXISTS `{0}`
		;""".format(self.taxadbconfig['database'])
		
		self.cur.execute(query)
		self.con.commit()
		
		query = """
		CREATE DATABASE `{0}` 
		;""".format(self.taxadbconfig['database'])
		
		self.cur.execute(query)
		self.con.commit()
		
		query = """
		GRANT ALL ON `{0}`.* TO %s
		;""".format(self.taxadbconfig['database'])
		
		self.cur.execute(query, [self.taxadbconfig['user']])
		self.con.commit()
		return


	def import_database(self):
		with open(self.dump_file) as fh:
			data_string = fh.read()
			data = data_string.encode()
			subprocess.run(['mysql', '{0}'.format(self.taxadbconfig['database']),
				'-h', '{0}'.format(self.taxadbconfig['host']),
				'-P', '{0}'.format(self.taxadbconfig['port']),
				'-u', '{0}'.format(self.taxadbconfig['user']),
				'-p{0}'.format(self.taxadbconfig['password'])
				]
				, check=True, input=data)
		
		return


if __name__ == "__main__":
	usage = "importTaxaMergerDBDump.py <mysql_dump.sql>"
	parser = argparse.ArgumentParser(prog="importTaxaMergerDBDump.py", usage=usage, description='Argument importTaxaMergerDBDump.py')
	parser.add_argument('file')
	args = parser.parse_args()
	
	TaxaMergerDBImport(args.file)
	exit(0)

