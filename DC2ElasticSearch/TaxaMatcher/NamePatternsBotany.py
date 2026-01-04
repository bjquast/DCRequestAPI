import re
import pudb
import argparse



class NamePatternsBotany():
	def __init__(self):
		self.author_prefix_pattern = r'(al|f|j|jr|ms|sr|v|v[ao]n|zu[rm]?|bis|d[aeiou]?|de[nrmls]?|degli|e|l[ae]s?|s|ter|t|y)'
		
		# ?: prevents fetching of the grouped content, can be removed when some additional parts of the name should be fetched
		self.subgenus_pattern = r'(?:\s+(?:(?:notho|n)?(?:subgenus|subgen\.|subg\.))\s+?([×]?[x]?\s?[A-Z\u00C0-\u00D6\u00D8-\u00DEa-z\u00DF-\u00F6\u00F8-\u00FF\-\_]+))?'
		self.sectio_pattern = r'(?:\s+(?:sectio|sect\.)\s+([A-Z\u00C0-\u00D6\u00D8-\u00DEa-z\u00DF-\u00F6\u00F8-\u00FF\-\_]+))?'
		self.subsectio_pattern = r'(?:\s+(?:subsectio|subsect\.)\s+([A-Z\u00C0-\u00D6\u00D8-\u00DEa-z\u00DF-\u00F6\u00F8-\u00FF\-\_]+))?'
		self.series_pattern = r'(?:\s+(?:series|ser\.)\s+([A-Z\u00C0-\u00D6\u00D8-\u00DEa-z\u00DF-\u00F6\u00F8-\u00FF\-\_]+))?'
		self.subseries_pattern = r'(?:\s+(?:subseries|subser\.)\s+([A-Z\u00C0-\u00D6\u00D8-\u00DEa-z\u00DF-\u00F6\u00F8-\u00FF\-\_]+))?'
		
		# the zoological alternative for subgenus combined with species
		#self.subgenus_species_pattern = r'(?:\s+(?:\(([A-Z\u00C0-\u00D6\u00D8-\u00DEa-z\u00DF-\u00F6\u00F8-\u00FF\-\_]+)\)\s*)?((?!{0}[\'\s]+)[×]?[x]?\s?[a-z\u00DF-\u00F6\u00F8-\u00FF\-\_]+))?'.format(self.author_prefix_pattern)
		
		self.species_pattern = r'(?:\s+((?!{0}[\'\s]+)[×]?[x]?\s?[a-z\u00DF-\u00F6\u00F8-\u00FF\-\_]+))?'.format(self.author_prefix_pattern)
		
		self.subspecies_pattern = r'(?:\s+(?:(?:notho|n)?(?:subspecies|subsp\.|ssp\.))\s+([×]?[x]?\s?[a-z\u00DF-\u00F6\u00F8-\u00FF\-\_]+))?'
		self.varietas_pattern = r'(?:\s+(?:(?:notho|n)?(?:varietas|variety|var\.))\s+([×]?[x]?\s?[a-z\u00DF-\u00F6\u00F8-\u00FF\-\_]+))?'
		self.subvarietas_pattern = r'(?:\s+(?:(?:notho|n)?(?:subvarietas|subvariety|subvar\.))\s+([×]?[x]?\s?[a-z\u00DF-\u00F6\u00F8-\u00FF\-\_]+))?'
		self.forma_pattern = r'(?:\s+(?:(?:notho|n)?(?:forma|form|f\.))\s+([×]?[x]?\s?[a-z\u00DF-\u00F6\u00F8-\u00FF\-\_]+))?'
		self.subforma_pattern = r'(?:\s+(?:(?:notho|n)?(?:subforma|subform|subf\.))\s+([×]?[x]?\s?[a-z\u00DF-\u00F6\u00F8-\u00FF\-\_]+))?'
		
		self.basionym_author_pattern = r'(\([^×]*?[A-Z\u00C0-\u00D6\u00D8-\u00DE][^\(\)]*?\))?'
		# self.authorship_pattern = '({0}\s*([\(]?[A-Z][^×]*?[\)]?(?<! x )))?'.format(self.basionym_author_pattern) overdefinition with look behind (?<! x ) ?
		self.authorship_pattern = r'(?:\s+({0}\s*([\(]?[^×]*?[A-Z\u00C0-\u00D6\u00D8-\u00DE][^×]*?[\)]?)))?'.format(self.basionym_author_pattern)
		self.hybrid_species_pattern = r'(?:(\s+[×x]\s*?(?:.+)?))?$'
		
		
		
		self.taxonpattern = r'([×]?[x]?\s?[A-Z\u00C0-\u00D6\u00D8-\u00DE][A-Z\u00C0-\u00D6\u00D8-\u00DEa-z\u00DF-\u00F6\u00F8-\u00FF\-\.]+)\s*{0}{1}{2}{3}{4}{5}{6}{7}{8}{9}{10}{11}{12}'.format(
											self.subgenus_pattern, 
											self.sectio_pattern,
											self.subsectio_pattern,
											self.series_pattern,
											self.subseries_pattern,
											#self.subgenus_species_pattern,
											self.species_pattern,
											self.subspecies_pattern,
											self.varietas_pattern,
											self.subvarietas_pattern,
											self.forma_pattern,
											self.subforma_pattern,
											self.authorship_pattern,
											self.hybrid_species_pattern,
											)
		
		self.compiled_taxonpattern = re.compile(self.taxonpattern)
		
		ranks_or_accronyms = r'subgenus|subgen.|subg.|sectio|sect.|subsectio|subsect.|series|ser.|subseries|subser.|subspecies|subsp.|ssp.|varietas|variety|var.|subvarietas|subvariety|subvar.|forma|form|f.|subforma|subform|subf.'
		self.is_hybrid_pattern = r'(notho|n)({0})|([×])|(\b[x][A-Z\u00C0-\u00D6\u00D8-\u00DE\s])'.format(ranks_or_accronyms)
		self.compiled_is_hybridpattern = re.compile(self.is_hybrid_pattern)
		self.split_hybridised_taxa_pattern = r'(?:\s+x\s+)|(?:\s*×\s*)'
		self.compiled_split_hybridised_taxa_pattern = re.compile(self.split_hybridised_taxa_pattern)
		
		
		self.author_year_pattern = r'\(?([^\(^\d^\)]*)((,*\s*)(\d{2,4})?)?\)?'
		self.compiled_authors_year_pattern = re.compile(self.author_year_pattern)
		self.strip_author_pattern = r'[\,\s]+$'
		self.compiled_strip_author_pattern = re.compile(self.strip_author_pattern)
		self.parantheses_pattern = r'\s*(\().*?(\))\s*'
		self.compiled_parantheses_pattern = re.compile(self.parantheses_pattern)
		
		self.ranks = [
			'genus_or_higher_taxon',
			'subgenus',
			'sectio',
			'subsectio',
			'series',
			'subseries',
			'species',
			'subspecies',
			'varietas',
			'subvarietas',
			'forma',
			'subforma',
		]
		
		self.metadata = [
			'authorship',
			'basionym_authorship',
			'basionym_author',
			'basionym_pub_year',
			'current_authorship',
			'current_author',
			'current_pub_year',
			'hybrid_taxon_with',
			'is_recombination',
		]


	def matchTaxonName(self, taxonname):
		
		if taxonname is None:
			return None
		m = self.compiled_taxonpattern.match(taxonname)
		
		self.taxondict = {}
		
		self.matches = None
		
		if m is not None:
			self.matches = m.groups()
			
			self.taxondict['genus_or_higher_taxon'] = self.matches[0]
			
			self.taxondict['subgenus'] = self.matches[1]
			#if self.taxondict['subgenus'] is None and self.matches[6] is not None:
			#	self.taxondict['subgenus'] = self.matches[6]
			#	self.taxondict['subgenus'] = self.matches[6]
			
			self.taxondict['sectio'] = self.matches[2]
			self.taxondict['subsectio'] = self.matches[3]
			self.taxondict['series'] = self.matches[4]
			self.taxondict['subseries'] = self.matches[5]
			
			self.taxondict['species'] = self.matches[6]
			
			self.taxondict['subspecies'] = self.matches[8]
			self.taxondict['varietas'] = self.matches[9]
			self.taxondict['subvarietas'] = self.matches[10]
			self.taxondict['forma'] = self.matches[11]
			self.taxondict['subforma'] = self.matches[12]
			self.taxondict['authorship'] = self.matches[13]
			self.taxondict['basionym_authorship'] = self.matches[14]
			self.taxondict['current_authorship'] = self.matches[15]
			self.taxondict['hybrid_taxon_with'] = self.matches[16]
			#self.taxondict['remaining_hybridised_taxa'] = self.matches[17]
			
			if self.taxondict['basionym_authorship'] is not None:
				self.is_recombination = 1
				self.taxondict['is_recombination'] = 1
			else:
				self.is_recombination = 0
				self.taxondict['is_recombination'] = 0
			
			self.infraspecific_epithet = None
			self.taxondict['infraspecific_epithet'] = None
			for rank in ['subforma', 'forma', 'subvarietas', 'varietas', 'subspecies']:
				if self.taxondict[rank] is not None:
					self.taxondict['taxonomic_rank'] = rank
					self.infraspecific_epithet = self.taxondict[rank]
					self.taxondict['infraspecific_epithet'] = self.taxondict[rank]
					break
			
			self.searchHybridPattern(taxonname)
			self.matchAuthorYear()
			
			self.taxondict['hybridised_taxa'] = []
			self.appendHybridisedTaxa()
			
			
			return self.taxondict
			
		return None


	def appendHybridisedTaxa(self):
		
		if self.taxondict['hybrid_taxon_with'] is not None:
			hybridised_taxa_list = self.compiled_split_hybridised_taxa_pattern.split(self.taxondict['hybrid_taxon_with'])
			for taxon in hybridised_taxa_list:
				if taxon is not None and len(taxon) > 0:
					self.taxondict['hybridised_taxa'].append('×'+taxon)
		
		return


	def searchHybridPattern(self, taxonname):
		self.taxon_is_hybrid = 0
		self.taxondict['taxon_is_hybrid'] = 0
		
		s = self.compiled_is_hybridpattern.search(taxonname)
		
		if s is not None:
			self.taxon_is_hybrid = 1
			self.taxondict['taxon_is_hybrid'] = 1
			
		return


	def matchAuthorYear(self):
		self.current_author = None
		self.taxondict['current_author'] = None
		self.current_pub_year = None
		self.taxondict['current_pub_year'] = None
		
		if self.taxondict['current_authorship'] is not None:
			m = self.compiled_authors_year_pattern.match(self.taxondict['current_authorship'])
			if m is not None:
				author = m.groups()[0]
				if m.groups()[0] is not None:
					author = self.compiled_strip_author_pattern.sub('', m.groups()[0])
				
				self.current_author = author
				self.taxondict['current_author'] = author
				self.current_pub_year = m.groups()[3]
				self.taxondict['current_pub_year'] = m.groups()[3]
				
				
		
		self.basionym_author = None
		self.taxondict['basionym_author'] = None
		self.basionym_pub_year = None
		self.taxondict['basionym_pub_year'] = None
		
		if self.taxondict['basionym_authorship'] is not None:
			m = self.compiled_authors_year_pattern.match(self.taxondict['basionym_authorship'])
			if m is not None:
				author = m.groups()[0]
				if m.groups()[0] is not None:
					author = self.compiled_strip_author_pattern.sub('', m.groups()[0])
				
				
				self.basionym_author = author
				self.taxondict['basionym_author'] = author
				self.basionym_pub_year = m.groups()[3]
				self.taxondict['basionym_pub_year'] = m.groups()[3]
		
		# move current_author to basionym_author when basionym_author is empty
		# this is needed because Trigger in DiversityTaxonNames sets author names from the separated parts
		# and always expects basionym_authors
		# but current_pub_year must be kept when current_author is set as basionym_author
		
		if self.taxondict['current_author'] is not None and self.taxondict['basionym_author'] is None:
			self.basionym_author = self.taxondict['current_author']
			self.taxondict['basionym_author'] = self.taxondict['current_author']
			self.basionym_pub_year = self.taxondict['current_pub_year']
			self.taxondict['basionym_pub_year'] = self.taxondict['current_pub_year']
			
			self.current_author = None
			self.taxondict['current_author'] = None
			
			# current_pub_year must be kept when current_author is set as basionym_author
			# because this is used by DiversityTaxonNames then
			#self.current_pub_year = None
			#self.taxondict['current_pub_year'] = None
		
		# if it is a zoological name and the current author is in parantheses
		
		if self.taxondict['current_authorship'] is not None:
			if self.compiled_parantheses_pattern.match(self.taxondict['current_authorship']) is not None:
				self.is_recombination = 1
				self.taxondict['is_recombination'] = 1
		
		return


	def printMatchResult(self):
		print(self.taxonpattern)
		
		if self.matches is not None:
			print(self.matches)
			
			for i in range(len(self.matches)):
				print('{0}: {1}'.format(i, self.matches[i]))
			
			for rank in self.ranks:
				print('{0}: {1}'.format(rank, self.taxondict[rank]))
			
			for key in self.metadata:
				print('{0}: {1}'.format(key, self.taxondict[key]))
		
		if 'taxon_is_hybrid' in self.taxondict and self.taxondict['taxon_is_hybrid'] is not None:
			print('Taxon is hybrid: {0}'.format(str(self.taxondict['taxon_is_hybrid'])))
		
		if 'hybridised_taxa' in self.taxondict:
			for hybridised_taxon in self.taxondict['hybridised_taxa']:
				print('Taxon is hybrid with: {0}'.format(hybridised_taxon))
		
		return


if __name__ == "__main__":
	usage = "NamePatterns.py "
	parser = argparse.ArgumentParser(prog="NamePatterns.py", usage=usage, description='Argument NamePatterns.py')
	parser.add_argument('taxonname')
	args = parser.parse_args()
	
	namepatterns = NamePatternsBotany()
	taxondict = namepatterns.matchTaxonName(args.taxonname)
	if taxondict is None:
		print('taxon name analysis failed for:\n{0}'.format(args.taxonname))
	namepatterns.printMatchResult()
	

