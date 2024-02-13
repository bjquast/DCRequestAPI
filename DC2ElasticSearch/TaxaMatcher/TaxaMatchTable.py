#!/usr/bin/env python
# -*- coding: utf8 -*-

import pudb

import logging
import logging.config

logger = logging.getLogger('elastic_indexer')
querylog = logging.getLogger('query')



class TaxaMatchTable():
	"""
	The class uses the data available for taxa in _Taxa table to compare them with 
	the given taxon names in the data comming from specimen
	"""
	
	def __init__(self, tempdb_con, taxamergerdb, specimentemptable):
		
		self.dbcon = tempdb_con
		
		self.cur = self.dbcon.getCursor()
		self.con = self.dbcon.getConnection()
		
		self.taxamergerdb = taxamergerdb
		
		self.taxamergetable = "`{0}`.TaxaMergeTable".format(self.taxamergerdb)
		self.taxarelationtable = "`{0}`.TaxaResultingRelationTable".format(self.taxamergerdb)
		
		self.synonymsmergetable = "`{0}`.TaxaSynonymsMergeTable".format(self.taxamergerdb)
		self.specimentable = specimentemptable
		
		self.createTempTable()


	def matchTaxaByTaxonNameURI(self):
		'''
		TODO: this method is completely outside the rest of the TaxaMatchTable structure
		must be made clear for the reader by moving it into an extra module
		'''
		#pudb.set_trace()
		
		
		query = """
		UPDATE `{0}` cs
		INNER JOIN {1} mt
		ON (cs.TaxonNameURI_sha = mt.TaxonNameURI_sha)
		SET 
			cs.taxon_id = mt.id,
			cs.taxon = mt.taxon,
			cs.author = mt.author,
			cs.`rank` = mt.`rank`,
			cs.FamilyCache = mt.familyCache,
			cs.OrderCache = mt.orderCache
		;""".format(self.specimentable, self.taxamergetable, self.taxarelationtable)
		
		querylog.debug(query)
		self.cur.execute(query)
		self.con.commit()
		
		return
		
		
	def matchSynonymsByTaxonNameURI(self):
		query = """
		UPDATE `{0}` cs
		INNER JOIN {1} sm
		ON (cs.TaxonNameURI_sha = sm.TaxonNameURI_sha)
		INNER JOIN {2} mt
		ON (sm.syn_taxon_id = mt.id)
		SET 
			cs.taxon_id = mt.id,
			cs.taxon = mt.taxon,
			cs.author = mt.author,
			cs.`rank` = mt.`rank`,
			cs.FamilyCache = mt.familyCache,
			cs.OrderCache = mt.orderCache
		;""".format(self.specimentable, self.synonymsmergetable, self.taxamergetable)
		
		querylog.debug(query)
		self.cur.execute(query)
		self.con.commit()
		
		return
		


	def createTempTable(self):
		query = """
		DROP -- TEMPORARY 
		TABLE IF EXISTS taxonmatcher;
		;"""
		querylog.debug(query)
		self.cur.execute(query)
		self.con.commit()
		
		query = """
		CREATE -- TEMPORARY 
		TABLE taxonmatcher
		(
		`specimen_id` varchar(255),
		`scientificName` varchar(255),
		`taxon_name` varchar(255),
		`authorship` varchar(255),
		`genus_name` varchar(255),
		`family_name` varchar(255),
		`order_name` varchar(255),
		`regnum_name` varchar(255),
		KEY `specimen_id` (`specimen_id`),
		KEY `scientificName` (`scientificName`),
		KEY `taxon_name` (`taxon_name`),
		KEY `authorship` (authorship),
		KEY `genus_name` (`genus_name`),
		KEY `family_name` (`family_name`),
		KEY `order_name` (`order_name`),
		KEY `regnum_name` (`regnum_name`)
		)
		;
		"""
		querylog.debug(query)
		self.cur.execute(query)
		self.con.commit()
		
		
		# all matched taxa of the current set will be stored in matchingresults table
		query = """
		DROP TEMPORARY 
		TABLE IF EXISTS matchingresults;
		;"""
		querylog.debug(query)
		self.cur.execute(query)
		self.con.commit()
		
		query = """
		CREATE TEMPORARY
		TABLE matchingresults
		(
		`specimen_id` varchar(255),
		`taxon_id` INT(10),
		`taxon` varchar(255),
		`author` varchar(255),
		`rank` varchar(50),
		KEY `specimen_id` (`specimen_id`)
		)
		;
		"""
		querylog.debug(query)
		self.cur.execute(query)
		self.con.commit()
		
		

	
	
	def insertIntoTempTable(self, placeholderstring, values):
		query = """
		INSERT INTO taxonmatcher
		(
			`specimen_id`,
			`scientificName`,
			`taxon_name`,
			`authorship`,
			`genus_name`,
			`family_name`,
			`order_name`,
			`regnum_name`
		)
		VALUES {0}
		;
		""".format(placeholderstring)
		
		querylog.debug(query)
		querylog.debug(values)
		self.cur.execute(query, values)
		self.con.commit()
		return
	
	
	def deleteMatched(self):
		query = """
		DELETE tm FROM taxonmatcher tm 
		INNER JOIN matchingresults r ON(tm.specimen_id = r.specimen_id)
		;
		"""
		querylog.debug(query)
		self.cur.execute(query)
		self.con.commit()
		return
	
	
	def matchScientificNameInFamily(self):
		query = """
		INSERT INTO matchingresults
		SELECT tm.specimen_id, mt.`id`, mt.`taxon`, mt.`author`, mt.`rank`
		FROM taxonmatcher tm
		INNER JOIN {0} mt ON (tm.taxon_name = mt.taxon AND tm.authorship = mt.author AND tm.family_name = mt.familyCache)
		 -- prevent that a scientificName is taken that occurs more than once
		INNER JOIN (SELECT COUNT(tm.specimen_id) AS matchcount, tm.specimen_id 
			FROM taxonmatcher tm
			INNER JOIN {0} mt ON (tm.taxon_name = mt.taxon AND tm.authorship = mt.author AND tm.family_name = mt.familyCache)
			GROUP BY specimen_id
			) tc 
		ON tc.specimen_id = tm.specimen_id
		WHERE tm.taxon_name != '' AND tm.authorship != '' AND tc.matchcount = 1
		;
		""".format(self.taxamergetable)
		querylog.debug(query)
		self.cur.execute(query)
		self.con.commit()
		
		self.deleteMatched()
		return
	
	
	def matchScientificNameInRegnum(self):
		query = """
		INSERT INTO matchingresults
		SELECT tm.specimen_id, mt.`id`, mt.`taxon`, mt.`author`, mt.`rank`
		FROM taxonmatcher tm
		INNER JOIN {0} mt ON (tm.taxon_name = mt.taxon AND tm.authorship = mt.author AND tm.regnum_name = mt.regnumCache)
		 -- prevent that a scientificName is taken that occurs more than once
		INNER JOIN (SELECT COUNT(tm.specimen_id) AS matchcount, tm.specimen_id 
			FROM taxonmatcher tm
			INNER JOIN {0} mt ON (tm.taxon_name = mt.taxon AND tm.authorship = mt.author AND tm.regnum_name = mt.regnumCache)
			GROUP BY specimen_id
			) tc 
		ON tc.specimen_id = tm.specimen_id
		WHERE tm.taxon_name != '' AND tm.authorship != '' AND tc.matchcount = 1
		;
		""".format(self.taxamergetable)
		#querylog.debug(query)
		self.cur.execute(query)
		self.con.commit()
		
		self.deleteMatched()
		return
	
	
	def matchScientificNameInOrderAndRegnum(self):
		query = """
		INSERT INTO matchingresults
		SELECT tm.specimen_id, mt.`id`, mt.`taxon`, mt.`author`, mt.`rank`
		FROM taxonmatcher tm
		INNER JOIN {0} mt ON (tm.taxon_name = mt.taxon AND tm.authorship = mt.author AND tm.order_name = mt.OrderCache AND tm.regnum_name = mt.regnumCache)
		 -- prevent that a scientificName is taken that occurs more than once
		INNER JOIN (SELECT COUNT(tm.specimen_id) AS matchcount, tm.specimen_id 
			FROM taxonmatcher tm
			INNER JOIN {0} mt ON (tm.taxon_name = mt.taxon AND tm.authorship = mt.author AND tm.order_name = mt.OrderCache AND tm.regnum_name = mt.regnumCache)
			GROUP BY specimen_id
			) tc 
		ON tc.specimen_id = tm.specimen_id
		WHERE tm.taxon_name != '' AND tm.authorship != '' AND tc.matchcount = 1
		;
		""".format(self.taxamergetable)
		querylog.debug(query)
		self.cur.execute(query)
		self.con.commit()
		
		self.deleteMatched()
		return


	def matchTaxonNameInRegnum(self):
		query = """
		INSERT INTO matchingresults
		SELECT tm.specimen_id, mt.`id`, mt.`taxon`, mt.`author`, mt.`rank`
		FROM taxonmatcher tm
		INNER JOIN {0} mt ON (tm.taxon_name = mt.taxon AND tm.regnum_name = mt.regnumCache)
		 -- prevent that a taxon is taken that occurs more than once
		INNER JOIN (SELECT COUNT(tm.specimen_id) AS matchcount, tm.specimen_id 
			FROM taxonmatcher tm
			INNER JOIN {0} mt ON (tm.taxon_name = mt.taxon AND tm.regnum_name = mt.regnumCache)
			GROUP BY specimen_id
			) tc 
		ON tc.specimen_id = tm.specimen_id
		WHERE tm.taxon_name != '' AND tc.matchcount = 1
		;
		""".format(self.taxamergetable)
		#querylog.debug(query)
		self.cur.execute(query)
		self.con.commit()
		
		self.deleteMatched()
		return


	def matchTaxonNameInOrderAndRegnum(self):
		query = """
		INSERT INTO matchingresults
		SELECT tm.specimen_id, mt.`id`, mt.`taxon`, mt.`author`, mt.`rank`
		FROM taxonmatcher tm
		INNER JOIN {0} mt ON (tm.taxon_name = mt.taxon AND tm.order_name = mt.OrderCache AND tm.regnum_name = mt.regnumCache)
		 -- prevent that a taxon is taken that occurs more than once
		INNER JOIN (SELECT COUNT(tm.specimen_id) AS matchcount, tm.specimen_id 
			FROM taxonmatcher tm
			INNER JOIN {0} mt ON (tm.taxon_name = mt.taxon AND tm.order_name = mt.OrderCache AND tm.regnum_name = mt.regnumCache)
			GROUP BY specimen_id
			) tc 
		ON tc.specimen_id = tm.specimen_id
		WHERE tm.taxon_name != '' AND tc.matchcount = 1
		;
		""".format(self.taxamergetable)
		querylog.debug(query)
		self.cur.execute(query)
		self.con.commit()
		
		self.deleteMatched()
		return


	def matchTaxonNameInFamily(self):
		query = """
		INSERT INTO matchingresults
		SELECT tm.specimen_id, mt.`id`, mt.`taxon`, mt.`author`, mt.`rank`
		FROM taxonmatcher tm
		INNER JOIN {0} mt ON (tm.taxon_name = mt.`taxon` AND tm.family_name = mt.familyCache)
		 -- prevent that a taxon_name is taken that occurs more than once
		INNER JOIN (SELECT COUNT(tm.specimen_id) AS matchcount, tm.specimen_id 
			FROM taxonmatcher tm
			INNER JOIN {0} mt ON (tm.taxon_name = mt.`taxon` AND tm.family_name = mt.familyCache)
			GROUP BY specimen_id
			) tc
		ON tc.specimen_id = tm.specimen_id
		WHERE tm.taxon_name != '' AND tc.matchcount = 1
		;
		""".format(self.taxamergetable)
		querylog.debug(query)
		self.cur.execute(query)
		self.con.commit()
		
		self.deleteMatched()
		return


	def matchSynonymInFamily(self):
		query = """
		INSERT INTO matchingresults
		SELECT tm.specimen_id, mt.`id`, mt.`taxon`, mt.`author`, mt.`rank`
		FROM taxonmatcher tm
		INNER JOIN {0} st ON (tm.`taxon_name` = st.`taxon`)
		INNER JOIN {1} mt ON (st.syn_taxon_id = mt.id AND tm.family_name = mt.familyCache)
		 -- prevent that a taxon name is taken that occurs more than once
		INNER JOIN (SELECT COUNT(tm.specimen_id) AS matchcount, tm.specimen_id 
			FROM taxonmatcher tm
			INNER JOIN {0} st ON (tm.`taxon_name` = st.`taxon`)
			INNER JOIN {1} mt ON (st.syn_taxon_id = mt.id AND tm.family_name = mt.familyCache)
			GROUP BY specimen_id
			) tc 
		ON tc.specimen_id = tm.specimen_id
		WHERE tm.taxon_name != '' AND tc.matchcount = 1
		;
		""".format(self.synonymsmergetable, self.taxamergetable)
		querylog.debug(query)
		self.cur.execute(query)
		self.con.commit()
		
		self.deleteMatched()
		return


	def matchSynonymToScientificName(self):
		query = """
		INSERT INTO matchingresults
		SELECT tm.specimen_id, mt.`id`, mt.`taxon`, mt.`author`, mt.`rank`
		FROM taxonmatcher tm
		INNER JOIN {0} st ON (tm.`taxon_name` = st.`taxon` AND tm.authorship = st.author)
		INNER JOIN {1} mt ON (st.syn_taxon_id = mt.id)
		WHERE tm.taxon_name != '' AND tm.authorship != ''
		;
		""".format(self.synonymsmergetable, self.taxamergetable)
		querylog.debug(query)
		self.cur.execute(query)
		self.con.commit()
		
		self.deleteMatched()
		return


	def matchGenusNameInFamilyAndRegnum(self):
		query = """
		INSERT INTO matchingresults
		SELECT tm.specimen_id, mt.`id`, mt.`taxon`, mt.`author`, mt.`rank`
		FROM taxonmatcher tm
		INNER JOIN {0} mt ON (tm.genus_name = mt.`taxon` AND tm.family_name = mt.familyCache AND tm.regnum_name = mt.regnumCache)
		WHERE tm.genus_name != ''
		;
		""".format(self.taxamergetable)
		#querylog.debug(query)
		self.cur.execute(query)
		self.con.commit()
		
		self.deleteMatched()
		return
	
	
	def matchGenusNameInFamilyOrderRegnum(self):
		query = """
		INSERT INTO matchingresults
		SELECT tm.specimen_id, mt.`id`, mt.`taxon`, mt.`author`, mt.`rank`
		FROM taxonmatcher tm
		INNER JOIN {0} mt ON (tm.genus_name = mt.`taxon` AND tm.family_name = mt.familyCache AND tm.order_name = mt.OrderCache AND tm.regnum_name = mt.regnumCache)
		WHERE tm.genus_name != ''
		;
		""".format(self.taxamergetable)
		querylog.debug(query)
		self.cur.execute(query)
		self.con.commit()
		
		self.deleteMatched()
		return
	
	
	def matchFamilyInRegnum(self):
		query = """
		INSERT INTO matchingresults
		SELECT tm.specimen_id, mt.`id`, mt.`taxon`, mt.`author`, mt.`rank`
		FROM taxonmatcher tm
		INNER JOIN {0} mt ON (tm.family_name = mt.`taxon` AND tm.family_name = mt.familyCache AND tm.regnum_name = mt.regnumCache)
		WHERE tm.genus_name != ''
		;
		""".format(self.taxamergetable)
		#querylog.debug(query)
		self.cur.execute(query)
		self.con.commit()
		
		self.deleteMatched()
		return
	
	
	def matchFamilyInOrderAndRegnum(self):
		query = """
		INSERT INTO matchingresults
		SELECT tm.specimen_id, mt.`id`, mt.`taxon`, mt.`author`, mt.`rank`
		FROM taxonmatcher tm
		INNER JOIN {0} mt ON (tm.family_name = mt.`taxon` AND tm.family_name = mt.familyCache AND tm.order_name = mt.OrderCache AND tm.regnum_name = mt.regnumCache)
		WHERE tm.genus_name != ''
		;
		""".format(self.taxamergetable)
		querylog.debug(query)
		self.cur.execute(query)
		self.con.commit()
		
		self.deleteMatched()
		return
	
	
	def matchTaxa(self):
		self.matchScientificNameInFamily()
		self.matchTaxonNameInFamily()
		self.matchSynonymInFamily()
		self.matchSynonymToScientificName()
		
		self.matchGenusNameInFamilyOrderRegnum()
		
		self.matchFamilyInOrderAndRegnum()
		self.matchScientificNameInOrderAndRegnum()
		self.matchTaxonNameInOrderAndRegnum()
		
		#self.matchGenusNameInFamilyAndRegnum()
		
		self.matchScientificNameInRegnum()
		#self.matchTaxonNameInRegnum()
		#self.matchFamilyInRegnum()
		
		return
		
		
	def updateTaxonIDsInSpecimens(self):
		query = """
		 -- after matchTaxa method matchingresults holds the ids of specimens for that a taxon have been found
		UPDATE `{0}` s
		INNER JOIN matchingresults mr
			ON (s._id = mr.specimen_id)
		SET s.taxon_id = mr.taxon_id
		;""".format(self.specimentable)
		querylog.debug(query)
		self.cur.execute(query)
		self.con.commit()
		
		'''
		query = """
		 -- after matchTaxa method taxonmatcher holds the ids of specimens that could not be matched with a taxon
		UPDATE `{0}` s
		INNER JOIN taxonmatcher tm
			ON(s._id = tm.specimen_id)
		SET s.taxon_id = NULL
		;""".format(self.specimentable)
		querylog.debug(query)
		self.cur.execute(query)
		self.con.commit()
		'''
		
		return
	
	
	def updateTaxonAuthorAndRankInSpecimens(self):
		query = """
		 -- after matchTaxa method matchingresults holds the ids of specimens for that a taxon have been found
		UPDATE `{0}` s
		INNER JOIN matchingresults mr
			ON (s._id = mr.specimen_id)
		SET s.taxon = mr.taxon, 
		s.author = mr.author,
		s.`rank` = mr.`rank`
		;""".format(self.specimentable)
		self.cur.execute(query)
		self.con.commit()


	def deleteTempTableData(self):
		query = """
		DELETE FROM taxonmatcher
		;"""
		querylog.debug(query)
		self.cur.execute(query)
		self.con.commit()
		
		query = """
		DELETE FROM matchingresults
		;"""
		querylog.debug(query)
		self.cur.execute(query)
		self.con.commit()
		
		return

	# taxa matched and taxa not matched are not stored in DCRequestAPI?!
	
	'''
	
	
	def createTaxaNotMatchedTable(self):
		query = """
		CREATE TABLE IF NOT EXISTS taxa_not_matched
		(
		`specimen_id` INT(10),
		`scientificName` varchar(255),
		`taxon_name` varchar(255),
		KEY `specimen_id` (`specimen_id`),
		KEY `scientificName` (`scientificName`),
		KEY `taxon_name` (`taxon_name`)
		)
		;
		"""
		querylog.debug(query)
		self.cur.execute(query)
		self.con.commit()


	def createTaxaMatchedTable(self):
		query = """
		CREATE TABLE IF NOT EXISTS taxa_matched
		(
		`specimen_id` INT(10),
		`taxon_id` INT(10),
		`taxon_name` varchar(255),
		KEY `specimen_id` (`specimen_id`),
		KEY `taxon_id` (taxon_id),
		KEY `taxon_name` (`taxon_name`)
		)
		;
		"""
		querylog.debug(query)
		self.cur.execute(query)
		self.con.commit()
	
	
	def appendTaxaNotMatched(self, taxa_not_matched, placeholders):
		values = []
		for taxon_not_matched in taxa_not_matched:
			values.extend(taxon_not_matched)
		
		query = """
		INSERT INTO taxa_not_matched
		(
			`specimen_id`,
			`scientificName`,
			`taxon_name`
		)
		VALUES {0}
		;
		""".format(', '.join(placeholders))
		
		querylog.debug(query)
		querylog.debug(values)
		self.cur.execute(query, values)
		self.con.commit()
		return
	'''


	# matched taxa should not be marked in TaxaMergeTable
	'''
	def markMatchedTaxaInMergeTable(self):
		query = """
		 -- after matchTaxa method matchingresults holds the ids of taxa for that have been found in specimens
		UPDATE {0} mt
		INNER JOIN (
			SELECT DISTINCT `taxon_id`
			FROM matchingresults
		) mr
		ON (mt.id = mr.`taxon_id`)
		SET mt.matched_in_specimens = 1
		""".format(self.taxamergetable)
		querylog.debug(query)
		self.cur.execute(query)
		self.con.commit()
	'''
