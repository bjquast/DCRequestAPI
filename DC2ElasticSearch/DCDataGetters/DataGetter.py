
import pudb
import math

import logging, logging.config
logger = logging.getLogger('elastic_indexer')
log_query = logging.getLogger('query')

from DBConnectors.MSSQLConnector import MSSQLConnector

class DataGetter():
	def __init__(self, dc_params):
		
		self.dc_con = MSSQLConnector(dc_params['connectionstring'])
		self.server_url = dc_params['server_url']
		self.database_name = dc_params['database_name']
		self.accronym = dc_params['accronym']
		self.database_id = dc_params['database_id']
		
		self.cur = self.dc_con.getCursor()
		self.con = self.dc_con.getConnection()
		


	def create_ids_temptable(self):
		query = """
		DROP TABLE IF EXISTS [#temp_iu_part_ids]
		;"""
		self.cur.execute(query)
		self.con.commit()
		
		query = """
		CREATE TABLE [#temp_iu_part_ids] (
		[rownumber] INT IDENTITY PRIMARY KEY, -- set an IDENTITY column that can be used for paging,
		[idshash] NVARCHAR(255) NOT NULL,
		[DatabaseURI] NVARCHAR(255),
		[DatabaseID] NVARCHAR(50),
		[DatabaseAccronym] NVARCHAR(255),
		[CollectionSpecimenID] INT, 
		[IdentificationUnitID] INT,
		[SpecimenPartID] INT,
		[SpecimenAccessionNumber] NVARCHAR(255),
		[PartAccessionNumber] NVARCHAR(255),
		INDEX [idx_idshash] UNIQUE ([idshash]),
		INDEX [idx_DatabaseURI] ([DatabaseURI]),
		INDEX [idx_CollectionSpecimenID] ([CollectionSpecimenID]),
		INDEX [idx_IdentificationUnitID] ([IdentificationUnitID]),
		INDEX [idx_SpecimenPartID] ([SpecimenPartID]),
		INDEX [idx_SpecimenAccessionNumber] ([SpecimenAccessionNumber]),
		INDEX [idx_PartAccessionNumber] ([PartAccessionNumber])
		)
		;"""
		self.cur.execute(query)
		self.con.commit()
		return


	def fill_ids_temptable(self, first_cs_id, last_cs_id):
		
		params = []
		
		query = """
		INSERT INTO [#temp_iu_part_ids]
		([idshash], [DatabaseURI], [DatabaseID], [DatabaseAccronym], [CollectionSpecimenID], [IdentificationUnitID], [SpecimenPartID], [SpecimenAccessionNumber], [PartAccessionNumber])
		SELECT 
		 -- for development
		 -- TOP 20000
		CONVERT(VARCHAR(256), HASHBYTES(
			'SHA2_256', CONCAT('{0}/{1}', '_', 
			cs.CollectionSpecimenID, '_', iu.IdentificationUnitID, '_', csp.SpecimenPartID)), 2
		) AS idshash,
		'{0}/{1}' AS DatabaseURI,
		'{2}' AS DatabaseID,
		'{3}' AS DatabaseAccronym,
		cs.CollectionSpecimenID, iu.IdentificationUnitID, csp.SpecimenPartID,
		cs.AccessionNumber AS SpecimenAccessionNumber,
		COALESCE(csp.AccessionNumber, cs.AccessionNumber) AS PartAccessionNumber
		FROM IdentificationUnit iu 
		INNER JOIN CollectionSpecimen cs 
		ON iu.CollectionSpecimenID = cs.CollectionSpecimenID 
		LEFT JOIN IdentificationUnitInPart iup
		ON iup.CollectionSpecimenID = iu.CollectionSpecimenID AND iup.IdentificationUnitID = iu.IdentificationUnitID 
		LEFT JOIN CollectionSpecimenPart csp 
		ON csp.CollectionSpecimenID = iup.CollectionSpecimenID AND csp.SpecimenPartID = iup.SpecimenPartID 
		WHERE cs.CollectionSpecimenID BETWEEN ? AND ?
		 -- for development
		 -- WHERE cs.AccessionNumber = 'ZFMK-TIS-46'
		 -- WHERE cs.CollectionSpecimenID = 14
		ORDER BY [CollectionSpecimenID], [IdentificationUnitID], [SpecimenPartID]
		;""".format(self.server_url, self.database_name, self.database_id, self.accronym)
		
		log_query.info(query)
		log_query.info([first_cs_id, last_cs_id])
		
		self.cur.execute(query, [first_cs_id, last_cs_id])
		self.cur.commit()
		
		query = """
		UPDATE [#temp_iu_part_ids]
		SET PartAccessionNumber = SpecimenAccessionNumber
		WHERE PartAccessionNumber = ''
		;"""
		
		self.cur.execute(query)
		self.cur.commit()
		
		#self.set_max_page()
		return

	'''
	def set_max_page(self):
		query = """
		SELECT COUNT(idshash) FROM [#temp_iu_part_ids]
		;"""
		
		self.cur.execute(query)
		row = self.cur.fetchone()
		self.rownumber = row[0]
		
		self.max_page = math.ceil(self.rownumber / self.pagesize)
		return


	def create_deleted_temptable(self):
		query = """
		DROP TABLE IF EXISTS [#temp_deleted_iu_part_ids]
		;"""
		self.cur.execute(query)
		self.con.commit()
		
		
		query = """
		CREATE TABLE [#temp_deleted_iu_part_ids] (
		[rownumber] INT IDENTITY PRIMARY KEY, -- set an IDENTITY column that can be used for paging,
		[idshash] NVARCHAR(255) NOT NULL,
		INDEX [idx_idshash] UNIQUE ([idshash])
		)
		;"""
		
		log_query.debug(query)
		self.cur.execute(query)
		self.con.commit()
		
		
		query = """
		INSERT INTO [#temp_deleted_iu_part_ids] ([idshash])
		SELECT DISTINCT
		CONVERT(VARCHAR(256), HASHBYTES(
			'SHA2_256', CONCAT('{0}/{1}', '_', 
			csl.CollectionSpecimenID, '_', iul.IdentificationUnitID, '_', cspl.SpecimenPartID)), 2
		) AS idshash
		FROM IdentificationUnit_log iul 
		INNER JOIN CollectionSpecimen_log csl 
		ON iul.CollectionSpecimenID = csl.CollectionSpecimenID 
		LEFT JOIN IdentificationUnitInPart_log iupl
		ON iupl.CollectionSpecimenID = iul.CollectionSpecimenID AND iupl.IdentificationUnitID = iul.IdentificationUnitID 
		LEFT JOIN CollectionSpecimenPart_log cspl 
		ON cspl.CollectionSpecimenID = iupl.CollectionSpecimenID AND cspl.SpecimenPartID = iupl.SpecimenPartID 
		WHERE csl.LogDate > CONVERT(DATETIME, ?, 120)
		AND csl.LogState = 'D'
		;""".format(self.server_url, self.database_name)
		
		log_query.debug(query)
		log_query.debug(self.last_updated)
		self.cur.execute(query, [self.last_updated])
		self.con.commit()
		
		self.set_max_page_to_delete()
		
		return


	def get_deleted_ids_page(self, page):
		if page <= self.max_page_to_delete:
			startrow = (page - 1) * self.pagesize + 1
			lastrow = page * self.pagesize
		
		query = """
		SELECT idshash 
		FROM [#temp_deleted_iu_part_ids]
		WHERE [rownumber] BETWEEN ? AND ?
		;"""
		
		self.cur.execute(query, [startrow,lastrow])
		rows = self.cur.fetchall()
		
		deleted_ids = []
		for row in rows:
			deleted_ids.append(row[0])
		
		return deleted_ids


	def set_max_page_to_delete(self):
		query = """
		SELECT COUNT(idshash) FROM [#temp_deleted_iu_part_ids]
		;"""
		
		self.cur.execute(query)
		row = self.cur.fetchone()
		self.rownumber = row[0]
		
		self.max_page_to_delete = math.ceil(self.rownumber / self.pagesize)
		return
	'''
