#!/usr/bin/env python
# -*- coding: utf8 -*-
import re

import pudb

from configparser import ConfigParser

import logging
import logging.config

logging.config.fileConfig('logging.conf')
logger = logging.getLogger('elastic_indexer')
log_queries = logging.getLogger('query')

from .TaxaMatchTable import TaxaMatchTable
from .NamePatternsBotany import NamePatternsBotany
from .NamePatternsZoology import NamePatternsZoology

from DBConnectors.MySQLConnector import MySQLConnector


config = ConfigParser()
config.read('./config.ini')


class TaxaMatcher():
	def __init__(self):
		dbconfig = {
			'host': config.get('taxamergerdb', 'host', fallback = 'localhost'),
			'port': int(config.get('taxamergerdb', 'port', fallback = 3306)),
			'user': config.get('taxamergerdb', 'user'),
			'password': config.get('taxamergerdb', 'password'),
			'database': config.get('taxamergerdb', 'database'),
			'charset': config.get('taxamergerdb', 'charset', fallback = 'utf8mb4')
		}
		
		self.dbcon = MySQLConnector(dbconfig)
		self.cur = self.dbcon.getCursor()
		self.con = self.dbcon.getConnection()
		
		self.specimentable = "SpecimenTempTable"
		
		self.namepatterns_botany = NamePatternsBotany()
		self.namepatterns_zoology = NamePatternsZoology()
		
		# fix for our Ichthyology department that added Eschmeyer chapter numbers to the family names
		self.eschmeyerpattern = re.compile(r'\s*\-?\d+\s*$')
		
		self.matchingtable = TaxaMatchTable(self.dbcon, dbconfig['database'], self.specimentable)
		
		#self.setWithholdForUnmatchedSpecimens()
		#self.deleteUnMatchedSpecimens()

	'''
	This is the target table where the results of the matching are inserted
	A similar temporary table is genereated within TaxaMatchTable which is used for the matching process
	After thinking about it, a second table is needed for the matching process as the results of
	the calculateNames() method has to be stored in any way and the alternative would be to create a 
	temporary table for updating the target table with the names gathered by calculateNames
	'''
	
	def createSpecimenTempTable(self):
		query = """
		DROP TEMPORARY 
		TABLE IF EXISTS {0}
		;""".format(self.specimentable)
		self.cur.execute(query)
		self.con.commit()
		
		query = """
		CREATE TEMPORARY 
		TABLE `{0}` (
		`_id` VARCHAR(255) NOT NULL,
		`taxon_id` INT,
		`taxon` VARCHAR(255),
		`author` VARCHAR(255),
		`rank` VARCHAR(50),
		`LastIdentificationCache` VARCHAR(255),
		`FamilyCache` VARCHAR(255),
		`OrderCache` VARCHAR(255),
		`RegnumCache` VARCHAR(50),
		`TaxonomicGroup` VARCHAR(50),
		`TaxonNameURI` VARCHAR(255),
		`TaxonNameURI_sha` VARCHAR(255),
		`PartAccessionNumber` VARCHAR(255),
		PRIMARY KEY(`_id`),
		KEY (`taxon_id`),
		KEY (`taxon`),
		KEY (`LastIdentificationCache`),
		KEY (`FamilyCache`),
		KEY (`OrderCache`),
		KEY (`RegnumCache`),
		KEY (`TaxonomicGroup`),
		KEY (`TaxonNameURI_sha`)
		) DEFAULT CHARSET=utf8mb4
		;""".format(self.specimentable)
		
		self.cur.execute(query)
		self.con.commit()
		return


	def fillSpecimenTempTable(self, valuelists):
		values = []
		placeholderstrings = []
		if len(valuelists) <= 0:
			return
		
		for valuelist in valuelists:
			values.extend(valuelist)
			placeholderstrings.append('(%s, %s, %s, %s, %s, %s, %s, %s)')
		
		query = """
		INSERT INTO `{0}` (
			`_id`,
			`LastIdentificationCache`,
			`FamilyCache`,
			`OrderCache`,
			`TaxonomicGroup`,
			`TaxonNameURI`,
			`TaxonNameURI_sha`,
			`PartAccessionNumber`
		)
		VALUES {1}
		;""".format(self.specimentable, ', '.join(placeholderstrings))
		
		self.cur.execute(query, values)
		self.con.commit()
		return


	def setRemainingSpecimen(self):
		self.remaining_specimen = []
		query = """
		SELECT 
		`_id`,
		`LastIdentificationCache`,
		`FamilyCache`,
		`OrderCache`,
		`TaxonomicGroup`,
		`PartAccessionNumber`
		FROM {0}
		WHERE `taxon_id` IS NULL
		;""".format(self.specimentable)
		
		self.cur.execute(query)
		rows = self.cur.fetchall()
		for row in rows:
			self.remaining_specimen.append(list(row))
		
		return


	def matchTaxa(self):
		#pudb.set_trace()
		logger.info("TaxaMatcher: started matching")
		
		logger.info('TaxaMatcher: match accepted names by TaxonNameURI')
		self.matchingtable.matchTaxaByTaxonNameURI()
		
		logger.info('TaxaMatcher: match synonyms by TaxonNameURI')
		self.matchingtable.matchSynonymsByTaxonNameURI()
		
		self.setRemainingSpecimen()
		self.calculateNames()
		
		if len(self.values) > 0:
			self.matchingtable.deleteTempTableData()
			self.matchingtable.insertIntoTempTable(self.placeholderstring, self.values)
			self.matchingtable.matchTaxa()
			self.matchingtable.updateTaxonIDsInSpecimens()
			self.matchingtable.updateTaxonAuthorAndRankInSpecimens()
		
		return


	def calculateNames(self):
		self.values = []
		self.placeholderstrings = []
		
		for specimenrow in self.remaining_specimen:
			specimen_id = specimenrow[0]
			taxonstring = specimenrow[1]
			
			familycache = specimenrow[2]
			ordercache = specimenrow[3]
			taxonomicgroup = specimenrow[4]
			
			genus_name = None
			
			if familycache is not None:
				# clean families for our Ichthyology department (familyname + Eschmeyer chapter number)
				familycache = self.eschmeyerpattern.sub('', familycache)
			
			
			#if taxonstring.startswith('Chloris chloris'): 
			#if specimen_id == 983468:
			#	pudb.set_trace()
			
			# this should not happen?
			if (taxonstring is None or taxonstring == ''):
				if (familycache is not None) and (familycache != ''):
					taxonstring = familycache
			
			if taxonomicgroup in ['amphibian', 'animal', 'arthropod', 'bird', 'cnidaria', 'Coleoptera', 'Diptera', 'echinoderm', 'evertebrate', 'fish', 'Heteroptera', 'Hymenoptera', 'insect', 'Lepidoptera', 'mammal', 'mollusc', 'reptile', 'spider', 'vertebrate']:
				taxondict = self.namepatterns_zoology.matchTaxonName(taxonstring)
				kingdom = 'Animalia'
			elif taxonomicgroup in ['plant', 'alga', 'algae', 'bryophyte']:
				taxondict = self.namepatterns_botany.matchTaxonName(taxonstring)
				kingdom = 'Plantae'
			elif taxonomicgroup in ['fungus', 'lichen']:
				taxondict = self.namepatterns_botany.matchTaxonName(taxonstring)
				kingdom = 'Fungi'
			elif taxonomicgroup in ['myxomycete']:
				taxondict = self.namepatterns_botany.matchTaxonName(taxonstring)
				kingdom = 'Protozoa'
			else:
				try:
					logger.debug('kingdom not found for taxonomicgroup: {0}'.format(taxonomicgroup))
				except:
					logger.debug('kingdom not found for taxonomicgroup: ')
					logger.debug(taxonomicgroup)
				continue
			
			if taxondict is None:
				accessionnumber = specimenrow[5]
				logger.debug('regex with scientificname failed: {0}, {1}, {2}'.format(specimen_id, accessionnumber, taxonstring))
				continue
			
			genus_name = taxondict['genus_or_higher_taxon']
			authorship = taxondict['basionym_authorship']
			taxon_name_parts = [
				taxondict['genus_or_higher_taxon'], taxondict['species'], taxondict['infraspecific_epithet']
			]
			taxon_name = ''
			for part in taxon_name_parts:
				if part is not None:
					taxon_name = taxon_name + ' ' + part
			taxon_name = taxon_name.strip()
			
			if len(taxon_name) <= 0:
				taxon_name = None
			
			scientific_name = taxonstring
			
			row = [specimen_id, scientific_name, taxon_name, authorship, genus_name, familycache, ordercache, kingdom]
			self.values.extend(row)
			self.placeholderstrings.append("(%s, %s, %s, %s, %s, %s, %s, %s)")
		
		self.placeholderstring = ", ".join(self.placeholderstrings)
		
		return


	def getMatchedTaxaDict(self):
		matched_taxa_dict = {}
		
		query = """
		SELECT cs.`_id`, cs.taxon, cs.author, cs.`rank`,
		COALESCE(mt.TaxonNameURI, CONCAT('taxamerger_id_', mt.id)) AS TaxonNameURI,
		mt.TaxonURL,
		anc.taxon AS ancestor_taxon, anc.`rank` AS ancestor_taxon_rank, 
		COALESCE(anc.`TaxonNameURI`, CONCAT('taxamerger_id_', anc.id)) AS ancestor_taxon_uri, 
		anc.`TaxonURL` AS ancestor_taxon_url, anc.taxon_tree_level -1 AS ancestor_taxon_tree_level,
		COALESCE(p_anc.`TaxonNameURI`, CONCAT('taxamerger_id_', p_anc.id)) AS ancestors_parent_taxon_uri
		FROM {0} cs
		INNER JOIN {1} mt
		ON mt.id = cs.taxon_id
		INNER JOIN {2} tr
		ON (cs.taxon_id = tr.DescendantID)
		INNER JOIN {1} anc
		ON (anc.id = tr.AncestorID AND anc.taxon != 'root') -- AND anc.id != cs.taxon_id)
		INNER JOIN {1} p_anc
		ON (p_anc.id = anc.parent_id)
		;""".format(self.specimentable, self.matchingtable.taxamergetable, self.matchingtable.taxarelationtable)
		self.cur.execute(query)
		rows = self.cur.fetchall()
		
		for row in rows:
				if row[0] not in matched_taxa_dict:
					matched_taxa_dict[row[0]] = {}
					matched_taxa_dict[row[0]]['MatchedTaxon'] = row[1]
					matched_taxa_dict[row[0]]['MatchedTaxonAuthor'] = row[2]
					matched_taxa_dict[row[0]]['MatchedTaxonRank'] = row[3]
					matched_taxa_dict[row[0]]['MatchedTaxonURI'] = row[4]
					matched_taxa_dict[row[0]]['MatchedTaxonURL'] = row[5]
					
					matched_taxa_dict[row[0]]['MatchedParentTaxa'] = []
					matched_taxa_dict[row[0]]['MatchedParentTaxaURIs'] = []
					matched_taxa_dict[row[0]]['MatchedTaxaTree'] = []
					
				matched_taxa_dict[row[0]]['MatchedParentTaxa'].append(row[6])
				matched_taxa_dict[row[0]]['MatchedParentTaxaURIs'].append(row[8])
				matched_taxa_dict[row[0]]['MatchedTaxaTree'].append({
					'Taxon': row[6], 'Rank': row[7], 'TaxonURI': row[8],
					'TaxonURL': row[9], 'TreeLevel': row[10], 'ParentTaxonURI': row[11]})
		
		return matched_taxa_dict
		
	
	'''
	def setWithholdForUnmatchedSpecimens(self):
		query = """
		UPDATE `{0}_Specimen` s
		SET s.withhold_flag = 1
		WHERE s.`taxon_id` IS NULL
		;
		""".format(self.specimentable)
		self.cur.execute(query)
		self.con.commit()
		return
	'''



	'''
	def removeTaxonIDs(self):
		query = """
		UPDATE {0}
		set `taxon_id` = NULL
		WHERE `taxon_id` IS NOT NULL
		;""".format(self.specimentable)
		self.cur.execute(query)
		self.con.commit()
		return
	
	
	
	
	def setMaxPage(self):
		query = """
		SELECT MAX(id) FROM `{0}`
		;
		""".format(self.specimentable)
		self.cur.execute(query)
		row = self.cur.fetchone()
		if row[0] is None:
			self.maxpage = 0
		elif row[0] <= 0:
			self.maxpage = 0
		else:
			self.maxpage = int(row[0] / self.pagesize + 1)
	
	def initPaging(self):
		self.currentpage = 1
		self.pagingstarted = True
	
	def getNextSpecimenPage(self):
		if self.pagingstarted is False:
			self.initPaging()
		if self.currentpage <= self.maxpage:
			specimens = self.getSpecimenPage(self.currentpage)
			self.currentpage = self.currentpage + 1
			if len(specimens) > 0:
				return specimens
			else:
				# there might be gaps in the primary key column
				while len(specimens) <= 0 and self.currentpage <= self.maxpage:
					specimens = self.getSpecimenPage(self.currentpage)
					self.currentpage = self.currentpage + 1
					if len(specimens) > 0:
						return specimens
				self.pagingstarted = False
				return None
		else:
			self.pagingstarted = False
			return None
	
	def getSpecimenPage(self, page):
		if page % 10 == 0:
			logger.info("TaxaMatcher get specimen page {0} of {1} pages".format(page, self.maxpage))
			
		startrow = ((page-1)*self.pagesize)+1
		lastrow = startrow + self.pagesize-1
		
		parameters = [startrow, lastrow]
		self.specimenquery = """
		SELECT `id`, TRIM(`taxon`) AS `taxon`, TRIM(`FamilyCache`) AS `FamilyCache`, TRIM(`OrderCache`) AS `OrderCache`, `TaxonomicGroup`, SHA2(`TaxonNameURI`, 256), `AccessionNumber` FROM {0}
		WHERE `id` BETWEEN %s AND %s
		AND `taxon_id` IS NULL
		;
		""".format(self.specimentable)
		
		self.cur.execute(self.specimenquery, parameters)
		specimendata = self.cur.fetchall()
		return specimendata
	'''



