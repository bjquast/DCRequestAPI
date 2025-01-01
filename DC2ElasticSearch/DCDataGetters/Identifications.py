
import pudb

import logging, logging.config
logging.config.fileConfig('logging.conf')
logger = logging.getLogger('elastic_indexer')
log_query = logging.getLogger('query')


class Identifications():
	def __init__(self, datagetter):
		self.datagetter = datagetter
		
		self.cur = self.datagetter.cur
		self.con = self.datagetter.con


	def get_data_page(self):
		
		query = """
		SELECT DISTINCT
		[rownumber],
		idstemp.[idshash] AS [_id],
		i.IdentificationSequence AS IdentificationSequenceID,
		CONVERT(NVARCHAR, i.IdentificationDate, 120) AS [IdentificationDate],
		i.TaxonomicName,
		i.VernacularTerm,
		i.NameURI AS TaxonNameURI,
		i.TypeStatus,
		i.TypeNotes,
		i.ResponsibleName,
		 -- columns for Embargo settings comming from DiversityProjects, a LIB specific idea, may not implemented elsewhere
		CASE WHEN idstemp.[embargo_anonymize_determiner] = 1 THEN 'true' ELSE 'false' END AS [embargo_anonymize_determiner]
		FROM [#temp_iu_part_ids] idstemp
		INNER JOIN IdentificationUnit iu 
		ON iu.[CollectionSpecimenID] = idstemp.[CollectionSpecimenID] AND iu.[IdentificationUnitID] = idstemp.[IdentificationUnitID]
		INNER JOIN [Identification] i
		ON i.[CollectionSpecimenID] = iu.[CollectionSpecimenID] AND i.[IdentificationUnitID] = iu.[IdentificationUnitID]
		ORDER BY [rownumber], i.[IdentificationSequence]
		;"""
		self.cur.execute(query)
		#self.columns = [column[0] for column in self.cur.description]
		
		self.rows = self.cur.fetchall()
		self.rows2dicts()
		self.set_vernaculars_dict()
		
		
		return self.identifications_dict


	def rows2dicts(self):
		self.identifications_dict = {}
		
		for row in self.rows:
			if row[1] not in self.identifications_dict:
				self.identifications_dict[row[1]] = {}
				self.identifications_dict[row[1]]['Identifications'] = []
				self.identifications_dict[row[1]]['VernacularTerms'] = []
				self.identifications_dict[row[1]]['TypeStatus'] = []
			
			identification = {
				'IdentificationSequenceID': row[2],
				'IdentificationDate': row[3],
				'TaxonomicName': row[4],
				'VernacularTerm': row[5],
				'TaxonNameURI': row[6],
				'TypeStatus': row[7],
				'TypeNotes': row[8],
				'ResponsibleName': row[9],
				'embargo_anonymize_determiner': row[10]
			}
			
			self.identifications_dict[row[1]]['Identifications'].append(identification)
			
			'''
			if row[5] is not None and row[5] != '':
				if row[5] not in self.identifications_dict[row[1]]['VernacularTerms']:
					self.identifications_dict[row[1]]['VernacularTerms'].append(row[5])
			'''
			
			if row[7] is not None and row[7] != '':
				if row[7] not in self.identifications_dict[row[1]]['TypeStatus']:
					self.identifications_dict[row[1]]['TypeStatus'].append(row[7])
			
		return


	def set_vernaculars_dict(self):
		self.vernaculars_dict = {}
		
		for row in self.rows:
			if row[1] not in self.vernaculars_dict:
				self.vernaculars_dict[row[1]] = {}
				self.vernaculars_dict[row[1]]['VernacularTerms'] = []
			if row[5] is not None and row[5] != '':
				if row[5] not in self.vernaculars_dict[row[1]]['VernacularTerms']:
					self.vernaculars_dict[row[1]]['VernacularTerms'].append(row[5])
		return












