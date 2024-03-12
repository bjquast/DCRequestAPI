from setuptools import setup
import sys

# check for python version and define the right requirements
if sys.version_info < (3, 0):
	raise Exception ('python version must be >= 3.0')
else:
	pass

requires = [
	'configparser',
	'elasticsearch',
	'pyodbc',
	'pymysql',
	'pudb',
	'pyramid',
	'pyramid_chameleon',
	'pyramid_debugtoolbar',
	'pyramid_beaker',
	'waitress',
	'requests',
	'cryptography',
	'bcrypt',
	'redis'
]

setup(name='DCRequestAPI',
	author='Björn Quast',
	author_email='b.quast@leibniz-lib.de',
	license='CC By 4.0',
	install_requires=requires,
	entry_points={
		'paste.app_factory': [
		'main = DCRequestAPI:main'
		],
	},
)
