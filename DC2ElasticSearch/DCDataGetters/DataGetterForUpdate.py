
import pudb
import logging, logging.config
logger = logging.getLogger('elastic_indexer')
log_query = logging.getLogger('query')

from DC2ElasticSearch.DCDataGetters.DataGetter import DataGetter

class DataGetterForUpdate(DataGetter):
	def __init__(self, dc_params, last_updated):
		DataGetter.__init__(self, dc_params, last_updated)
		self.last_updated = last_updated


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
		
		self.max_page_to_delete = int(self.rownumber / self.pagesize) +1
		return
