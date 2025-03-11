import pudb

from ElasticSearch.FieldDefinitions import FieldDefinitions


class HierarchyAggregations():
	def __init__(self, aggregations = {}):
		self.aggregations = aggregations
		
		fielddefs = FieldDefinitions()
		self.hierarchy_fields = fielddefs.hierarchy_query_fields
		
		self.hierarchies_dict = {}


	def calcHierarchiesDict(self):
		for agg_name in self.aggregations:
			if agg_name in self.hierarchy_fields:
				self.hierarchies_dict[agg_name] = {}
				buckets = self.aggregations[agg_name]
				for bucket in buckets:
					bucket['path_elements'] = [element.strip() for element in bucket['key'].split('>')]
					
					self.addPathElements(self.hierarchies_dict[agg_name], bucket)
		
		return self.hierarchies_dict


	def addPathElements(self, subdict, bucket):
		element = bucket['path_elements'].pop(0)
		#if element == 'Annelida':
		#	pudb.set_trace()
		if element not in subdict:
			subdict[element] = {}
			if len(bucket['path_elements']) == 0:
				del bucket['path_elements']
				subdict[element] = bucket
				subdict[element]['taxon'] = element
				return
			else:
				self.addPathElements(subdict[element], bucket)
		else:
			if len(bucket['path_elements']) > 0:
				self.addPathElements(subdict[element], bucket)
			else:
				# add key and doc_count whe not added before
				# because the bucket has not been on the end of the path_elements list before
				subdict[element]['key'] = bucket['key']
				subdict[element]['doc_count'] = bucket['doc_count']
				subdict[element]['taxon'] = element
				return
		return


