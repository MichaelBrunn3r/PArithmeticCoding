from fractions import Fraction
from decimal import Decimal
import decimal
import intervals as Intervals
import math

COLUMN_LOWER = '['
COLUMN_UPPER = ']'
COLUMN_DELTA_INTERVAL = 'd'
COLUMNS = [COLUMN_LOWER, COLUMN_UPPER, COLUMN_DELTA_INTERVAL]
DEFAULT_COLUMN_HEADERS = {
	COLUMN_LOWER: 'Lower',
	COLUMN_UPPER: 'Upper',
	COLUMN_DELTA_INTERVAL: 'Delta I'
}

def char_occurrences(string):
	""" Returns a list of pairs, each consisting out of a char and its number of occurences in the string """
	probs = dict()
	for char in string:
		if not char in probs:
			probs[char] = 1
		else:
			probs[char] = probs[char] + 1	
	return sorted(list(map(lambda c: (c,probs[c]), probs)))

def char_probabilities(string):
	""" Returns a list of pairs, each consisting out of a char and its probability in the string """
	return list(map(lambda x: (x[0], Fraction(x[1],len(string))), char_occurrences(string)))

def get_char_intervals(string):
	char_probs = char_probabilities(string)
	intervals = dict()
	current_interval = [Fraction(0), char_probs[0][1]]

	for i, (char, prob) in enumerate(char_probs): 
		if i > 0:
			current_interval[1] = current_interval[0] + prob
		intervals[char] = {'P': prob, 'Interval': Intervals.closed(current_interval[0], current_interval[1])}
		current_interval[0] = current_interval[1]

	return intervals

def calculate_interval(string, char_intervals=None):
	""" Calculates the interval the string is inside """
	if not char_intervals:
		char_intervals = get_char_intervals(string)
	for last in calculate_intervals(string, char_intervals):
		pass
	return last

def calculate_intervals(string, char_intervals=None):
	""" Returns all the intervals that arise while calculating the interval the string is inside """
	if not char_intervals:
		char_intervals = get_char_intervals(string)

	interval = [Fraction(0),Fraction(1)]
	for char in string:
		interval_length = interval[1] - interval[0]
		lower = interval[0]
		interval[0] = lower + char_intervals[char]['Interval'].lower * interval_length
		interval[1] = lower + char_intervals[char]['Interval'].upper * interval_length
		yield Intervals.closedopen(interval[0], interval[1])

def encode(interval):
	sum = Fraction(0)
	exponent = -1
	code = ""

	while not interval.contains(sum):
		if sum + math.pow(2, exponent) < interval.upper:
			sum += math.pow(2, exponent)
			code += '1'
		else:
			code += '0'
		exponent -= 1

	return code

#############
# CLI Utils #
#############

def fraction_to_decimal(fraction):
	return Decimal(fraction.numerator) / Decimal(fraction.denominator)

def generate_interval_table_rows(string, columns_with_options):
	char_intervals = get_char_intervals(string)
	intervals = calculate_intervals(string, char_intervals)

	for char in string:
		interval = next(intervals)
		row = [char]
		for column,options in columns_with_options:
			if column == COLUMN_LOWER:				
				lower = interval.lower
				if not options or not options.get('frac',False): lower = fraction_to_decimal(lower)
				if options and 'f' in options: lower = "{{{}}}".format(options['f']).format(float(lower))
				row.append(str(lower))
			elif column == COLUMN_UPPER:
				upper = interval.upper
				if not options or not options.get('frac',False): upper = fraction_to_decimal(upper)
				if options and 'f' in options: upper = "{{{}}}".format(options['f']).format(float(upper))
				row.append(str(upper))
			elif column == COLUMN_DELTA_INTERVAL:
				delta = interval.upper - interval.lower
				if not options or not options.get('frac',False): delta = fraction_to_decimal(delta)
				if options and 'f' in options: delta = "{{{}}}".format(options['f']).format(float(delta))
				row.append(str(delta))
		yield row

def create_table(rows, columns_with_options):
	from prettytable import PrettyTable

	# Create Table Headers
	headers = ['Chars']
	for column, options in columns_with_options:
		if options and 'name' in options: headers.append(options['name'])
		else: headers.append(DEFAULT_COLUMN_HEADERS[column])

	# Create Table
	table = PrettyTable(headers)
	for row in rows: table.add_row(row)
	return table

def split_every_nth(string, n=4, delimiter=' '):
	parts = [string[i:i+n] for i in range(0, len(string), n)]
	return delimiter.join(parts)

################
# CLI Commands #
################

def cmd_intervals(argsv):
	parser = argparse.ArgumentParser(description='Outputs table of the intervals arising during arithmetic coding of the input string', usage='%(prog)s {} [-h] [string] [-c] [-p]'.format(CMD_INTERVALS))
	parser.add_argument('string', nargs='?', type=str, default=None, help='String to create intervals from. Omit to use stdin'),
	parser.add_argument('-c', '--columns', type=str, help='Included Columns in that order: [{}].'.format('|'.join(COLUMNS)))
	parser.add_argument('-p', '--pretty-print', action='store_true', help='Pretty prints table')
	args = parser.parse_args(argsv)

	# Defaults
	if not args.columns: args.columns = "{}{{'f':':'}}{}{{'f':':'}}".format(COLUMN_LOWER,COLUMN_UPPER)

	# Parse args.columns
	columns_with_options = []
	for param in re.findall("(.(?:\{[^\{\}]*\})?)", args.columns):
		# Extract column and options 
		column_option_pair = list(re.findall("(.)(\{[^\{\}]*\})?",param)[0])
		if not column_option_pair[0] in COLUMNS:
			 raise Exception("Unknown column: '{}'. Valid columns are: [{}]".format(column_option_pair[0], '|'.join(COLUMNS)))
		if column_option_pair[1]:
			column_option_pair[1] = ast.literal_eval(column_option_pair[1])
		columns_with_options.append(column_option_pair)

	def execute(input):
		rows = generate_interval_table_rows(input, columns_with_options)
		if args.pretty_print:
			table = create_table(rows, columns_with_options)
			print(table)
		else: 
			for row in rows: print(';'.join(row))

	if args.string:
		execute(args.string)
	else:
		line = sys.stdin.readline().rstrip()
		while line != '':
			execute(line)
			line = sys.stdin.readline().rstrip()

def cmd_encode(argsv):
	parser = argparse.ArgumentParser(description='Encodes the input string using Arithmetic Coding', usage='%(prog)s {} [-h] [string] [-g] [-d]'.format(CMD_INTERVALS))
	parser.add_argument('string', nargs='?', type=str, default=None, help='String to encode. Omit to use stdin')
	parser.add_argument('-g', '--groupby', type=int, help='The size to group the output bits by')
	parser.add_argument('-d', '--delimiter', type=str, default=' ', help='The group delimiter')
	args = parser.parse_args(argsv)

	def execute(input):
		interval = calculate_interval(input)
		encoded = encode(interval)
		if args.groupby:
			encoded = split_every_nth(encoded, args.groupby, args.delimiter)
		print(encoded)

	if args.string:
		execute(args.string)
	else:
		line = sys.stdin.readline().rstrip()
		while line != '':
			execute(line)
			line = sys.stdin.readline().rstrip()

########
# Main #
########

CMD_INTERVALS = 'intervals'
CMD_ENCODE = 'encode'
COMMANDS = [CMD_INTERVALS,CMD_ENCODE]

if __name__ == '__main__':
	import argparse, sys, re, ast
	parser = argparse.ArgumentParser(description='Arithmetic coding utility')
	parser.add_argument('command', type=str, choices=COMMANDS, help='Subcommand to run')
	args = parser.parse_args(sys.argv[1:2])

	if args.command == CMD_INTERVALS:
		cmd_intervals(sys.argv[2:])
	elif args.command == CMD_ENCODE:
		cmd_encode(sys.argv[2:])
