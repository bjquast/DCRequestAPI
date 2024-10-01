#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pudb

from configparser import ConfigParser

config = ConfigParser()
config.read('config.ini')

import logging, logging.config
logging.config.fileConfig('logging.conf')
logger = logging.getLogger('elastic_indexer')
log_query = logging.getLogger('query')

from DBConnectors.MSSQLConnector import MSSQLConnector


class EmbargoGetter():
	def __init__(self, projects_db, dc_db):
		self.embargo_filters = []
		self.embargo_temptable = None
		
		self.read_embargo_filters(projects_db)
		self.fill_embargo_temptable_in_DC(dc_db)


	def read_embargo_filters(self, projects_db):
		projects_db_con = projects_db.getConnection()
		projects_db_cur = projects_db.getCursor()
		
		query = """
		WITH cte_embargo(adepth, ChildProjectID, ProjectID, ProjectParentID, Project) AS (
			SELECT 0 AS adepth, bp.ProjectID AS ChildProjectID, p.ProjectID, p.ProjectParentID, p.Project
			FROM Project p
			INNER JOIN Project bp ON p.ProjectID = bp.ProjectID
		UNION ALL 
			SELECT 
			ct.adepth+1,
			ct.ChildProjectID,
			dp.ProjectID, dp.ProjectParentID, dp.Project
			FROM Project dp
			 -- join cte it self
			INNER JOIN cte_embargo ct
			ON dp.ProjectID = ct.ProjectParentID
		)
		SELECT DISTINCT  -- ct.ChildProjectID, ct.ProjectID, ct.adepth, ds.DisplayText, dps.value, ct.ProjectParentID, ct.Project
		ct.ChildProjectID, ds.DisplayText
		FROM cte_embargo ct
		INNER JOIN ProjectSetting dps ON ct.ProjectID = dps.ProjectID
		INNER JOIN Setting ds ON dps.SettingID = ds.SettingID
		WHERE ds.DisplayText IN ('embargo_collector', 'anonymize_collector', 'anonymize_depositor',
					'anonymize_determiner', 'embargo_event_but_country', 'embargo_coordinates',
					'embargo_event_but_country_after_1992', 'embargo_coll_date')
		ORDER BY ct.ChildProjectID
		;"""
		log_query.debug(query)
		projects_db_cur.execute(query)
		rows = projects_db_cur.fetchall()
		
		self.embargo_filters = []
		
		for row in rows:
			self.embargo_filters.append([int(row[0]), row[1]])
		
		return self.embargo_filters


	def fill_embargo_temptable_in_DC(self, dc_db):
		dc_con = dc_db.getConnection()
		dc_cur = dc_db.getCursor()
		
		self.embargo_temptable = '#embargo_temptable'
		
		query = """
		DROP TABLE IF EXISTS [{0}]
		;""".format(self.embargo_temptable)
		dc_cur.execute(query)
		dc_con.commit()
		
		query = """
		CREATE TABLE [{0}] (
			ProjectID INT NOT NULL,
			DisplayText NVARCHAR(50) COLLATE DATABASE_DEFAULT,
			INDEX [ProjectID_idx] ([ProjectID]),
			INDEX [DisplayText_idx] ([DisplayText])
		)
		;""".format(self.embargo_temptable)
		log_query.debug(query)
		dc_cur.execute(query)
		dc_con.commit()
		
		pagesize = 1000
		while len(self.embargo_filters) > 0:
			cached_valuelists = self.embargo_filters[:pagesize]
			del self.embargo_filters[:pagesize]
			
			placeholders = ['(?, ?)' for _ in cached_valuelists]
			values = []
			for valuelist in cached_valuelists:
				values.extend(valuelist)
			
			query = """
			INSERT INTO [{0}] (ProjectID, DisplayText)
			VALUES {1}
			;""".format(self.embargo_temptable, ', '.join(placeholders))
			dc_cur.execute(query, values)
			dc_con.commit()
		
		return self.embargo_temptable
