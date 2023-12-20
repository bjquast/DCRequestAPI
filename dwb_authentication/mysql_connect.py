import pudb
import pymysql

from configparser import ConfigParser
config = ConfigParser(allow_no_value=True)
config.read('./config.ini')


def mysql_connect():
	host = config.get('authentication_db', 'host')
	port = int(config.get('authentication_db', 'port'))
	user = config.get('authentication_db', 'user')
	passwd = config.get('authentication_db', 'password')
	db = config.get('authentication_db', 'database')
	
	
	conn = pymysql.connect(host=host, port=port, user=user, passwd=passwd, db=db)
	cur = conn.cursor()
	return (conn, cur)
