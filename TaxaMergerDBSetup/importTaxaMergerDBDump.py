import pudb
import subprocess
import argparse

from configparser import ConfigParser
config = ConfigParser(allow_no_value=True)
config.read('./config.ini')

# from DBConnectors.MySQLConnector import MySQLConnector

class TaxaMergerDBImport():
	def __init__(self, dump_file):
		self.dump_file = dump_file
		
		self.dbconfig = {
			'host': config.get('taxamergerdb', 'host'),
			'port': int(config.get('taxamergerdb', 'port')),
			'user': config.get('taxamergerdb', 'user'),
			'password': config.get('taxamergerdb', 'password'),
			'database': config.get('taxamergerdb', 'database'),
			'charset': config.get('taxamergerdb', 'charset', fallback = 'utf8mb4')
		}
		
		self.import_database()


	def import_database(self):
		with open(self.dump_file) as fh:
			data_string = fh.read()
			data = data_string.encode()
			subprocess.run(['mysql', '{0}'.format(self.dbconfig['database']),
				'-h', '{0}'.format(self.dbconfig['host']),
				'-P', '{0}'.format(self.dbconfig['port']),
				'-u', '{0}'.format(self.dbconfig['user']),
				'-p{0}'.format(self.dbconfig['password'])
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

