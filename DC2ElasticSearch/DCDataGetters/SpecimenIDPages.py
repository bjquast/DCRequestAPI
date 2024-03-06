
import pudb
import math

import logging, logging.config
logger = logging.getLogger('elastic_indexer')
log_query = logging.getLogger('query')

from DBConnectors.MSSQLConnector import MSSQLConnector

class SpecimenIDPages():
	"""
	class to get the first and last CollectionSpecimenID for a page that should become indexed or updated
	because the CollectionsSpecimenIDs 
	"""
	
	def __init__(self, dc_params, last_updated = None):
		
		self.dc_con = MSSQLConnector(dc_params['connectionstring'])
		self.server_url = dc_params['server_url']
		self.database_name = dc_params['database_name']
		self.accronym = dc_params['accronym']
		self.database_id = dc_params['database_id']
		
		self.cur = self.dc_con.getCursor()
		self.con = self.dc_con.getConnection()
		
		self.last_updated = last_updated
		
		self.pagesize = 10000
		
		self.create_ids_temptable()
		self.fill_ids_temptable()
		


	def create_ids_temptable(self):
		query = """
		DROP TABLE IF EXISTS [#temp_cs_ids]
		;"""
		self.cur.execute(query)
		self.con.commit()
		
		query = """
		CREATE TABLE [#temp_cs_ids] (
		[rownumber] INT IDENTITY PRIMARY KEY, -- set an IDENTITY column that can be used for paging,
		[CollectionSpecimenID] INT,
		INDEX [idx_CollectionSpecimenID] ([CollectionSpecimenID])
		)
		;"""
		self.cur.execute(query)
		self.con.commit()
		return


	def fill_ids_temptable(self, last_updated = None):
		if last_updated is not None:
			self.last_updated = last_updated
		
		params = []
		last_update_clause = ""
		
		if self.last_updated is not None:
			last_update_clause = "WHERE LogUpdatedWhen > CONVERT(DATETIME, ?, 121)"
			params.append(self.last_updated)
		
		query = """
		INSERT INTO [#temp_cs_ids] ([CollectionSpecimenID])
		SELECT 
		 -- TOP 40000
		[CollectionSpecimenID]
		FROM [CollectionSpecimen]
		 -- important to order, so that the rownumbers can be used to get the min and max [CollectionSpecimenID] for each page
		ORDER BY [CollectionSpecimenID]
		{0}
		;""".format(last_update_clause)
		
		self.cur.execute(query, params)
		self.con.commit()
		
		self.set_max_page()
		return


	# wich version will be faster?
	def getPageRangesSimple(self):
		# with 1000000 SpecimenIDs = 100 database requests
		# with 10000000 SpecimenIDs = 1000 database requests
		# with 100000000 SpecimenIDs = 10000 database requests
		page_ranges = []
		for page in range(1, self.max_page + 1):
			startrow = (page - 1) * self.pagesize + 1
			lastrow = page * self.pagesize
			
			query = """
			SELECT MIN(CollectionSpecimenID), MAX(CollectionSpecimenID)
			FROM [#temp_cs_ids]
			WHERE [rownumber] BETWEEN ? AND ?
			;"""
			self.cur.execute(query)
			row = self.cur.fetchone()
			if row is not None:
				page_ranges.append(row[0], row[1])
		
		return page_ranges


	def getPageRangesByDB(self):
		# with 1000000 SpecimenIDs = 5 database requests
		# with 10000000 SpecimenIDs = 6 database requests
		# with 100000000 SpecimenIDs = 24 database requests
		query = """
		DROP TABLE IF EXISTS [#temp_page_limits]
		;"""
		self.cur.execute(query)
		self.con.commit()
		
		query = """
		CREATE TABLE [#temp_page_limits] (
			[page] INT NOT NULL PRIMARY KEY,
			[start_row] INT NOT NULL,
			[last_row] INT NOT NULL,
			[CollectionSpecimenID_start] INT,
			[CollectionSpecimenID_last] INT,
			INDEX [idx_start_row] ([start_row]),
			INDEX [idx_last_row] ([last_row]),
			INDEX [idx_CollectionSpecimenID_start] ([CollectionSpecimenID_start]),
			INDEX [idx_CollectionSpecimenID_last] ([CollectionSpecimenID_last])
		)
		;"""
		self.cur.execute(query)
		self.con.commit()
		
		pagelimits = []
		for page in range(1, self.max_page + 1):
			startrow = (page - 1) * self.pagesize + 1
			lastrow = page * self.pagesize
			pagelimits.append([page, startrow, lastrow])
		
		# ms sql does not accept more than 2100 parameters in insert query
		
		while len(pagelimits) > 0:
			limits_slice = pagelimits[0:500]
			del pagelimits[0:500]
			values = []
			for limits in limits_slice:
				values.extend(limits)
			placeholders = ['(?, ?, ?)' for _ in limits_slice]
		
			query = """
			INSERT INTO [#temp_page_limits] ([page], [start_row], [last_row])
			VALUES {0}
			;""".format(', '.join(placeholders))
			
			self.cur.execute(query, values)
			self.con.commit()
		
		query = """
		UPDATE [#temp_page_limits]
		SET 
			[#temp_page_limits].[CollectionSpecimenID_start] = cs_ids_start.[CollectionSpecimenID],
			[#temp_page_limits].[CollectionSpecimenID_last] = cs_ids_last.[CollectionSpecimenID]
		FROM [#temp_page_limits] pl
		INNER JOIN [#temp_cs_ids] cs_ids_start
			ON cs_ids_start.[rownumber] = pl.[start_row]
		INNER JOIN [#temp_cs_ids] cs_ids_last
			ON cs_ids_last.[rownumber] = pl.[last_row]
		;"""
		self.cur.execute(query)
		self.con.commit()
			
		
		page_ranges = []
		query = """
		SELECT [CollectionSpecimenID_start], [CollectionSpecimenID_last]
		FROM [#temp_page_limits]
		ORDER BY [page]
		;"""
		self.cur.execute(query)
		rows = self.cur.fetchall()
		for row in rows:
			page_ranges.append([row[0], row[1]])
		
		return page_ranges



	def set_max_page(self):
		query = """
		SELECT COUNT(CollectionSpecimenID) FROM [#temp_cs_ids]
		;"""
		
		self.cur.execute(query)
		row = self.cur.fetchone()
		self.rownumber = row[0]
		
		self.max_page = math.ceil(self.rownumber / self.pagesize)
		return
