import pudb
import argparse
import json
from datetime import date, datetime
from dateutil.relativedelta import relativedelta



class DateRangesGenerator():
	def __init__(self, startdate = None, enddate = None, interval = None, interval_multiplicator = 1):
		self.set_start_end_range(startdate, enddate)
		self.set_interval_multiplicator(interval_multiplicator)
		self.set_interval(interval)
		self.set_key_format(interval)


	def set_start_end_range(self, startdate_string = None, enddate_string = None):
		if startdate_string is None:
			self.startdate = datetime.strptime('1800-01-01', '%Y-%m-%d').date()
		else:
			self.startdate = datetime.strptime(startdate_string, '%Y-%m-%d').date()
		if enddate_string is None:
			self.enddate = date.today()
		else:
			self.enddate = datetime.strptime(enddate_string, '%Y-%m-%d').date()

	def set_interval(self, interval):
		self.interval = interval
		if self.interval is None:
			self.date_delta = relativedelta(years=self.i_multiplicator)
			self.key_delta = relativedelta(years=self.i_multiplicator - 1)
		elif self.interval.lower() in ['year', 'years', 'y']:
			self.date_delta = relativedelta(years=self.i_multiplicator)
			self.key_delta = relativedelta(years=self.i_multiplicator - 1)
		elif self.interval.lower() in['month', 'months', 'm']:
			self.date_delta = relativedelta(months=self.i_multiplicator)
			self.key_delta = relativedelta(month=self.i_multiplicator - 1)
		# days take long and not needed in DCRequestAPI DateAggregations
		#elif self.interval.lower() in ['day', 'days', 'd']:
		#	self.date_delta = relativedelta(days=self.i_multiplicator)
		#	self.key_delta = relativedelta(days=self.i_multiplicator - 1)
		else:
			self.date_delta = relativedelta(years=self.i_multiplicator)
			self.key_delta = relativedelta(years=self.i_multiplicator - 1)
		return

	def set_key_format(self, interval):
		if interval is None:
			self.date_format = '%Y-%m-%d'
		elif interval.lower() in ['year', 'years', 'y']:
			self.date_format = '%Y'
		elif interval.lower() in['month', 'months', 'm']:
			self.date_format = '%Y-%m'
		# days take long and not needed in DCRequestAPI DateAggregations
		#elif interval.lower() in ['day', 'days', 'd']:
		#	self.date_format = '%Y-%m-%d'
		else:
			self.date_format = '%Y-%m-%d'
		return

	def set_interval_multiplicator(self, interval_multiplicator):
		self.i_multiplicator = int(interval_multiplicator)
		if self.i_multiplicator < 1:
			self.i_multiplicator = 1
		return

	def generate_ranges(self):
		self.date_ranges = []

		next_start = self.startdate

		while next_start <= self.enddate:
			next_end = next_start + self.date_delta
			key_date = next_start + (self.key_delta)
			range_dict = {
				"key": key_date.strftime(self.date_format),
				"from": next_start.strftime('%Y-%m-%d'),
				"to": next_end.strftime('%Y-%m-%d')
			}
			self.date_ranges.append(range_dict)
			next_start = next_start + self.date_delta
		return self.date_ranges


if __name__ == "__main__":
	usage = "date_range_generator.py -s startdate -e enddate"
	parser = argparse.ArgumentParser(prog="date_range_generator.py", usage=usage, description='Arguments for date_range_generator')
	parser.add_argument('-s', '--startdate', nargs='?', default=None)
	parser.add_argument('-e', '--enddate', nargs='?', default=None)
	parser.add_argument('-i', '--interval', nargs='?', default=None)
	parser.add_argument('-m', '--interval_multiplicator', nargs='?', default=1)
	args = parser.parse_args()
	
	ranges_gen = DateRangesGenerator(args.startdate, args.enddate, args.interval, args.interval_multiplicator)
	date_ranges = ranges_gen.generate_ranges()


	json_string = json.dumps(date_ranges, indent='\t')
	print(json_string)
	
