import logging
import logging.config
logging.config.fileConfig('logging.conf')
logger = logging.getLogger('elastic_queries')

import pudb

from ElasticSearch.FieldDefinitions import FieldDefinitions
from ElasticSearch.QueryConstructor.QuerySorter import QuerySorter

class TreeQueries(QuerySorter):
	def __init__(self, users_project_ids = [], source_fields = []):
		self.users_project_ids = users_project_ids
		self.source_fields = source_fields
		
		fielddefs = FieldDefinitions()
		if len(self.source_fields) <= 0:
			self.source_fields = fielddefs.tree_query_fields
		
		QuerySorter.__init__(self, fielddefs.fielddefinitions, self.source_fields)
		self.sort_queries_by_definitions()


	def setNestedRootQuery(self, field):
		for field in in self.nested_fields:
			rootquery = {
				"aggs": {
					"{0}_tree".format(field): {
						"nested": {
							"path": self.nested_fields[field]['path']
						}, 
						"aggs": {
							"filter_rank": {
								"filter": {
									"bool": {
										"must": [
											{
												"term": {
													"{0}.TreeLevel".format(self.nested_fields[field]['path']): self.nested_fields[field]['root_level']
												}
											}
										]
									}
								},
								"aggs": {
									"{0}_tree_buckets".format(field): {
										"composite": {
											"size": 500,
											"sources": [
												{
													"Taxon": {
														"terms": {
															"field": self.nested_fields[field]['field_query']
														}
													}
												},
												{
													"TaxonURI": {
														"terms": {
															"field": self.nested_fields[field]['id_field_for_tree']
														}
													}
												}
											]
										}
									}
								}
							}
						}
					}
				}
			}



	def setNestedChildsQuery(self, field, parent_id):
		for field in in self.nested_fields:
			rootquery = {
				"aggs": {
					"{0}_tree".format(field): {
						"nested": {
							"path": self.nested_fields[field]['path']
						}, 
						"aggs": {
							"filter_rank": {
								"filter": {
									"bool": {
										"must": [
											{
												"term": {
													self.nested_fields[field]['id_field_for_tree']: parent_id
												}
											}
										]
									}
								},
								"aggs": {
									"{0}_tree_buckets".format(field): {
										"composite": {
											"size": 500,
											"sources": [
												{
													"Taxon": {
														"terms": {
															"field": self.nested_fields[field]['field_query']
														}
													}
												},
												{
													"TaxonURI": {
														"terms": {
															"field": self.nested_fields[field]['id_field_for_tree']
														}
													}
												}
											]
										}
									}
								}
							}
						}
					}
				}
			}
