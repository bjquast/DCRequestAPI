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


class EmbargoWithholdSetter():
	def __init__(self, dc_db, embargo_temptable):
		self.dc_db = dc_db
		self.embargo_temptable = embargo_temptable
		
		self.con = self.dc_db.getConnection()
		self.cur = self.dc_db.getCursor()
		
		self.embargo_collector()
		self.anonymize_depositor()
		self.anonymize_depositor_after_1950()
		self.anonymize_collector()
		self.anonymize_collector_after_1950()
		self.anonymize_determiner()
		self.anonymize_determiner_after_1950()
		self.embargo_event_but_country()
		self.embargo_coordinates()
		self.embargo_event_but_country_after_1992()
		self.embargo_coll_date()
		self.embargo_specimen()


	def embargo_collector(self):
		query = """
		UPDATE [#temp_iu_part_ids]
		SET [embargo_collector] = 1
		FROM [#temp_iu_part_ids] gt
		INNER JOIN IdentificationUnit iu ON
		iu.CollectionSpecimenID = gt.CollectionSpecimenID AND iu.IdentificationUnitID = gt.IdentificationUnitID
		INNER JOIN CollectionProject cp ON
		cp.CollectionSpecimenID = iu.CollectionSpecimenID
		INNER JOIN [{0}] et
		ON et.ProjectID = cp.ProjectID
		WHERE et.DisplayText IN ('embargo_collector')
		;""".format(self.embargo_temptable)
		log_query.debug(query)
		self.cur.execute(query)
		self.con.commit()
		return


	def anonymize_depositor(self):
		query = """
		UPDATE [#temp_iu_part_ids]
		SET [embargo_anonymize_depositor] = 1
		FROM [#temp_iu_part_ids] gt
		INNER JOIN IdentificationUnit iu ON
		iu.CollectionSpecimenID = gt.CollectionSpecimenID AND iu.IdentificationUnitID = gt.IdentificationUnitID
		INNER JOIN CollectionProject cp ON 
		cp.CollectionSpecimenID = iu.CollectionSpecimenID
		INNER JOIN [{0}] et
		ON et.ProjectID = cp.ProjectID
		WHERE et.DisplayText IN ('anonymize_depositor')
		;""".format(self.embargo_temptable)
		log_query.debug(query)
		self.cur.execute(query)
		self.con.commit()
		return


	def anonymize_depositor_after_1950(self):
		query = """
		UPDATE [#temp_iu_part_ids]
		SET [embargo_anonymize_depositor] = 1
		FROM [#temp_iu_part_ids] gt
		INNER JOIN IdentificationUnit iu
		ON iu.CollectionSpecimenID = gt.CollectionSpecimenID AND iu.IdentificationUnitID = gt.IdentificationUnitID
		INNER JOIN CollectionSpecimen cs
		ON iu.CollectionSpecimenID = cs.CollectionSpecimenID
		INNER JOIN CollectionEvent ce
		ON ce.CollectionEventID = cs.CollectionEventID AND ce.CollectionYear > 1949
		INNER JOIN CollectionProject cp
		ON cp.CollectionSpecimenID = iu.CollectionSpecimenID
		INNER JOIN [{0}] et
		ON et.ProjectID = cp.ProjectID
		WHERE et.DisplayText IN ('anonymize_depositor_after_1950')
		;""".format(self.embargo_temptable)
		log_query.debug(query)
		self.cur.execute(query)
		self.con.commit()
		return


	def anonymize_collector(self):
		query = """
		UPDATE [#temp_iu_part_ids]
		SET [embargo_anonymize_collector] = 1
		FROM [#temp_iu_part_ids] gt
		INNER JOIN IdentificationUnit iu
		ON iu.CollectionSpecimenID = gt.CollectionSpecimenID AND iu.IdentificationUnitID = gt.IdentificationUnitID
		INNER JOIN CollectionProject cp
		ON cp.CollectionSpecimenID = iu.CollectionSpecimenID
		INNER JOIN [{0}] et
		ON et.ProjectID = cp.ProjectID
		WHERE et.DisplayText IN ('anonymize_collector')
		;""".format(self.embargo_temptable)
		log_query.debug(query)
		self.cur.execute(query)
		self.con.commit()
		return


	def anonymize_collector_after_1950(self):
		query = """
		UPDATE [#temp_iu_part_ids]
		SET [embargo_anonymize_collector] = 1
		FROM [#temp_iu_part_ids] gt
		INNER JOIN IdentificationUnit iu
		ON iu.CollectionSpecimenID = gt.CollectionSpecimenID AND iu.IdentificationUnitID = gt.IdentificationUnitID
		INNER JOIN CollectionSpecimen cs
		ON iu.CollectionSpecimenID = cs.CollectionSpecimenID
		INNER JOIN CollectionEvent ce
		ON ce.CollectionEventID = cs.CollectionEventID AND ce.CollectionYear > 1949
		INNER JOIN CollectionProject cp
		ON cp.CollectionSpecimenID = iu.CollectionSpecimenID
		INNER JOIN [{0}] et
		ON et.ProjectID = cp.ProjectID
		WHERE et.DisplayText IN ('anonymize_collector_after_1950')
		;""".format(self.embargo_temptable)
		log_query.debug(query)
		self.cur.execute(query)
		self.con.commit()
		return


	def anonymize_determiner(self):
		query = """
		UPDATE [#temp_iu_part_ids]
		SET [embargo_anonymize_determiner] = 1
		FROM [#temp_iu_part_ids] gt
		INNER JOIN IdentificationUnit iu
		ON iu.CollectionSpecimenID = gt.CollectionSpecimenID AND iu.IdentificationUnitID = gt.IdentificationUnitID
		INNER JOIN CollectionProject cp
		ON cp.CollectionSpecimenID = iu.CollectionSpecimenID
		INNER JOIN [{0}] et
		ON et.ProjectID = cp.ProjectID
		WHERE et.DisplayText IN ('anonymize_determiner')
		;""".format(self.embargo_temptable)
		log_query.debug(query)
		self.cur.execute(query)
		self.con.commit()
		return


	def anonymize_determiner_after_1950(self):
		query = """
		UPDATE [#temp_iu_part_ids]
		SET [embargo_anonymize_determiner] = 1
		FROM [#temp_iu_part_ids] gt
		INNER JOIN IdentificationUnit iu
		ON iu.CollectionSpecimenID = gt.CollectionSpecimenID AND iu.IdentificationUnitID = gt.IdentificationUnitID
		INNER JOIN CollectionSpecimen cs
		ON iu.CollectionSpecimenID = cs.CollectionSpecimenID
		INNER JOIN CollectionEvent ce
		ON ce.CollectionEventID = cs.CollectionEventID AND ce.CollectionYear > 1949
		INNER JOIN CollectionProject cp
		ON cp.CollectionSpecimenID = iu.CollectionSpecimenID
		INNER JOIN [{0}] et
		ON et.ProjectID = cp.ProjectID
		WHERE et.DisplayText IN ('anonymize_determiner_after_1950')
		;""".format(self.embargo_temptable)
		log_query.debug(query)
		self.cur.execute(query)
		self.con.commit()
		return


	def embargo_event_but_country(self):
		query = """
		UPDATE [#temp_iu_part_ids]
		SET [embargo_event_but_country] = 1
		FROM [#temp_iu_part_ids] gt
		INNER JOIN IdentificationUnit iu
		ON iu.CollectionSpecimenID = gt.CollectionSpecimenID AND iu.IdentificationUnitID = gt.IdentificationUnitID
		INNER JOIN CollectionProject cp
		ON cp.CollectionSpecimenID = iu.CollectionSpecimenID
		INNER JOIN [{0}] et
		ON et.ProjectID = cp.ProjectID
		WHERE et.DisplayText IN ('embargo_event_but_country')
		;""".format(self.embargo_temptable)
		log_query.debug(query)
		self.cur.execute(query)
		self.con.commit()
		return


	def embargo_coordinates(self):
		query = """
		UPDATE [#temp_iu_part_ids]
		SET [embargo_coordinates] = 1
		FROM [#temp_iu_part_ids] gt
		INNER JOIN IdentificationUnit iu
		ON iu.CollectionSpecimenID = gt.CollectionSpecimenID AND iu.IdentificationUnitID = gt.IdentificationUnitID
		INNER JOIN CollectionProject cp
		ON cp.CollectionSpecimenID = iu.CollectionSpecimenID
		INNER JOIN [{0}] et
		ON et.ProjectID = cp.ProjectID
		WHERE et.DisplayText IN ('embargo_coordinates')
		;""".format(self.embargo_temptable)
		log_query.debug(query)
		self.cur.execute(query)
		self.con.commit()
		return


	def embargo_event_but_country_after_1992(self):
		query = """
		UPDATE [#temp_iu_part_ids]
		SET [embargo_event_but_country_after_1992] = 1
		FROM [#temp_iu_part_ids] gt
		INNER JOIN IdentificationUnit iu
			ON iu.CollectionSpecimenID = gt.CollectionSpecimenID AND iu.IdentificationUnitID = gt.IdentificationUnitID
		INNER JOIN CollectionSpecimen cs
			ON iu.CollectionSpecimenID = cs.CollectionSpecimenID
		INNER JOIN CollectionEvent ce
			ON ce.CollectionEventID = cs.CollectionEventID AND ce.CollectionYear > 1991
		INNER JOIN CollectionProject cp
			ON cp.CollectionSpecimenID = iu.CollectionSpecimenID
		INNER JOIN [{0}] et
		ON et.ProjectID = cp.ProjectID
		WHERE et.DisplayText IN ('embargo_event_but_country_after_1992')
		;""".format(self.embargo_temptable)
		log_query.debug(query)
		self.cur.execute(query)
		self.con.commit()
		return


	def embargo_coll_date(self):
		query = """
		UPDATE [#temp_iu_part_ids]
		SET [embargo_coll_date] = 1
		FROM [#temp_iu_part_ids] gt
		INNER JOIN IdentificationUnit iu
		ON iu.CollectionSpecimenID = gt.CollectionSpecimenID AND iu.IdentificationUnitID = gt.IdentificationUnitID
		INNER JOIN CollectionProject cp
		ON cp.CollectionSpecimenID = iu.CollectionSpecimenID
		INNER JOIN [{0}] et
		ON et.ProjectID = cp.ProjectID
		WHERE et.DisplayText IN ('embargo_coll_date')
		;""".format(self.embargo_temptable)
		log_query.debug(query)
		self.cur.execute(query)
		self.con.commit()
		return


	def embargo_specimen(self):
		query = """
		UPDATE [#temp_iu_part_ids]
		SET [embargo_complete] = 1
		FROM [#temp_iu_part_ids] gt
		INNER JOIN IdentificationUnit iu
		ON iu.CollectionSpecimenID = gt.CollectionSpecimenID AND iu.IdentificationUnitID = gt.IdentificationUnitID
		INNER JOIN CollectionProject cp
		ON cp.CollectionSpecimenID = iu.CollectionSpecimenID
		INNER JOIN [{0}] et
		ON et.ProjectID = cp.ProjectID
		WHERE et.DisplayText IN ('embargo_complete')
		;""".format(self.embargo_temptable)
		log_query.debug(query)
		self.cur.execute(query)
		self.con.commit()
		return







	'''
	def apply_embargos(self):
		for project_id in self.datasource_config.project_ids:
			self.project_id = project_id
			
			self.embargo_filters = EmbargoGetter(self.datasource_config, project_id).get_filters_by_project()
			if len(self.embargo_filters) > 0:
				logger.info('Applying embargos for project {0} in data source {1}'.format(project_id, self.datasource_name))
				
				self.set_specimen_temptable()
				
				if 'embargo_collector' in self.embargo_filters:
					logger.info('embargo_collector for project {0} in data source {1}'.format(project_id, self.datasource_name))
					self.setWithholdFlagAgent()
					self.anonymize_by_field_id(6)
				
				if 'anonymize_collector' in self.embargo_filters:
					logger.info('anonymize_collector for project {0} in data source {1}'.format(project_id, self.datasource_name))
					self.anonymize_by_field_id(6)
				
				if 'anonymize_depositor' in self.embargo_filters:
					logger.info('anonymize_depositor for project {0} in data source {1}'.format(project_id, self.datasource_name))
					self.anonymize_by_field_id(9)
				
				if 'anonymize_determiner' in self.embargo_filters:
					logger.info('anonymize_determiner for project {0} in data source {1}'.format(project_id, self.datasource_name))
					self.anonymize_by_field_id(97)
				
				if 'embargo_event_but_country' in self.embargo_filters:
					logger.info('embargo_event_but_country for project {0} in data source {1}'.format(project_id, self.datasource_name))
					self.delete_by_field_ids([3, 4, 5, 6, 9, 10, 11, 13, 14, 16, 18, 26])
					self.delete_coordinates()
				
				if 'embargo_coordinates' in self.embargo_filters:
					logger.info('embargo_coordinates for project {0} in data source {1}'.format(project_id, self.datasource_name))
					self.delete_coordinates()
				
				if 'embargo_event_but_country_after_1992' in self.embargo_filters:
					logger.info('embargo_event_but_country_after_1992 for project {0} in data source {1}'.format(project_id, self.datasource_name))
					self.embargo_event_but_country_after_1992()
					self.delete_coordinates(after = 1992)
				
				if 'embargo_coll_date' in self.embargo_filters:
					logger.info('embargo_coll_date for project {0} in data source {1}'.format(project_id, self.datasource_name))
					self.delete_by_field_ids([4])
		return


	def set_specimen_temptable(self):
		query = """DROP TEMPORARY TABLE IF EXISTS specimen_temp_table;"""
		self.cur.execute(query)
		self.con.commit()
		
		query = """
		CREATE TEMPORARY TABLE specimen_temp_table (
		id INT NOT NULL,
		PRIMARY KEY(id)
		) 
		SELECT id 
		FROM {0}_Specimen cs
		INNER JOIN {0}_CollectionProject cp ON cp.specimen_id = cs.id AND cp.DatasourceID = cs.DatasourceID
		WHERE cp.ProjectID = %s and cp.DatasourceID = %s
		""".format(self.db_suffix)
		
		self.cur.execute(query, [self.project_id, self.datasource_id])
		self.con.commit()
		return


	def setWithholdFlagAgent(self):
		query = """
		UPDATE {0}_Specimen s
		INNER JOIN specimen_temp_table st
		ON st.id = s.id
		SET s.withhold_flag_CollectionAgent = 1
		""".format(self.db_suffix)



	def old_anonymize_by_field_id(self, field_id):
		query = """
		UPDATE {0}_Data d
		INNER JOIN {0}_Data2Specimen d2s
		ON d.id = d2s.data_id
		INNER JOIN specimen_temp_table st
		ON st.id = d2s.specimen_id
		SET d.term = 'Anonymized'
		WHERE d.field_id = %s
		""".format(self.db_suffix)
		
		self.cur.execute(query, field_id)
		self.con.commit()
		return


	def delete_by_field_ids(self, field_ids = []):
		if len(field_ids) > 0:
			placeholders = ['%s' for i in field_ids]
			query = """
			DELETE d2s FROM {0}_Data2Specimen d2s
			INNER JOIN specimen_temp_table st
			ON st.id = d2s.specimen_id
			INNER JOIN {0}_Data d
			ON d2s.data_id = d.id
			WHERE d.field_id IN ({1})
			""".format(self.db_suffix, ', '.join(placeholders))
			
			self.cur.execute(query, field_ids)
			self.con.commit()
			
			self.delete_unconnected_data()
		return


	def delete_coordinates(self, before = None, after = None):
		try:
			before = int(before)
		except:
			before = None
		try:
			after = int(after)
		except:
			after = None
		
		params = []
		whereclauses = []
		
		if after is not None:
			whereclauses.append('s.CollectionYear > %s')
			params.append(after)
		if before is not None:
			whereclauses.append('s.CollectionYear < %s')
			params.append(before)
		
		whereclause = ''
		if len(whereclauses) > 0:
			whereclause = 'WHERE ' + ' AND '.join(whereclauses)
		
		"""
		query = "
		UPDATE {0}_Specimen s
		INNER JOIN specimen_temp_table st
		ON st.id = s.id
		SET s.event_id = NULL
		{1}
		;".format(self.db_suffix, whereclause)
		"""
		
		query = """
		UPDATE {0}_Geo g
		INNER JOIN {0}_Specimen s ON g.specimen_id = s.id
		INNER JOIN specimen_temp_table st
		ON st.id = s.id
		SET g.lat = NULL,
		g.lon = NULL
		{1}
		;""".format(self.db_suffix, whereclause)
		
		self.cur.execute(query, params)
		self.con.commit()
		
		return


	def old_embargo_event_but_country_after_1992(self):
		query = """
		DELETE d2s FROM {0}_Data2Specimen d2s
		INNER JOIN specimen_temp_table st
		ON st.id = d2s.specimen_id
		INNER JOIN {0}_Data d
		ON d2s.data_id = d.id
		INNER JOIN {0}_Specimen cs 
		ON cs.id = st.id
		WHERE d.field_id IN (3, 4, 5, 6, 9, 10, 11, 13, 14, 16, 18, 26)
		AND (cs.CollectionYear IS NULL OR cs.CollectionYear > 1992)
		""".format(self.db_suffix)
		
		self.cur.execute(query)
		self.con.commit()
		
		self.delete_unconnected_data()
		return


	def delete_unconnected_data(self):
		query = """
		DELETE d FROM {0}_Data d
		LEFT JOIN {0}_Data2Specimen d2s
		ON d2s.data_id = d.id
		WHERE d2s.id IS NULL
		""".format(self.db_suffix)
		
		self.cur.execute(query)
		self.con.commit()
		return
	'''
	
