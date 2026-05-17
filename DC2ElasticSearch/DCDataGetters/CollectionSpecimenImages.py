
import pudb

import logging, logging.config
logging.config.fileConfig('logging.conf')
logger = logging.getLogger('elastic_indexer')
log_query = logging.getLogger('query')


class CollectionSpecimenImages():
	def __init__(self, datagetter):
		self.datagetter = datagetter
		
		self.cur = self.datagetter.cur
		self.con = self.datagetter.con


	def get_data_page(self):
		
		query = """
		SELECT 
		[rownumber],
		idstemp.[idshash] AS [_id],
		csi.[URI],
		csi.ResourceURI,
		csi.ImageType,
		csi.[Title],
		CONVERT(VARCHAR(MAX), csi.[Description], 0) AS [Description],
		csi.CreatorAgent AS [ImageCreator],
		csi.CopyRightStatement,
		csi.LicenseType,
		csi.LicenseURI,
		csi.LicenseHolder,
		csi.LicenseHolderAgentURI,
		csi.LicenseYear,
		csi.DisplayOrder AS ImageDisplayOrder,
		csi.DataWithholdingReason AS ImageWithholdingReason,
		CASE 
			WHEN csi.[DataWithholdingReason] = '' THEN 'false'
			WHEN csi.[DataWithholdingReason] IS NULL THEN 'false'
			ELSE 'true'
		END AS ImageWithhold
		FROM [#temp_iu_part_ids] idstemp
		INNER JOIN CollectionSpecimenImage csi 
		ON csi.[CollectionSpecimenID] = idstemp.[CollectionSpecimenID] 
			AND csi.[IdentificationUnitID] = idstemp.[IdentificationUnitID]
			AND csi.[SpecimenPartID] = idstemp.[SpecimenPartID]
		UNION 
		SELECT 
		[rownumber],
		idstemp.[idshash] AS [_id],
		csi.[URI],
		csi.ResourceURI,
		csi.ImageType,
		csi.[Title],
		CONVERT(VARCHAR(MAX), csi.[Description], 0) AS [Description],
		csi.CreatorAgent AS [ImageCreator],
		csi.CopyRightStatement,
		csi.LicenseType,
		csi.LicenseURI,
		csi.LicenseHolder,
		csi.LicenseHolderAgentURI,
		csi.LicenseYear,
		csi.DisplayOrder AS ImageDisplayOrder,
		csi.DataWithholdingReason AS ImageWithholdingReason,
		CASE 
			WHEN csi.[DataWithholdingReason] = '' THEN 'false'
			WHEN csi.[DataWithholdingReason] IS NULL THEN 'false'
			ELSE 'true'
		END AS ImageWithhold
		FROM [#temp_iu_part_ids] idstemp
		INNER JOIN CollectionSpecimenImage csi 
		ON csi.[CollectionSpecimenID] = idstemp.[CollectionSpecimenID] 
			AND csi.[IdentificationUnitID] = idstemp.[IdentificationUnitID]
			AND csi.[SpecimenPartID] IS NULL
		UNION
		SELECT 
		[rownumber],
		idstemp.[idshash] AS [_id],
		csi.[URI],
		csi.ResourceURI,
		csi.ImageType,
		csi.[Title],
		CONVERT(VARCHAR(MAX), csi.[Description], 0) AS [Description],
		csi.CreatorAgent AS [ImageCreator],
		csi.CopyRightStatement,
		csi.LicenseType,
		csi.LicenseURI,
		csi.LicenseHolder,
		csi.LicenseHolderAgentURI,
		csi.LicenseYear,
		csi.DisplayOrder AS ImageDisplayOrder,
		csi.DataWithholdingReason AS ImageWithholdingReason,
		CASE 
			WHEN csi.[DataWithholdingReason] = '' THEN 'false'
			WHEN csi.[DataWithholdingReason] IS NULL THEN 'false'
			ELSE 'true'
		END AS ImageWithhold
		FROM [#temp_iu_part_ids] idstemp
		INNER JOIN CollectionSpecimenImage csi 
		ON csi.[CollectionSpecimenID] = idstemp.[CollectionSpecimenID] 
			AND csi.[IdentificationUnitID] IS NULL
			AND csi.[SpecimenPartID] IS NULL
		ORDER BY [rownumber]
		;"""
		self.cur.execute(query)
		self.columns = [column[0] for column in self.cur.description]
		
		self.rows = self.cur.fetchall()
		self.rows2dict()
		
		
		return self.images_dict


	def rows2dict(self):
		self.images_dict = {}
		
		for row in self.rows:
			if row[1] not in self.images_dict:
				self.images_dict[row[1]] = {}
				self.images_dict[row[1]]['Images'] = []
				self.images_dict[row[1]]['NumberOfSpecimenImages'] = 0
				self.images_dict[row[1]]['ImagesAvailable'] = 'available'
				self.images_dict[row[1]]['ImagesWithhold'] = 'true'
				self.images_dict[row[1]]['MediaTypesDict'] = {}
			
			image = {
				'URI': row[2],
				'ResourceURI': row[3],
				'ImageType': row[4],
				'Title': row[5],
				'Description': row[6],
				'ImageCreator': row[7],
				'CopyRightStatement': row[8],
				'LicenseType': row[9],
				'LicenseURI': row[10],
				'LicenseHolder': row[11],
				'LicenseHolderAgentURI': row[12],
				'LicenseYear': row[13],
				'ImageDisplayOrder': row[14],
				'ImageWithholdingReason': row[15],
				'ImageWithhold': row[16]
			}
			
			# set ImagesWithhold flag to 'false' if there is at least one image without an Withhold flag 
			if image['ImageWithhold'] == 'false':
				self.images_dict[row[1]]['ImagesWithhold'] = 'false'
			
			self.images_dict[row[1]]['Images'].append(image)
			self.images_dict[row[1]]['NumberOfSpecimenImages'] += 1
			
			
			# set a nested dict for mediatypes and if the according media are withholded
			if image['ImageType'] not in self.images_dict[row[1]]['MediaTypesDict']:
				self.images_dict[row[1]]['MediaTypesDict'][image['ImageType']] = image['ImageWithhold']
			elif image['ImageWithhold'] == 'false':
				self.images_dict[row[1]]['MediaTypesDict'][image['ImageType']] = image['ImageWithhold']
		
		for hash_id in self.images_dict:
			self.images_dict[hash_id]['MediaTypes'] = []
			for imagetype in self.images_dict[hash_id]['MediaTypesDict']:
				self.images_dict[hash_id]['MediaTypes'].append({'MediaType': imagetype, 'MediaTypeWithhold': self.images_dict[hash_id]['MediaTypesDict'][imagetype]})
			del self.images_dict[hash_id]['MediaTypesDict']
			
			
		return















