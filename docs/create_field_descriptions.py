import pudb
import json

from ElasticSearch.FieldConfig import FieldConfig
from ElasticSearch.ES_Connector import ES_Connector


class FieldDescriptions():
	def __init__(self):
		pass

	def write_field_descriptions_json(self):
		fielddefs = FieldConfig().fielddefinitions
		descriptions = {}
		for field in fielddefs:
			description = fielddefs[field].get('description', None)
			if description:
				descriptions[field] = description
		
		with open('./docs/field_descriptions.json', 'w') as fh:
			json.dump(descriptions, fh, indent=2, sort_keys=True)
		return


class ElasticMapping():
	def __init__(self):
		self.index = 'iuparts'
		self.client = ES_Connector().client

	def write_es_mapping_json(self):
		mapping = dict(self.client.indices.get_mapping(index=self.index))
		with open('./docs/iuparts_mapping.json', 'w') as fh:
			json.dump(mapping, fh, indent=2, sort_keys=True)
		return


if __name__ == "__main__":
	#pudb.set_trace()
	
	FieldDescriptions().write_field_descriptions_json()
	ElasticMapping().write_es_mapping_json()
	
	print('json files for mapping and field description completed')
	exit(0)
