import re
import pudb
import argparse


class NamePatternsZoology():
	def __init__(self):
		#self.namepattern = re.compile(r'([A-Z][a-z\-\_]+)\s*(\(([^\,]*?)\))*\s*([a-z\-\_]+)*\s*([a-z\-\_]+)*')
		#self.authorpattern = re.compile(r'([\(]?([A-Z\u00C0-\u00D6\u00D8-\u00DEa-z\u00DF-\u00F6\u00F8-\u00FF][^\)\d]*[a-z\u00DF-\u00F6\u00F8-\u00FF])[\,\s]*(\d{2,4})?[\)]?)')
		
		self.author_prefix_pattern = r'(al|f|j|jr|ms|sr|v|v[ao]n|zu[rm]?|bis|d[aeiou]?|de[nrmls]?|degli|e|l[ae]s?|s|ter|t|y)'
		
		self.taxonname_pattern = r'([A-Z][a-z\-\_]+)(?:\s+(\(([^\,]*?)\)))?(?:\s+((?!{0}[\'\s]+)[a-z\-\_]+)*)?(?:\s+((?!{0}[\'\s]+)[a-z\-\_]+)*)?(?:\s*((\()?([A-Z\u00C0-\u00D6\u00D8-\u00DEa-z\u00DF-\u00F6\u00F8-\u00FF].*?)\,\s*(\d{{2,4}})\s*(\))?)?)?.*?'.format(self.author_prefix_pattern)
		self.compiled_pattern = re.compile(self.taxonname_pattern)
		
		self.ranks = [
			'genus_or_higher_taxon',
			'subgenus',
			'species',
			'subspecies',
		]
		
		self.metadata = [
			'basionym_authorship',
			'basionym_author',
			'basionym_pub_year',
			'is_recombination',
		]
		


	def matchTaxonName(self, taxonname):
		if taxonname is None:
			return None
		
		self.taxondict = {}
		
		m = self.compiled_pattern.match(taxonname)
		
		self.matches = None
		
		if m is not None:
			self.matches = m.groups()
			
			self.taxondict['genus_or_higher_taxon'] = self.matches[0]
			self.taxondict['subgenus'] = self.matches[2]
			self.taxondict['species'] = self.matches[3]
			self.taxondict['subspecies'] = self.matches[5]
			self.taxondict['infraspecific_epithet'] = self.matches[5]
			self.taxondict['basionym_authorship'] = self.matches[7]
			self.taxondict['basionym_author'] = self.matches[9]
			self.taxondict['basionym_pub_year'] = self.matches[10]
			
			self.taxondict['current_authorship'] = None
			self.taxondict['current_author'] = None
			self.taxondict['current_pub_year'] = None
			
			if self.matches[8] == '(' and self.matches[11] == ')':
				self.taxondict['is_recombination'] = 1
			else:
				self.taxondict['is_recombination'] = 0
			
			# not true and not false because i do not know how to handle hybrids in zoological code
			self.taxondict['taxon_is_hybrid'] = None
		
			return self.taxondict
		
		return None


	def printMatchResult(self):
		print(self.taxonname_pattern)
		
		if self.matches is not None:
			print(self.matches)
			
			for i in range(len(self.matches)):
				print('{0}: {1}'.format(i, self.matches[i]))
			
			for rank in self.ranks:
				print('{0}: {1}'.format(rank, self.taxondict[rank]))
			
			for key in self.metadata:
				print('{0}: {1}'.format(key, self.taxondict[key]))
		
		return




if __name__ == "__main__":
	usage = "NamePatterns.py "
	parser = argparse.ArgumentParser(prog="NamePatternsZoology.py", usage=usage, description='Argument NamePatternsZoology.py')
	parser.add_argument('taxonname')
	args = parser.parse_args()
	
	namepatterns = NamePatternsZoology()
	taxondict = namepatterns.matchTaxonName(args.taxonname)
	if taxondict is None:
		print('taxon name analysis failed for:\n{0}'.format(args.taxonname))
	namepatterns.printMatchResult()



