import pudb

from configparser import ConfigParser
config = ConfigParser(allow_no_value=True)
config.read('./config.ini')

from dwb_authentication.mysql_connect import mysql_connect

class SessionDBSetup():
	def __init__(self):
		self.con, self.cur = mysql_connect()
		
		self.delete_tables()
		self.create_tables()
		self.set_default_connectors()


	def delete_tables(self):
		
		query = """
		DROP TABLE IF EXISTS `dwb_projects`
		;"""
		
		self.cur.execute(query)
		self.con.commit()
		
		query = """
		DROP TABLE IF EXISTS `dwb_roles`
		;"""
		
		self.cur.execute(query)
		self.con.commit()
		
		query = """
		DROP TABLE IF EXISTS `sessions`
		;"""
		
		self.cur.execute(query)
		self.con.commit()
		
		query = """
		DROP TABLE IF EXISTS `mssql_connectors`
		;"""
		
		self.cur.execute(query)
		self.con.commit()
		


	def create_tables(self):
		
		query = """
		CREATE TABLE `mssql_connectors` (
			`db_connector_id` INT NOT NULL AUTO_INCREMENT,
			`server` varchar(255) NOT NULL,
			`port` INT DEFAULT NULL,
			`database` varchar(255) DEFAULT NULL,
			`remember_connector` tinyint(1) DEFAULT 0,
			PRIMARY KEY (`db_connector_id`),
			UNIQUE KEY `idx_connector` (`server`,`port`,`database`),
			KEY (`server`),
			KEY (`database`)
		) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
		;"""
		
		self.cur.execute(query)
		self.con.commit()
		
		
		query = """
		CREATE TABLE `sessions` (
			`session_id` INT NOT NULL AUTO_INCREMENT,
			`hashed_token` varchar(255) NOT NULL,
			`encrypted_passwd` varchar(255),
			`expiration_time` datetime NOT NULL,
			`username` VARCHAR(50) NOT NULL,
			`db_connector_id` INT NOT NULL,
			PRIMARY KEY (`session_id`),
			UNIQUE KEY `hashed_token` (`hashed_token`),
			KEY (`username`),
			FOREIGN KEY (`db_connector_id`) REFERENCES `mssql_connectors` (`db_connector_id`)
		) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
		;"""
		
		self.cur.execute(query)
		self.con.commit()
		
		
		query = """
		CREATE TABLE `dwb_roles` (
			`users_dwb_role` VARCHAR(255),
			`session_id` INT NOT NULL,
			PRIMARY KEY(`session_id`, `users_dwb_role`),
			FOREIGN KEY(`session_id`) REFERENCES `sessions` (`session_id`)
		) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
		;
		"""
		self.cur.execute(query)
		self.con.commit()
		
		
		query = """
		CREATE TABLE `dwb_projects` (
			`users_dwb_project_id` INT,
			`project_name` VARCHAR(255),
			`session_id` INT NOT NULL,
			PRIMARY KEY(`session_id`, `users_dwb_project_id`),
			FOREIGN KEY(`session_id`) REFERENCES `sessions` (`session_id`)
		) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
		;
		"""
		self.cur.execute(query)
		self.con.commit()


	def set_default_connectors(self):
		
		self.read_default_connectors()
		
		if len(self.default_connectors) > 0:
			placeholders = []
			values = []
			for valuelist in self.default_connectors:
				placeholders.append('(%s, %s, %s, %s)')
				values.extend(valuelist)
			placeholderstring = ', '.join(placeholders)
			
			query = """
			INSERT INTO `mssql_connectors`
			(`server`, `port`, `database`, `remember_connector`)
			VALUES {0}
			;""".format(placeholderstring)
			
			
			self.cur.execute(query, values)
			self.con.commit()


	def read_default_connectors(self):
		self.default_connectors = []
		
		sections = config.sections()
		for section in sections:
			if section[:12]=='data_source_' and section!='data_source_test':
				server = config.get(section, 'server', fallback = None)
				port = config.get(section, 'port', fallback = None)
				database_name = config.get(section, 'database', fallback = None)
			
				if server is not None and port is not None and database_name is not None:
					self.default_connectors.append([server, port, database_name, 1])
		
		return
		



if __name__ == "__main__":
	db_setup = SessionDBSetup()


