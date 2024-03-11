import os
import re
import pudb


class ConfigSetter():
	def __init__(self, sourcefile, targetfile):
		self.sourcefile = sourcefile
		self.targetfile = targetfile
		self.env_variables = {
		}
	
	
	def set_config(self):
		self.read_env_variables()
		self.set_config_parameters()
	
	
	def read_env_variables(self):
		pattern = re.compile(r'\@\@(.*)\@\@')
		with open(self.sourcefile, 'r') as fh_source:
			lines = fh_source.readlines()
			for line in lines:
				m = pattern.search(line)
				if m is not None and len(m[1]) > 0:
					self.env_variables[m[1]] = None
		
		for variable in self.env_variables:
			self.env_variables[variable] = os.getenv(variable, None)
	
	def set_config_parameters(self):
		with open(self.sourcefile, 'r') as fh_source:
			filecontent = fh_source.read()
			
			for variable in self.env_variables:
				if self.env_variables[variable] is not None:
					replacestring = '@@{0}@@'.format(variable)
					filecontent = filecontent.replace(replacestring, self.env_variables[variable])
		
		with open(self.targetfile, 'w') as fh_target:
			fh_target.write(filecontent)


if __name__ == '__main__':
	import argparse
	parser = argparse.ArgumentParser()
	parser.add_argument("config_template")
	parser.add_argument("config_file")
	args = parser.parse_args()
	configsetter = ConfigSetter(args.config_template, args.config_file)
	configsetter.set_config()
	



